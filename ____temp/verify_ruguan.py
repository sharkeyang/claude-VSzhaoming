# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 猜想B: 站上DJA(日ZA>0), 按DTZA分组(=1/=2/>=3), 看后续维持升管概率
# 维持升管 = 3日内不跌破DJA
rB = defaultdict(lambda:[0,0])  # (护型, DTZA组) -> [样本, 3日内仍升管]

# 猜想D: 等2与等5相邻, 等1与等6相邻
# 等2(末位CDEF)次日转等5? 等1次日转等6?
rD = defaultdict(lambda:[0,0])  # (当前等型, 次日等型) -> [样本, 计数]
# 等2/等5 阴柱大小: 用涨幅[5]衡量
rD_amp = defaultdict(lambda:[0,0,0])  # (等型) -> [样本, 阴柱, 阳柱]

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
        cur_hx = row[9][0]
        cur_za = int(row[13])
        cur_deng = row[44]
        nxt_deng = nxt[44]
        nxt_za = int(nxt[13])
        # 猜想B: 升管中按DTZA分组
        if cur_za > 0:
            if cur_za == 1:
                grp = 'DTZA=1'
            elif cur_za == 2:
                grp = 'DTZA=2'
            else:
                grp = 'DTZA>=3'
            # 3日内仍升管
            still = 1
            for j in range(i+1, min(i+4, len(rows))):
                if int(rows[j][13]) < 0:
                    still = 0
                    break
            rB[(cur_hx, grp)][0] += 1
            if still: rB[(cur_hx, grp)][1] += 1
        # 猜想D: 等型转移
        rD[(cur_deng, nxt_deng)][0] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 猜想B: 升管中(日ZA>0) 按DTZA分组 3日内仍升管概率 ===')
print(f"{'护型':<4}{'DTZA组':<10}{'样本':>9}{'3日仍升管':>10}{'P3日仍升':>10}")
for hx in ['a','b','r']:
    for grp in ['DTZA=1','DTZA=2','DTZA>=3']:
        tot, still = rB[(hx,grp)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{grp:<10}{tot:>9}{still:>10}{still/tot*100:>9.2f}%")

print('\n=== 猜想D: 等型转移矩阵 (等2/等5, 等1/等6 相邻性) ===')
# 只看关键转移
for cur in ['等1','等2','等5','等6']:
    row = {k[1]:v[0] for k,v in rD.items() if k[0]==cur}
    tot = sum(row.values())
    if tot == 0: continue
    top = sorted(row.items(), key=lambda x:-x[1])[:5]
    print(f'  {cur} (n={tot}): ' + ', '.join(f'{k}={v/tot*100:.1f}%' for k,v in top))
