# -*- coding: utf-8 -*-
"""检查离顶(顶态L)DTZA验证的准确性：确认顶态L判断+样本量+DTZA分布
"""
import csv, io, os
from collections import Counter

COL_ZA = 13
COL_ZC = 14
COL_DING = 43
COL_GAOFU = 6

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计顶态L样本量 + DTZA分布
n_L = 0
n_L_zc0 = 0
dtza_L = Counter()
# 顶态L + DXZC>0 的次日冲高率(≥3%)，按DTZA
stats_L = {}

for fi, fname in enumerate(files):
    path = os.path.join('昭明算展/谕组日', fname)
    try:
        with io.open(path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader)
            rows = []
            for row in reader:
                if len(row) <= COL_DING:
                    continue
                try:
                    za = float(row[COL_ZA])
                    zc = float(row[COL_ZC])
                except (ValueError, IndexError):
                    continue
                rows.append((za, zc, row[COL_DING], row[COL_GAOFU]))
            for i in range(len(rows) - 1):
                za, zc, ding, _ = rows[i]
                is_L = ding.startswith('L') or ding.startswith('_L')
                if is_L:
                    n_L += 1
                    if zc > 0:
                        n_L_zc0 += 1
                        dtza_L[za] += 1
                        if za not in stats_L:
                            stats_L[za] = [0, 0]
                        stats_L[za][0] += 1
                        try:
                            nh = float(rows[i+1][3])
                        except (ValueError, TypeError):
                            continue
                        if nh >= 3:
                            stats_L[za][1] += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print(f'\n=== 顶态L 样本量 ===')
print(f'顶态L 总样本: {n_L}')
print(f'顶态L + DXZC>0: {n_L_zc0} ({n_L_zc0/n_L*100:.1f}%)')

print(f'\n=== 顶态L + DXZC>0 的 DTZA 分布 ===')
print(f'{"DTZA":<8}{"样本":<12}{"占比":<10}')
total = sum(dtza_L.values())
for za in sorted(dtza_L.keys()):
    if -10 <= za <= 10:
        print(f'{za:<8}{dtza_L[za]:<12}{dtza_L[za]/total*100:<10.2f}')

print(f'\n=== 顶态L + DXZC>0 不同DTZA 次日冲高率(≥3%) ===')
print(f'{"DTZA":<8}{"样本":<12}{"≥3%":<10}{"冲高率":<10}')
for za in sorted(stats_L.keys()):
    if -10 <= za <= 10:
        t, g = stats_L[za]
        if t:
            print(f'{za:<8}{t:<12}{g:<10}{g/t*100:<10.1f}')