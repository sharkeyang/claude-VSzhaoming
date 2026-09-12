# -*- coding: utf-8 -*-
import csv, glob
from collections import Counter, defaultdict

files = glob.glob('谕组日_*.csv')

# 假设1c: 己+等1 的次日护型转移 (验证等1在己阶段, 转甲后不再等1)
ji_e1_next = Counter()   # 己+等1 -> 次日护型
ji_e1_total = 0
# 甲+等1 的来源护型 (前一日)
jia_e1_prev = Counter()
jia_e1_total = 0

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)):
        row = rows[i]
        cur_hx = row[9][0]
        deng = row[44]
        prev_hx = rows[i-1][9][0] if i>0 else None
        nxt_hx = rows[i+1][9][0] if i+1<len(rows) else None
        # 己+等1 -> 次日护型
        if cur_hx == 'r' and deng == '等1':
            ji_e1_total += 1
            ji_e1_next[nxt_hx if nxt_hx else '?'] += 1
        # 甲+等1 -> 前一日护型
        if cur_hx == 'a' and deng == '等1':
            jia_e1_total += 1
            jia_e1_prev[prev_hx if prev_hx else '?'] += 1
    n += 1

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己','?':'边界'}
print('总文件:', n)
print('\n=== 假设1c: 己+等1 的次日护型转移 ===')
print('己+等1样本:', ji_e1_total)
for k,v in ji_e1_next.most_common():
    print(f'  次日{HX.get(k,k)}: {v} ({v/ji_e1_total*100:.2f}%)')

print('\n=== 甲+等1 的前一日护型来源 ===')
print('甲+等1样本:', jia_e1_total)
for k,v in jia_e1_prev.most_common():
    print(f'  前日{HX.get(k,k)}: {v} ({v/jia_e1_total*100:.2f}%)')
