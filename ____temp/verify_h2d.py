# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 假设2d: 甲+等2, 按DTZA(日ZA)分组, 看次日冲高/下破DJA
# 用户说"DXAB>10后等2=回归DJA", 可能实际指DTZA>10
jia_e2_dtza = defaultdict(lambda:[0,0,0])

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        cur_hx = row[9][0]
        deng = row[44]
        if cur_hx == 'a' and deng == '等2':
            try:
                dtza = int(row[13])
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            if dtza <= 3:
                grp = 'DTZA<=3(转甲初期)'
            elif dtza <= 10:
                grp = 'DTZA4-10'
            else:
                grp = 'DTZA>10(回归DJA)'
            jia_e2_dtza[grp][0] += 1
            if next_hr_f > 3: jia_e2_dtza[grp][1] += 1
            if next_za < 0: jia_e2_dtza[grp][2] += 1
    n += 1

print('总文件:', n)
print('\n=== 假设2d: 甲+等2 按DTZA分组 (次日冲高/下破DJA) ===')
print(f"{'分组':<20}{'样本':>9}{'冲高':>8}{'P冲高':>8}{'下破DJA':>9}{'P下破':>8}")
for grp, (tot, hit, brk) in sorted(jia_e2_dtza.items()):
    p1 = hit/tot*100 if tot else 0
    p2 = brk/tot*100 if tot else 0
    print(f"{grp:<20}{tot:>9}{hit:>8}{p1:>7.2f}%{brk:>9}{p2:>7.2f}%")
