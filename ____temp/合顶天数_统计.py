# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
class A:
    def __init__(self): self.n=0; self.s=0.0; self.p3=0
    def add(self, x):
        self.n+=1; self.s+=x
        if x>=3: self.p3+=1
def calc_合顶(sf):
    if not sf or len(sf)==0: return 0
    c=0
    for ch in reversed(sf):
        if ch=='A': c+=1
        else: break
    return c
agg_合顶 = defaultdict(A)
agg_未触顶 = A()
t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','日ZC','层界'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    sf = df['层界'].astype(str).values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        if zc[j]<=0: continue
        合顶 = calc_合顶(sf[j])
        if 合顶>=1: agg_合顶[(合顶,)].add(nhr)
        else: agg_未触顶.add(nhr)
print(f'耗时 {time.time()-t0:.0f}s')
print('今天触顶(合顶>=1)的合顶天数:')
for d in range(1,6):
    v=agg_合顶[(d,)]
    print(f'  合顶{d}: n={v.n:>8,d} P3={v.p3/v.n*100:>5.1f}% 均值={v.s/v.n:.2f}%')
print(f'未触顶(合顶=0): n={agg_未触顶.n:>8,d} P3={agg_未触顶.p3/agg_未触顶.n*100:>5.1f}% 均值={agg_未触顶.s/agg_未触顶.n:.2f}%')
