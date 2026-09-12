# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict
files = glob.glob('谕组日_*.csv')

# 验证等6/等7(DXZA<0)用BSHA[19]分组的样本量和冲高概率
r = defaultdict(lambda:[0,0,0.0])

n=0
for fp in files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        rows = list(r_csv)
    for i in range(len(rows)-1):
        row = rows[i]; nxt = rows[i+1]
        if len(row)<62 or len(nxt)<62: continue
        za = int(row[13])
        hx0 = row[9][0]
        try: bsha = float(row[19]); nxt_hr = float(nxt[26])
        except: continue
        if za < 0 and hx0 in ('b','c'):
            if za == -1: deng = '等6'
            else: deng = '等7'
            if bsha < 3: grp = 'BSHA<3'
            elif bsha < 8: grp = 'BSHA3-8'
            else: grp = 'BSHA>=8'
            key = (deng, grp)
            r[key][0] += 1
            if nxt_hr>=3: r[key][1] += 1
            r[key][2] += nxt_hr
    n += 1

print('总文件:', n)
print('等6/等7(DXZA<0) 用BSHA分组 样本量和冲高概率:')
print(f"{'等型':<6}{'BSHA组':<10}{'n':>9}{'P(>=3%)':>10}{'均高幅':>8}")
for deng in ['等6','等7']:
    for grp in ['BSHA<3','BSHA3-8','BSHA>=8']:
        tot, hit, s = r[(deng,grp)]
        if tot == 0: continue
        print(f"{deng:<6}{grp:<10}{tot:>9}{hit/tot*100:>9.2f}%{s/tot:>7.2f}%")
