# -*- coding: utf-8 -*-
"""
验证 1.4.1.2.1 的"乙+触顶A+BSHA8+十字星(无长上影)=67.8%"数据。
基于 重跑54_正确列_test.py 的列位置索引（VBA写入顺序）：
  高幅=[6], DXAB=[9], 日ZA=[13], 日ZC=[14], BSHA=[19], 宽哼JC=[22],
  次日高幅=[26], 上符串=[30], 日龟BT合顶哼=[56], 开/收/高/低 需确认
"""
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))

# 正确列位置（VBA源码 PX算研_RAP算展1引擎.bas L1802-1864 实测）
# 收=1 开=2 高=3 低=4 高幅=6 DXAB=9 日ZA=13 日ZC=14 BSHA=19 宽哼JC=22 次日高幅=26 上符串=30 日龟BT合顶哼=56
C_高幅=6; C_DXAB=9; C_日ZA=13; C_日ZC=14; C_BSHA=19; C_宽哼JC=22
C_次日高幅=26; C_上符串=30; C_合顶哼=56

class A:
    def __init__(self): self.n=0; self.s=0.0; self.p2=0; self.p3=0; self.p5=0
    def add(self, x):
        self.n+=1; self.s+=x
        if x>=2: self.p2+=1
        if x>=3: self.p3+=1
        if x>=5: self.p5+=1
    def stats(self):
        if self.n==0: return None
        return {'n':self.n,'P2':self.p2/self.n*100,'P3':self.p3/self.n*100,'P5':self.p5/self.n*100,'均值':self.s/self.n}

# 聚合器：按护型拆分的十字星
agg_十字星_护型 = defaultdict(A)   # 触顶+BSHA≥8+十字星(无长上影) 按护型
agg_十字星_全 = defaultdict(A)     # 触顶+BSHA≥8+十字星(无长上影) 全部
agg_十字星_护型_合顶 = defaultdict(A)  # 触顶+BSHA≥8+合顶≥3+十字星 按护型

t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk', header=None, skiprows=1)
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    n=len(df)
    if n<2: continue
    hr = pd.to_numeric(df[C_高幅], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    zc = pd.to_numeric(df[C_日ZC], errors='coerce').values
    bsha = pd.to_numeric(df[C_BSHA], errors='coerce').values
    hd = pd.to_numeric(df[C_合顶哼], errors='coerce').values
    sf = df[C_上符串].astype(str).values
    dxab = df[C_DXAB].astype(str).values
    # 开/收/高/低 固定列位置（实测表头：收=1 开=2 高=3 低=4）
    c_open=2; c_close=1; c_high=3; c_low=4
    opn = pd.to_numeric(df[c_open], errors='coerce').values
    cls = pd.to_numeric(df[c_close], errors='coerce').values
    hig = pd.to_numeric(df[c_high], errors='coerce').values
    low = pd.to_numeric(df[c_low], errors='coerce').values
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        zc_v=zc[j]; bsha_v=bsha[j]; hd_v=hd[j]
        s=sf[j]; ab=dxab[j]
        is_touch = len(s)>0 and s[-1]=='A'
        # 十字星形态（触顶+BSHA≥8 子集）
        if zc_v>0 and is_touch and not np.isnan(bsha_v) and bsha_v>=8:
            o=opn[j]; c=cls[j]; h=hig[j]; l=low[j]
            if np.isnan(o) or np.isnan(c) or np.isnan(h) or np.isnan(l) or h<=l: continue
            body=abs(c-o); rng=h-l
            if rng<=0: continue
            upper=h-max(o,c)
            is_doji = body < 0.1*rng
            is_long_upper = upper > 2*body and upper > 0.4*rng
            if is_doji and not is_long_upper:
                agg_十字星_全[('全部',)].add(nhr)
                # 按护型
                if '乙' in ab: agg_十字星_护型[('乙',)].add(nhr)
                elif '甲' in ab: agg_十字星_护型[('甲',)].add(nhr)
                elif '己' in ab: agg_十字星_护型[('己',)].add(nhr)
                elif '戊' in ab: agg_十字星_护型[('戊',)].add(nhr)
                elif '丙' in ab: agg_十字星_护型[('丙',)].add(nhr)
                elif '丁' in ab: agg_十字星_护型[('丁',)].add(nhr)
                # 合顶≥3
                if not np.isnan(hd_v) and hd_v>=3:
                    agg_十字星_护型_合顶[('全部+合顶≥3',)].add(nhr)
                    if '乙' in ab: agg_十字星_护型_合顶[('乙+合顶≥3',)].add(nhr)

print(f'耗时 {time.time()-t0:.0f}s')
out=[]
out.append('='*70)
out.append('验证 1.4.1.2.1 乙+触顶A+BSHA8+十字星(无长上影)')
out.append('='*70)
def dump(title, agg, keys):
    out.append(f'【{title}】')
    out.append(f'{"条件":<20s}  {"P2":>7s}  {"P3":>7s}  {"P5":>7s}  {"均值":>7s}  {"样本":>10s}')
    out.append('-'*62)
    for k in keys:
        kk=(k,) if isinstance(k,str) else k
        s=agg[kk].stats()
        if s: out.append(f'{str(k):<20s}  {s["P2"]:>6.1f}%  {s["P3"]:>6.1f}%  {s["P5"]:>6.1f}%  {s["均值"]:>6.2f}  {s["n"]:>10,d}')
    out.append('')
dump('触顶+BSHA≥8+十字星(无长上影) 全部', agg_十字星_全, ['全部'])
dump('触顶+BSHA≥8+十字星(无长上影) 按护型', agg_十字星_护型, ['乙','甲','己','戊','丙','丁'])
dump('触顶+BSHA≥8+合顶≥3+十字星 按护型', agg_十字星_护型_合顶, ['全部+合顶≥3','乙+合顶≥3'])
result='\n'.join(out)
print(result)
with open('____temp/验证_乙触顶十字星_结果.txt','w',encoding='utf-8') as f: f.write(result)
print(f'\n结果已保存: ____temp/验证_乙触顶十字星_结果.txt')
