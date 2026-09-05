# -*- coding: utf-8 -*-
"""等1前一柱各护型的 ≥1/≥2/≥3 阈值"""
import csv, os
from collections import defaultdict
HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))
res = defaultdict(lambda: [0,0,0,0])  # 护型 -> [n,>=1,>=2,>=3]
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code=fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    prev_hx=None
    with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<=44: continue
            etc=row[44].strip(); dxab=row[9].strip()
            hx=HX.get(dxab[0]) if dxab else None
            try: nxt=float(row[26])
            except: continue
            if etc=='等1' and prev_hx:
                res[prev_hx][0]+=1
                if nxt>=1: res[prev_hx][1]+=1
                if nxt>=2: res[prev_hx][2]+=1
                if nxt>=3: res[prev_hx][3]+=1
            prev_hx=hx
out=[]
for hx in ['甲','乙','丙','丁','戊','己']:
    if hx in res:
        n,a,b,c=res[hx]
        out.append(f'{hx}: n={n}, ≥1%={a/n*100:.1f}%, ≥2%={b/n*100:.1f}%, ≥3%={c/n*100:.1f}%')
with open('____temp/etc1_prev_all.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
