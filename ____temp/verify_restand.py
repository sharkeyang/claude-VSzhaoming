# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证问题3: 下破DJA后重新站上(日ZA>0), 是否能站稳?
# 重新站上后: 5日/10日仍升管(站稳) vs 又跌破(诱多)
# 按重新站上时的DTZA分组(ZA=1/2/>=3)
r = defaultdict(lambda:[0,0,0,0.0])  # (DTZA组) -> [样本, 5日仍升管, 10日仍升管, 5日收益和]

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
        if hx0 not in ('a','b','r'): continue
        # 找下破DJA后重新站上的点
        # 当前是升管(za>0), 但前一日是跌管(za_prev<0) => 重新站上
        if za > 0 and i > 0:
            za_prev = int(rows[i-1][13])
            if za_prev < 0:
                # 重新站上点
                if za == 1: grp = '重站DTZA=1'
                elif za == 2: grp = '重站DTZA=2'
                else: grp = '重站DTZA>=3'
                # 5日/10日仍升管
                still5 = 0; still10 = 0
                for j in range(i+1, min(i+6, len(rows))):
                    if int(rows[j][13]) > 0:
                        still5 = 1
                        break
                for j in range(i+1, min(i+11, len(rows))):
                    if int(rows[j][13]) > 0:
                        still10 = 1
                        break
                # 5日收益
                ret5 = 0.0
                try:
                    cur = float(row[1])
                    exit5 = float(rows[min(i+5, len(rows)-1)][1])
                    ret5 = (exit5 - cur) / cur * 100
                except: pass
                r[grp][0] += 1
                if still5: r[grp][1] += 1
                if still10: r[grp][2] += 1
                r[grp][3] += ret5
    n += 1

print('总文件:', n)
print('\n=== 下破DJA后重新站上(日ZA>0), 按DTZA分组 能否站稳 ===')
print(f"{'分组':<14}{'样本':>9}{'5日仍升管':>10}{'P5日':>8}{'10日仍升管':>11}{'P10日':>8}{'5日收益':>9}")
for grp in ['重站DTZA=1','重站DTZA=2','重站DTZA>=3']:
    tot, s5, s10, sret = r[grp]
    if tot == 0: continue
    print(f"{grp:<14}{tot:>9}{s5:>10}{s5/tot*100:>7.2f}%{s10:>11}{s10/tot*100:>7.2f}%{sret/tot:>8.3f}%")
