# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))

class A:
    def __init__(self): self.n=0; self.p2=0; self.p3=0; self.s=0.0
    def add(self, x):
        self.n+=1; self.s+=x
        if x>=2: self.p2+=1
        if x>=3: self.p3+=1
    def stats(self):
        if self.n==0: return None
        return {'n':self.n,'P2':self.p2/self.n*100,'P3':self.p3/self.n*100,'均值':self.s/self.n}

# 聚合器
agg_等5_zc0_乙 = A()          # 等5+ZC<0+乙
agg_等5_zc0_乙_bsha5 = A()    # 等5+ZC<0+乙+BSHA5
agg_等5_zc0 = A()             # 等5+ZC<0
agg_等5 = A()                 # 等5（全）
agg_等5_bsha5 = A()           # 等5+BSHA5

t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','日ZA','日ZC','DXAB','BSHA'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    za = pd.to_numeric(df['日ZA'], errors='coerce').values
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    bsha = pd.to_numeric(df['BSHA'], errors='coerce').values
    dxab = df['DXAB'].astype(str).values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        za_v=za[j]; zc_v=zc[j]; bsha_v=bsha[j]; ab=dxab[j]
        # 等5 = DTZA=-1
        is_等5 = (za_v == -1)
        if not is_等5: continue
        agg_等5.add(nhr)
        if zc_v<0:
            agg_等5_zc0.add(nhr)
            if '乙' in ab:
                agg_等5_zc0_乙.add(nhr)
                if not np.isnan(bsha_v) and bsha_v>5:
                    agg_等5_zc0_乙_bsha5.add(nhr)
        if not np.isnan(bsha_v) and bsha_v>5:
            agg_等5_bsha5.add(nhr)

print(f'耗时 {time.time()-t0:.0f}s')
out=[]
out.append('='*60)
out.append('验证 等5+ZC<0+乙+BSHA5 = 77.3%')
out.append('='*60)
def dump(name, agg):
    s=agg.stats()
    if s:
        out.append(f'{name:<30s}  P2={s["P2"]:>6.1f}%  P3={s["P3"]:>6.1f}%  均值={s["均值"]:>5.2f}%  n={s["n"]:>8,d}')
    else:
        out.append(f'{name:<30s}  无样本')
dump('等5（全）', agg_等5)
dump('等5+ZC<0', agg_等5_zc0)
dump('等5+ZC<0+乙', agg_等5_zc0_乙)
dump('等5+ZC<0+乙+BSHA5', agg_等5_zc0_乙_bsha5)
dump('等5+BSHA5', agg_等5_bsha5)
result='\n'.join(out)
print(result)
with open('____temp/验证等5_结果.txt','w',encoding='utf-8') as f: f.write(result)
print(f'\n结果已保存: ____temp/验证等5_结果.txt')
