# -*- coding: utf-8 -*-
"""验证 DXZC>0 离顶(顶态L)时，不同DTZA的次日冲高率
聚焦 DTZA 合理范围(-10~10)
"""
import csv, io, os

COL_ZC = 14     # 日ZC
COL_ZA = 13     # 日ZA (DTZA)
COL_DING = 43   # 顶型
COL_GAOFU = 6   # 高幅

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计：DXZC>0 + 顶态L 时，不同DTZA的次日冲高率
stats_L = {}    # 顶态L
stats_all = {}  # 全部(不分顶态)

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
                    zc = float(row[COL_ZC])
                    za = float(row[COL_ZA])
                except (ValueError, IndexError):
                    continue
                rows.append((zc, za, row[COL_DING], row[COL_GAOFU]))
            for i in range(len(rows) - 1):
                zc, za, ding, _ = rows[i]
                if zc <= 0:
                    continue
                if za < -10 or za > 10:
                    continue
                is_L = ding.startswith('L') or ding.startswith('_L')
                try:
                    next_high = float(rows[i+1][3])
                except (ValueError, TypeError):
                    continue
                if za not in stats_all:
                    stats_all[za] = [0, 0]
                stats_all[za][0] += 1
                if next_high >= 3:
                    stats_all[za][1] += 1
                if is_L:
                    if za not in stats_L:
                        stats_L[za] = [0, 0]
                    stats_L[za][0] += 1
                    if next_high >= 3:
                        stats_L[za][1] += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print('\n=== DXZC>0 + 顶态L(离顶) 不同DTZA 次日冲高率(≥3%) ===')
print(f'{"DTZA":<8}{"总数":<12}{"≥3%":<10}{"冲高率":<10}')
for za in sorted(stats_L.keys()):
    t, g = stats_L[za]
    if t:
        print(f'{za:<8}{t:<12}{g:<10}{g/t*100:<10.1f}')

print('\n=== 对照: DXZC>0 全部(不分顶态) 不同DTZA 次日冲高率(≥3%) ===')
print(f'{"DTZA":<8}{"总数":<12}{"≥3%":<10}{"冲高率":<10}')
for za in sorted(stats_all.keys()):
    t, g = stats_all[za]
    if t:
        print(f'{za:<8}{t:<12}{g:<10}{g/t*100:<10.1f}')