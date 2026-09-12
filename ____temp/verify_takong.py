# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DJA之上跌连后的踏空概率
# DJA之上(日ZA>0, 甲乙己)出现跌连后:
# 1. 后续是否继续上涨(踏空): 5日/10日内创新高(收盘价>跌连日收盘)
# 2. 后续是否下破DJA(正确退出)
# 3. 后续是否重新站上DJA(短暂回调后继续)
r = defaultdict(lambda:[0,0,0,0,0.0])  # (信号) -> [样本, 5日创新高, 10日创新高, 3日下破, 5日收益和]

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
        try:
            cur_close = float(row[1])
        except:
            continue
        # 信号分类
        if zhu.startswith('跌') and '连' in zhu:
            sig = 'DJA之上跌连'
        elif zhu.startswith('跌'):
            sig = 'DJA之上跌排/跌吞'
        elif zhu.startswith('升'):
            sig = 'DJA之上升排'
        else:
            sig = 'DJA之上人排'
        # 5日/10日创新高(收盘>当前收盘)
        hi5 = 0; hi10 = 0
        for j in range(i+1, min(i+6, len(rows))):
            try:
                if float(rows[j][1]) > cur_close:
                    hi5 = 1
                    break
            except: pass
        for j in range(i+1, min(i+11, len(rows))):
            try:
                if float(rows[j][1]) > cur_close:
                    hi10 = 1
                    break
            except: pass
        # 3日下破
        brk = 0
        for j in range(i+1, min(i+4, len(rows))):
            if int(rows[j][13]) < 0:
                brk = 1
                break
        # 5日收益
        ret5 = 0.0
        try:
            exit5 = float(rows[min(i+5, len(rows)-1)][1])
            ret5 = (exit5 - cur_close) / cur_close * 100
        except: pass
        r[sig][0] += 1
        if hi5: r[sig][1] += 1
        if hi10: r[sig][2] += 1
        if brk: r[sig][3] += 1
        r[sig][4] += ret5
    n += 1

print('总文件:', n)
print('\n=== DJA之上各柱排: 踏空概率(后续创新高) vs 下破概率 ===')
print(f"{'信号':<20}{'样本':>9}{'5日创新高':>10}{'P5日新高':>10}{'10日创新高':>11}{'P10日新高':>11}{'3日下破':>9}{'P下破':>8}{'5日收益':>9}")
for k,(tot,hi5,hi10,brk,sret) in sorted(r.items(), key=lambda x:-x[1][0]):
    if tot < 1000: continue
    print(f"{k:<20}{tot:>9}{hi5:>10}{hi5/tot*100:>9.2f}%{hi10:>11}{hi10/tot*100:>10.2f}%{brk:>9}{brk/tot*100:>7.2f}%{sret/tot:>8.3f}%")
