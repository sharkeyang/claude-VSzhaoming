# -*- coding: utf-8 -*-
"""验证周门过滤部分：1.4.3.1+周门、1.4.3.2交叉、1.5.5.5赛马、1.5.5.7 BSHA3/5"""
import csv, os
from collections import defaultdict
HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

def classify(zx):
    if '梯' in zx: return '柱梯'
    if '栅' in zx: return '柱栅'
    if '枝' in zx: return '柱枝'
    if '根' in zx: return '柱根'
    return '柱其他'

# 1.4.3.1 +周门: (柱型) -> [n,h2,h3,sum]
zx_men = defaultdict(lambda: [0,0,0,0.0])
# 1.4.3.2 交叉: (柱型,等型) -> [n,h2,h3,sum]
zx_etc = defaultdict(lambda: [0,0,0,0.0])
# 1.5.5.5 等1赛马: 组合 -> [n,h2,h3]
race_etc1 = defaultdict(lambda: [0,0,0])
# 1.5.5.7 BSHA3/5+周门: (等型,BSHA阈值) -> [n,h2]
bsha_men = defaultdict(lambda: defaultdict(lambda: [0,0]))

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code=fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    prev_hx=None
    with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<=44: continue
            etc=row[44].strip()
            if not etc.startswith('等'): continue
            dxab=row[9].strip()
            hx=HX.get(dxab[0]) if dxab else None
            try: zc=int(float(row[14]))
            except: continue
            cd=row[8].strip()
            # 周门 = ZC>0 且 CD=上
            if not (zc>0 and cd=='上'): continue
            try: nxt=float(row[26])
            except: continue
            h2=1 if nxt>=2 else 0
            h3=1 if nxt>=3 else 0
            zx=row[27].strip()
            g=classify(zx) if zx else '柱其他'
            # 1.4.3.1 +周门
            zx_men[g][0]+=1; zx_men[g][1]+=h2; zx_men[g][2]+=h3; zx_men[g][3]+=nxt
            # 1.4.3.2 交叉
            zx_etc[(g,etc)][0]+=1; zx_etc[(g,etc)][1]+=h2; zx_etc[(g,etc)][2]+=h3; zx_etc[(g,etc)][3]+=nxt
            # 1.5.5.5 等1赛马
            if etc=='等1':
                try: bsha=float(row[19])
                except: bsha=0
                if bsha>5:
                    if prev_hx in ('甲','乙'):
                        race_etc1['等1+前一柱甲乙+BSHA5+周门'][0]+=1; race_etc1['等1+前一柱甲乙+BSHA5+周门'][1]+=h2; race_etc1['等1+前一柱甲乙+BSHA5+周门'][2]+=h3
                    race_etc1['等1+周门+BSHA5'][0]+=1; race_etc1['等1+周门+BSHA5'][1]+=h2; race_etc1['等1+周门+BSHA5'][2]+=h3
            # 1.5.5.7 BSHA3/5+周门
            try: bsha=float(row[19])
            except: bsha=0
            if bsha>5:
                bsha_men[etc][5][0]+=1; bsha_men[etc][5][1]+=h2
            if bsha>3:
                bsha_men[etc][3][0]+=1; bsha_men[etc][3][1]+=h2
            prev_hx=hx

out=[]
out.append('=== 1.4.3.1 +周门 ===')
for g in ['柱梯','柱栅','柱枝','柱根','柱其他']:
    n,h2,h3,s=zx_men[g]
    if n>0:
        out.append(f'{g}_周门: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%, 均冲高={s/n:.2f}%')
out.append('')
out.append('=== 1.4.3.2 交叉 (柱型×等型, 周门) ===')
for (g,etc),v in sorted(zx_etc.items(), key=lambda x:-x[1][1]/x[1][0] if x[1][0] else 0):
    n,h2,h3,s=v
    if n>0:
        out.append(f'{g}+{etc}_周门: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%, 均冲高={s/n:.2f}%')
out.append('')
out.append('=== 1.5.5.5 等1赛马 (周门) ===')
for k,v in race_etc1.items():
    n,h2,h3=v
    if n>0:
        out.append(f'{k}: n={n}, H2={h2/n*100:.1f}%, H3={h3/n*100:.1f}%')
out.append('')
out.append('=== 1.5.5.7 BSHA3/5+周门 ===')
for etc in ['等1','等2','等3']:
    for th in [3,5]:
        if th in bsha_men[etc] and bsha_men[etc][th][0]>0:
            n,h2=bsha_men[etc][th]
            out.append(f'{etc}+BSHA{th}+周门: n={n}, H2={h2/n*100:.1f}%')
with open('____temp/zhoumen_check.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
