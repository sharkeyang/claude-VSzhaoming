# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 跌管退出: 乙ZA<0/丙 + DTZA<=-2, 后续是否继续深跌(3日内日ZA<=-4)
r_exit = defaultdict(lambda:[0,0])

# 冲高回落减仓: 升管内(甲乙己) 跌排, 后续是否下破DJA
r_reduce = defaultdict(lambda:[0,0])

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
        hx0 = row[9][0]
        za = int(row[13])
        zhu = row[10]
        # 跌管退出: 乙ZA<0/丙
        if (hx0 == 'b' and za < 0) or hx0 == 'c':
            # 3日内继续深跌(日ZA<=-4)
            deep = 0
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) <= -4:
                    deep = 1
                    break
            if za <= -2:
                grp = '乙ZA<0/丙+DTZA<=-2'
            elif za == -1:
                grp = '乙ZA<0/丙+DTZA=-1'
            else:
                continue
            r_exit[grp][0] += 1
            if deep: r_exit[grp][1] += 1
        # 冲高回落减仓: 升管内(甲乙己) 跌排, 3日内下破DJA
        if hx0 in ('a','b','r') and za > 0:
            brk = 0
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) < 0:
                    brk = 1
                    break
            if zhu.startswith('跌'):
                grp = '升管内跌排'
            elif zhu.startswith('升'):
                grp = '升管内升排'
            else:
                continue
            r_reduce[grp][0] += 1
            if brk: r_reduce[grp][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 跌管退出: 乙ZA<0/丙, 3日内继续深跌(日ZA<=-4)概率 ===')
print(f"{'分组':<24}{'样本':>9}{'3日深跌':>9}{'P深跌':>8}")
for k,(tot,deep) in sorted(r_exit.items()):
    print(f"{k:<24}{tot:>9}{deep:>9}{deep/tot*100:>7.2f}%")

print('\n=== 冲高回落减仓: 升管内(甲乙己), 3日内下破DJA概率 ===')
print(f"{'分组':<16}{'样本':>9}{'3日下破':>9}{'P下破':>8}")
for k,(tot,brk) in sorted(r_reduce.items()):
    print(f"{k:<16}{tot:>9}{brk:>9}{brk/tot*100:>7.2f}%")
