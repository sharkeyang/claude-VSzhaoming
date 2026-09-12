# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 假设2c: 甲+等2, 区分 由己转甲当天 vs 非转甲, 看次日下破DJA概率
# 同时按中符末位细分
jia_e2 = defaultdict(lambda:[0,0,0])  # 分组 -> [样本, 冲高, 下破DJA]

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
        prev_hx = rows[i-1][9][0] if i>0 else None
        deng = row[44]
        zhong = row[33]
        if cur_hx == 'a' and deng == '等2':
            try:
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            is_zhuan = (prev_hx == 'r')
            mo = zhong[-1] if zhong else '?'
            if is_zhuan:
                grp = '由己转甲+等2'
            else:
                grp = '非转甲+等2'
            jia_e2[grp][0] += 1
            if next_hr_f > 3: jia_e2[grp][1] += 1
            if next_za < 0: jia_e2[grp][2] += 1
            # 细分: 由己转甲+等2+末位CD vs EF
            if is_zhuan and mo in 'CD':
                jia_e2['转甲+等2+末位CD'][0] += 1
                if next_hr_f > 3: jia_e2['转甲+等2+末位CD'][1] += 1
                if next_za < 0: jia_e2['转甲+等2+末位CD'][2] += 1
            if is_zhuan and mo in 'EF':
                jia_e2['转甲+等2+末位EF'][0] += 1
                if next_hr_f > 3: jia_e2['转甲+等2+末位EF'][1] += 1
                if next_za < 0: jia_e2['转甲+等2+末位EF'][2] += 1
    n += 1

print('总文件:', n)
print('\n=== 假设2c: 甲+等2 由己转甲 vs 非转甲 (次日冲高/下破DJA) ===')
print(f"{'分组':<18}{'样本':>9}{'冲高':>8}{'P冲高':>8}{'下破DJA':>9}{'P下破':>8}")
for grp, (tot, hit, brk) in sorted(jia_e2.items()):
    p1 = hit/tot*100 if tot else 0
    p2 = brk/tot*100 if tot else 0
    print(f"{grp:<18}{tot:>9}{hit:>8}{p1:>7.2f}%{brk:>9}{p2:>7.2f}%")
