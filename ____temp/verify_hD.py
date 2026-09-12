# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 猜想D: 等2 vs 等5 阴柱大小(涨幅[5]), 等1 vs 等6 阳柱大小
# 涨幅[5] = 位os结幅PR0
rD = defaultdict(lambda:[0,0,0])  # (等型, 阴阳) -> [样本, 涨幅和, 涨幅平方和]
# 猜想B修正: 升管中按DTZA分组, 进入深跌管(日ZA<=-2)概率
rB = defaultdict(lambda:[0,0])  # (护型, DTZA组) -> [样本, 进入深跌管]

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
        cur_deng = row[44]
        cur_za = int(row[13])
        cur_hx = row[9][0]
        try:
            amp = float(row[5])  # 涨幅
            nxt_za = int(nxt[13])
        except:
            continue
        # 猜想D: 等2/等5 阴柱, 等1/等6 阳柱
        if cur_deng in ('等2','等5'):
            if amp < 0:  # 阴柱
                rD[(cur_deng,'阴')][0] += 1
                rD[(cur_deng,'阴')][1] += amp
                rD[(cur_deng,'阴')][2] += amp*amp
        if cur_deng in ('等1','等6'):
            if amp > 0:  # 阳柱
                rD[(cur_deng,'阳')][0] += 1
                rD[(cur_deng,'阳')][1] += amp
                rD[(cur_deng,'阳')][2] += amp*amp
        # 猜想B修正: 升管中按DTZA分组, 5日内进入深跌管
        if cur_za > 0 and cur_hx in ('a','b','r'):
            if cur_za == 1: grp='DTZA=1'
            elif cur_za == 2: grp='DTZA=2'
            else: grp='DTZA>=3'
            deep = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) <= -2:
                    deep = 1
                    break
            rB[(cur_hx, grp)][0] += 1
            if deep: rB[(cur_hx, grp)][1] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 猜想D: 等2/等5 阴柱大小, 等1/等6 阳柱大小 ===')
print(f"{'等型':<6}{'阴阳':<4}{'样本':>9}{'均涨幅':>10}")
for deng in ['等1','等2','等5','等6']:
    for yin in ['阳','阴']:
        tot, s, s2 = rD[(deng,yin)]
        if tot == 0: continue
        mean = s/tot
        print(f"{deng:<6}{yin:<4}{tot:>9}{mean:>9.3f}%")

print('\n=== 猜想B修正: 升管中按DTZA分组 5日内进入深跌管(日ZA<=-2)概率 ===')
print(f"{'护型':<4}{'DTZA组':<10}{'样本':>9}{'深跌':>8}{'P深跌':>8}")
for hx in ['a','b','r']:
    for grp in ['DTZA=1','DTZA=2','DTZA>=3']:
        tot, deep = rB[(hx,grp)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{grp:<10}{tot:>9}{deep:>8}{deep/tot*100:>7.2f}%")
