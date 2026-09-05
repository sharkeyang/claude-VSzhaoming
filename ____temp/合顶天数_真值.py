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
agg_合顶 = defaultdict(A)  # 用日龟BT合顶哼(正值=合顶天数)
agg_未触顶 = A()  # 合顶哼<=0 (未触顶或合底)
t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','日ZC','日龟BT合顶哼'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    合顶哼 = pd.to_numeric(df['日龟BT合顶哼'], errors='coerce').values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        if zc[j]<=0: continue
        hd = 合顶哼[j]
        if np.isnan(hd): continue
        if hd>0:
            # 合顶天数，分桶：1-5, 6-10, 11-15, 16-20, 21+
            if hd<=5: agg_合顶[(hd,)].add(nhr)
            elif hd<=10: agg_合顶[('6-10',)].add(nhr)
            elif hd<=15: agg_合顶[('11-15',)].add(nhr)
            elif hd<=20: agg_合顶[('16-20',)].add(nhr)
            else: agg_合顶[('21+',)].add(nhr)
        else:
            agg_未触顶.add(nhr)
print(f'耗时 {time.time()-t0:.0f}s')
print('合顶天数(用日龟BT合顶哼, ZC>0):')
for k in [1,2,3,4,5,'6-10','11-15','16-20','21+']:
    v=agg_合顶[(k,)]
    print(f'  合顶{k}: n={v.n:>8,d} P3={v.p3/v.n*100:>5.1f}% 均值={v.s/v.n:.2f}%')
print(f'未触顶/合底(<=0): n={agg_未触顶.n:>8,d} P3={agg_未触顶.p3/agg_未触顶.n*100:>5.1f}% 均值={agg_未触顶.s/agg_未触顶.n:.2f}%')
