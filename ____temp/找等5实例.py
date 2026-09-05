# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))

# 找 ZC>0 + 甲乙己 + BSHA5 + 等5(DTZA=-1) 的实例
found = []
t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['日期','收','开','高','低','涨幅','高幅','日ZA','日ZC','DXAB','BSHA'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    za = pd.to_numeric(df['日ZA'], errors='coerce').values
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    bsha = pd.to_numeric(df['BSHA'], errors='coerce').values
    dxab = df['DXAB'].astype(str).values
    dates = df['日期'].astype(str).values
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    n=len(df)
    for j in range(n-1):
        za_v=za[j]; zc_v=zc[j]; bsha_v=bsha[j]; ab=dxab[j]
        # 等5 = DTZA=-1
        if za_v != -1: continue
        if zc_v <= 0: continue
        if not any(h in ab for h in ['甲','乙','己']): continue
        if np.isnan(bsha_v) or bsha_v <= 5: continue
        # 命中条件
        found.append({
            'cid': cidl, 'date': dates[j], 'ab': ab, 'za': za_v, 'zc': zc_v,
            'bsha': bsha_v, 'next_hr': next_hr[j] if not np.isnan(next_hr[j]) else None
        })
        if len(found) >= 15: break
    if len(found) >= 15: break

print(f'耗时 {time.time()-t0:.0f}s')
print(f'找到 {len(found)} 个实例:')
print('='*80)
for r in found:
    print(f'股票={r["cid"]} 日期={r["date"]} 护型={r["ab"]} DTZA={r["za"]} ZC={r["zc"]} BSHA={r["bsha"]:.1f} 次日高幅={r["next_hr"]}')
