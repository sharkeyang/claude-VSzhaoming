# -*- coding: utf-8 -*-
"""验证 1.5.5.2 等1前一柱护型 和 1.5.5.3 等2/等5/等6前一柱护型"""
import csv, os
from collections import defaultdict

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 等1前一柱护型: 当前等1, 前一柱护型 -> [n,h2,h3]
etc1_prev = defaultdict(lambda: [0,0,0])
# 等2/等5/等6前一柱护型分组: (等型, 前一柱AB/丙丁戊) -> [n,h2]
etc256_prev = defaultdict(lambda: defaultdict(lambda: [0,0]))

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code=fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    prev_hx = None
    with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<=44: continue
            etc=row[44].strip()
            dxab=row[9].strip()
            hx = HX.get(dxab[0]) if dxab else None
            try: nxt=float(row[26])
            except: continue
            h2=1 if nxt>=2 else 0
            h3=1 if nxt>=3 else 0
            if etc=='等1' and prev_hx:
                etc1_prev[prev_hx][0]+=1; etc1_prev[prev_hx][1]+=h2; etc1_prev[prev_hx][2]+=h3
            if etc in ('等2','等5','等6') and prev_hx:
                if prev_hx in ('甲','乙','己'):
                    g='AB'
                else:
                    g='CDE'
                etc256_prev[etc][g][0]+=1; etc256_prev[etc][g][1]+=h2
            prev_hx = hx

out=[]
out.append('=== 等1 前一柱护型 ===')
for hx in ['甲','乙','丙','丁','戊','己']:
    if hx in etc1_prev:
        n,h2,h3=etc1_prev[hx]
        out.append(f'{hx}: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%')
out.append('')
out.append('=== 等2/等5/等6 前一柱护型分组 ===')
for etc in ['等2','等5','等6']:
    for g in ['AB','CDE']:
        if g in etc256_prev[etc]:
            n,h2=etc256_prev[etc][g]
            out.append(f'{etc}+前一柱{g}: n={n}, H2={h2/n*100:.1f}%')
with open('____temp/prev_hx_check.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
