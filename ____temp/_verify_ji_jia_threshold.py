# -*- coding: utf-8 -*-
"""验证己/甲(DXZC>0)在多个次日高幅阈值下的概率：≥0%/≥1%/≥2%/≥3%
"""
import csv, io, os

COL_HX = 9      # DXAB 护型 (第2字符)
COL_ZC = 14     # 日ZC
COL_GAOFU = 6   # 高幅 (当日最高相对前收盘)

files = [f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]

# 统计：护型(DXZC>0) 的次日高幅分布
# stats[hx] = [总数, ≥0, ≥1, ≥2, ≥3]
stats = {}
for hx in ['甲', '乙', '己', '丙', '丁', '戊']:
    stats[hx] = [0, 0, 0, 0, 0]

for fi, fname in enumerate(files):
    path = os.path.join('昭明算展/谕组日', fname)
    try:
        with io.open(path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader)
            rows = []
            for row in reader:
                if len(row) <= COL_GAOFU:
                    continue
                hx = row[COL_HX][1] if len(row[COL_HX]) > 1 else ''
                try:
                    zc = float(row[COL_ZC])
                except (ValueError, IndexError):
                    continue
                rows.append((hx, zc, row[COL_GAOFU]))
            for i in range(len(rows) - 1):
                hx, zc, _ = rows[i]
                if hx not in stats:
                    continue
                if zc <= 0:
                    continue
                try:
                    next_high = float(rows[i+1][2])
                except (ValueError, TypeError):
                    continue
                stats[hx][0] += 1
                if next_high >= 0: stats[hx][1] += 1
                if next_high >= 1: stats[hx][2] += 1
                if next_high >= 2: stats[hx][3] += 1
                if next_high >= 3: stats[hx][4] += 1
    except Exception:
        pass
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件')

print('\n=== 各护型 DXZC>0 次日高幅阈值概率 ===')
print(f'{"护型":<6}{"总数":<12}{"≥0%":<10}{"≥1%":<10}{"≥2%":<10}{"≥3%":<10}')
for hx in ['甲', '乙', '己', '丙', '丁', '戊']:
    t, g0, g1, g2, g3 = stats[hx]
    if t:
        print(f'{hx:<6}{t:<12}{g0/t*100:<10.1f}{g1/t*100:<10.1f}{g2/t*100:<10.1f}{g3/t*100:<10.1f}')
    else:
        print(f'{hx:<6} 无样本')