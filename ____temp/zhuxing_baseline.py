# -*- coding: utf-8 -*-
"""验证柱型baseline：按梯/栅/枝/根/其他分组"""
import csv, os
from collections import defaultdict

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 柱型分组: 梯/栅/枝/根/其他
zx_group = defaultdict(lambda: [0,0,0,0.0,0])  # 组 -> [n,h2,h3,sum,dn]

def classify(zx):
    if '梯' in zx: return '柱梯'
    if '栅' in zx: return '柱栅'
    if '枝' in zx: return '柱枝'
    if '根' in zx: return '柱根'
    return '柱其他'

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code=fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<=27: continue
            zx=row[27].strip()
            if not zx: continue
            try: nxt=float(row[26])
            except: continue
            g=classify(zx)
            zx_group[g][0]+=1
            if nxt>=2: zx_group[g][1]+=1
            if nxt>=3: zx_group[g][2]+=1
            zx_group[g][3]+=nxt
            if nxt>0: zx_group[g][4]+=1

out=[]
total_n=0
for g in ['柱梯','柱栅','柱枝','柱根','柱其他']:
    n,h2,h3,s,dn=zx_group[g]
    total_n+=n
    out.append(f'{g}: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%, 均冲高={s/n:.2f}%, 下柱>0={dn/n*100:.1f}%')
out.append(f'总计: n={total_n}')
with open('____temp/zhuxing_baseline.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
