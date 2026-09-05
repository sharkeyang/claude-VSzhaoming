# -*- coding: utf-8 -*-
"""检查 等1 前一柱乙 的各种阈值，找出 63.3% 对应什么"""
import csv, os
from collections import defaultdict

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 等1前一柱乙: 统计各种阈值
th = defaultdict(int)  # 阈值 -> 计数
n = 0
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
            if etc=='等1' and prev_hx=='乙':
                n+=1
                for t in [0,1,2,3,4,5,6,7,8,9,10]:
                    if nxt>=t: th[t]+=1
            prev_hx = hx

out=[]
out.append(f'等1前一柱乙: n={n}')
for t in [0,1,2,3,4,5,6,7,8,9,10]:
    out.append(f'≥{t}%: {th[t]/n*100:.1f}%')
with open('____temp/etc1_prev_yi_th.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
