# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DJA之上(哼JA管)稳定运行: 操作区域内甲乙己(DXZA>0)
# 警惕信号: DJA之上跌连/回归DJA/冲高导致管宽过大
# 指标: 3日下破DJA概率
r = defaultdict(lambda:[0,0])  # (信号) -> [样本, 3日下破]

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
        if hx0 not in ('a','b','r') or za <= 0: continue
        # 3日下破
        brk = 0
        for j in range(i+1, min(i+4, len(rows))):
            if int(rows[j][13]) < 0:
                brk = 1
                break
        # 信号分类
        if zhu.startswith('跌') and '连' in zhu:
            sig = 'DJA之上跌连'
        elif zhu.startswith('跌'):
            sig = 'DJA之上跌排/跌吞'
        elif zhu.startswith('升'):
            sig = 'DJA之上升排'
        else:
            sig = 'DJA之上人排'
        r[sig][0] += 1
        if brk: r[sig][1] += 1
    n += 1

print('总文件:', n)
print('\n=== DJA之上(哼JA管) 各柱排 3日下破DJA概率 ===')
print(f"{'信号':<20}{'样本':>9}{'3日下破':>9}{'P下破':>8}")
for k,(tot,brk) in sorted(r.items(), key=lambda x:-x[1][0]):
    if tot < 1000: continue
    print(f"{k:<20}{tot:>9}{brk:>9}{brk/tot*100:>7.2f}%")
