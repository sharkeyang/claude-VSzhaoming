# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DJA之下(JA哈管)稳定下跌通道
# 1. DJA之下三柱跌排 -> 很可能形成下跌管(后续继续深跌)
# 2. DJA之下升排/上破DJA -> 是否诱多(后续又跌回)
r = defaultdict(lambda:[0,0])  # (信号) -> [样本, 3日深跌/下破]

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
        if hx0 not in ('a','b','r','c','y','z') or za >= 0: continue
        # 3日继续深跌(日ZA<=-4)
        deep = 0
        for j in range(i+1, min(i+4, len(rows))):
            if int(rows[j][13]) <= -4:
                deep = 1
                break
        # 信号分类
        if zhu.startswith('跌') and '连' in zhu:
            sig = 'DJA之下跌连'
        elif zhu.startswith('跌'):
            sig = 'DJA之下跌排/跌吞'
        elif zhu.startswith('升'):
            sig = 'DJA之下升排'
        else:
            sig = 'DJA之下人排'
        r[sig][0] += 1
        if deep: r[sig][1] += 1
    n += 1

print('总文件:', n)
print('\n=== DJA之下(JA哈管) 各柱排 3日继续深跌(日ZA<=-4)概率 ===')
print(f"{'信号':<20}{'样本':>9}{'3日深跌':>9}{'P深跌':>8}")
for k,(tot,deep) in sorted(r.items(), key=lambda x:-x[1][0]):
    if tot < 1000: continue
    print(f"{k:<20}{tot:>9}{deep:>9}{deep/tot*100:>7.2f}%")
