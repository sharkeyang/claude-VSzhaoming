# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 跌管入管判定: 镜面映射升管
# 升管入管: DTZA>=3(站上DJA三柱), 5日深跌率最高
# 跌管入管: DTZA<=-3(跌破DJA三柱), 5日深跌率(继续深跌)最高?
# 验证: 跌管中(日ZA<0)按DTZA分组, 5日内继续深跌(日ZA<=-4)概率
r = defaultdict(lambda:[0,0])  # (护型, DTZA组) -> [样本, 5日深跌]

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
        cur_za = int(row[13])
        cur_hx = row[9][0]
        if cur_za < 0 and cur_hx in ('a','b','r','c','y','z'):
            if cur_za == -1: grp='DTZA=-1'
            elif cur_za == -2: grp='DTZA=-2'
            else: grp='DTZA<=-3'
            deep = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) <= -4:
                    deep = 1
                    break
            r[(cur_hx, grp)][0] += 1
            if deep: r[(cur_hx, grp)][1] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己','c':'丙','y':'戊','z':'丁'}
print('总文件:', n)
print('\n=== 跌管入管判定: 跌管中(日ZA<0)按DTZA分组 5日内继续深跌(日ZA<=-4)概率 ===')
print(f"{'护型':<4}{'DTZA组':<10}{'样本':>9}{'5日深跌':>9}{'P深跌':>8}")
for hx in ['a','b','r','c','y','z']:
    for grp in ['DTZA=-1','DTZA=-2','DTZA<=-3']:
        tot, deep = r[(hx,grp)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{grp:<10}{tot:>9}{deep:>9}{deep/tot*100:>7.2f}%")
