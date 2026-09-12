# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证跌管退出: 乙ZA<0/丙 + DTZA<=-2
# 乙ZA<0 = 护型b + 日ZA<0; 丙 = 护型c
# 对比: DTZA<=-2 vs DTZA=-1
r_exit = defaultdict(lambda:[0,0])

# 验证冲高回落减仓: 升管内(甲乙己) 跌排
# 冲高回落 = 前一日冲高(高幅大)后回落? 简化: 升管内跌排
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
        nxt = rows[i+1]
        hx0 = row[9][0]
        za = int(row[13])
        zhu = row[10]
        try:
            nxt_hr = float(nxt[26])
        except:
            continue
        p3 = 1 if nxt_hr >= 3 else 0
        # 跌管退出: 乙ZA<0/丙
        if (hx0 == 'b' and za < 0) or hx0 == 'c':
            if za <= -2:
                grp = '乙ZA<0/丙+DTZA<=-2'
            elif za == -1:
                grp = '乙ZA<0/丙+DTZA=-1'
            else:
                continue
            r_exit[grp][0] += 1
            if p3: r_exit[grp][1] += 1
        # 冲高回落减仓: 升管内(甲乙己) 跌排
        if hx0 in ('a','b','r') and za > 0:
            if zhu.startswith('跌'):
                grp = '升管内跌排'
            elif zhu.startswith('升'):
                grp = '升管内升排'
            else:
                continue
            r_reduce[grp][0] += 1
            if p3: r_reduce[grp][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 跌管退出: 乙ZA<0/丙 + DTZA<=-2 ===')
print(f"{'分组':<24}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in sorted(r_exit.items()):
    print(f"{k:<24}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")

print('\n=== 冲高回落减仓: 升管内(甲乙己) 跌排 vs 升排 ===')
print(f"{'分组':<16}{'样本':>9}{'P>=3%':>8}{'P':>8}")
for k,(tot,hit) in sorted(r_reduce.items()):
    print(f"{k:<16}{tot:>9}{hit:>8}{hit/tot*100:>7.2f}%")
