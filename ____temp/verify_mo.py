# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 甲+等2 按中符末位A-F完整分布
jia_e2_mo = defaultdict(lambda:[0,0,0])  # 末位 -> [样本, 下破, 冲高]

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
            zhong = row[33]
            mo = zhong[-1] if zhong else '?'
            try:
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            jia_e2_mo[mo][0] += 1
            if next_za < 0: jia_e2_mo[mo][1] += 1
            if next_hr_f > 3: jia_e2_mo[mo][2] += 1
    n += 1

MO = {'A':'上全','B':'上探','C':'鼎正','D':'反鼎','E':'下探','F':'下全'}
print('总文件:', n)
print('\n=== 甲+等2 按中符末位A-F完整分布 ===')
print(f"{'末位':<8}{'含义':<6}{'样本':>9}{'下破':>8}{'P下破':>8}{'冲高':>8}{'P冲高':>8}")
for mo in 'ABCDEF':
    tot, brk, hit = jia_e2_mo[mo]
    if tot == 0: continue
    print(f"{mo:<8}{MO.get(mo,''):<6}{tot:>9}{brk:>8}{brk/tot*100:>7.2f}%{hit:>8}{hit/tot*100:>7.2f}%")
