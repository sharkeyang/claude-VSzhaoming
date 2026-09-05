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
agg_柱排 = defaultdict(A); agg_波型 = defaultdict(A); agg_盈 = defaultdict(A)
agg_顶型 = defaultdict(A); agg_等型 = defaultdict(A)
agg_总 = A()
t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','DXAB','日ZA','柱排','波型','盈提示','顶型','日等型'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    dxab = df['DXAB'].astype(str).values
    za = pd.to_numeric(df['日ZA'], errors='coerce').values
    zhupai = df['柱排'].astype(str).values
    boying = df['波型'].astype(str).values
    ying = df['盈提示'].astype(str).values
    dingxing = df['顶型'].astype(str).values
    ri等型 = df['日等型'].astype(str).values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        # 乙(DXZA>0) -> 非乙(DXZA>0)：今日乙且ZA>0，次日非乙(ZA>0)
        is_乙正 = '乙' in dxab[j] and za[j]>0
        is_乙正次 = '乙' in dxab[j+1] and za[j+1]>0
        if is_乙正 and not is_乙正次:
            agg_总.add(nhr)
            agg_柱排[(zhupai[j],)].add(nhr)
            agg_波型[(boying[j],)].add(nhr)
            agg_盈[(ying[j],)].add(nhr)
            agg_顶型[(dingxing[j],)].add(nhr)
            agg_等型[(ri等型[j],)].add(nhr)
print(f'耗时 {time.time()-t0:.0f}s')
print(f'乙(DXZA>0)->非乙 总样本: {agg_总.n}, P3={agg_总.p3/agg_总.n*100:.2f}%')
def dump(title, agg, top=12):
    print(f'\n【{title}】')
    items = sorted(agg.items(), key=lambda x:-x[1].n)[:top]
    for k,v in items:
        print(f'  {str(k):<20s} n={v.n:>8,d} P3={v.p3/v.n*100:>5.1f}%')
dump('柱排', agg_柱排)
dump('波型', agg_波型)
dump('盈提示', agg_盈)
dump('顶型', agg_顶型)
dump('日等型', agg_等型)
