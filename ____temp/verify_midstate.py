# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证: 下破DJA后, 按DTZA分组(-1/-2/<=-3), 后续走势(重新站上 vs 继续深跌)
# 呼应§2.9.4.2跌管入管判定(DTZA<=-3确认进入跌管)
# 中间态 = 未确认进入跌管(DTZA>-3), 在选择方向
r = defaultdict(lambda:[0,0,0,0.0])  # (DTZA组) -> [样本, 5日重新站上, 5日继续深跌(ZA<=-4), 5日收益和]

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
        hx0 = row[9][0]; za = int(row[13])
        if hx0 not in ('a','b','r','c','y','z'): continue
        if za < 0:  # 跌管中
            if za == -1: grp = 'DTZA=-1(刚下破)'
            elif za == -2: grp = 'DTZA=-2'
            else: grp = 'DTZA<=-3(已入跌管)'
            # 5日重新站上
            rest = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    rest = 1
                    break
            # 5日继续深跌
            deep = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) <= -4:
                    deep = 1
                    break
            ret5 = 0.0
            try:
                cur = float(row[1])
                exit5 = float(rows[min(i+5, len(rows)-1)][1])
                ret5 = (exit5 - cur) / cur * 100
            except: pass
            r[grp][0] += 1
            if rest: r[grp][1] += 1
            if deep: r[grp][2] += 1
            r[grp][3] += ret5
    n += 1

print('总文件:', n)
print('\n=== 下破DJA后 按DTZA分组 后续走势(中间态选择方向) ===')
print(f"{'DTZA组':<20}{'样本':>9}{'5日重新站上':>12}{'P重站':>8}{'5日继续深跌':>12}{'P深跌':>8}{'5日收益':>9}")
for grp in ['DTZA=-1(刚下破)','DTZA=-2','DTZA<=-3(已入跌管)']:
    tot, rest, deep, sret = r[grp]
    if tot == 0: continue
    print(f"{grp:<20}{tot:>9}{rest:>12}{rest/tot*100:>7.2f}%{deep:>12}{deep/tot*100:>7.2f}%{sret/tot:>8.3f}%")
