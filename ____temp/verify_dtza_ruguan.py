# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证DTZA=1/2/3的入管价值
# 基线内(DXCD=上忐+DXZC>0+甲乙己), 按DTZA分组
# 看P>=3% 和 3日下破DJA
r = defaultdict(lambda:[0,0,0])  # (DTZA组) -> [样本, P>=3%, 3日下破]

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
        nxt = rows[i+1]
        dxcd = row[8]
        dxzc = int(row[14])
        hx0 = row[9][0]
        za = int(row[13])
        if dxcd in ('上','忐') and dxzc > 0 and hx0 in ('a','b','r'):
            if za == 1: grp='DTZA=1'
            elif za == 2: grp='DTZA=2'
            elif za >= 3: grp='DTZA>=3'
            else: continue
            try:
                nxt_hr = float(nxt[26])
            except:
                continue
            p3 = 1 if nxt_hr >= 3 else 0
            brk = 0
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) < 0:
                    brk = 1
                    break
            r[grp][0] += 1
            if p3: r[grp][1] += 1
            if brk: r[grp][2] += 1
    n += 1

print('总文件:', n)
print('\n=== 基线内按DTZA分组: P>=3% 和 3日下破DJA ===')
print(f"{'DTZA组':<10}{'样本':>9}{'P>=3%':>8}{'P':>8}{'3日下破':>9}{'P下破':>8}")
for grp in ['DTZA=1','DTZA=2','DTZA>=3']:
    tot, hit, brk = r[grp]
    print(f"{grp:<10}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%{brk:>9}{brk/tot*100:>7.2f}%")
