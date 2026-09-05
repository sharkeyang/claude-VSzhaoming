# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))

# 真实列位置（VBA写入顺序，不看表头）
# 表头[19]日机警 = 真实BSHA
# 表头[22]BSAC = 真实宽哼JC
# 表头[30]层界 = 真实上符串
# 表头[26]上身 = 真实次日高幅
# 表头[56]日龟BT合顶哼 = 真实合顶天数
# 表头[9]DXAB = 真实护型
# 表头[14]日ZC = 真实ZC
# 表头[13]日ZA = 真实ZA
# 表头[1]收, [2]开, [3]高, [4]低 = 真实K线

class A:
    def __init__(self): self.n=0; self.s=0.0; self.p3=0; self.p5=0
    def add(self, x):
        self.n+=1; self.s+=x
        if x>=3: self.p3+=1
        if x>=5: self.p5+=1
    def stats(self):
        if self.n==0: return None
        return {'n':self.n,'P3':self.p3/self.n*100,'P5':self.p5/self.n*100,'均值':self.s/self.n}

def calc_合顶(sf):
    if not sf or len(sf)==0: return 0
    c=0
    for ch in reversed(sf):
        if ch=='A': c+=1
        else: break
    return c

# 聚合器
agg_bsha = defaultdict(A)          # BSHA分级（真实BSHA）
agg_最强 = defaultdict(A)          # 最强信号
agg_十字星 = defaultdict(A)        # 十字星形态（触顶+BSHA>=8）
agg_十字星_bsha = defaultdict(A)   # 十字星×BSHA
agg_bsha5 = defaultdict(A)         # BSHA5 各位置

t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','日ZA','日ZC','日机警','BSAC','层界','DXAB','日龟BT合顶哼','开','收','高','低'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    za = pd.to_numeric(df['日ZA'], errors='coerce').values
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    bsha = pd.to_numeric(df['日机警'], errors='coerce').values   # 真实BSHA
    kh = pd.to_numeric(df['BSAC'], errors='coerce').values       # 真实宽哼JC
    hd = pd.to_numeric(df['日龟BT合顶哼'], errors='coerce').values
    sf = df['层界'].astype(str).values                            # 真实上符串
    dxab = df['DXAB'].astype(str).values
    opn = pd.to_numeric(df['开'], errors='coerce').values
    cls = pd.to_numeric(df['收'], errors='coerce').values
    hig = pd.to_numeric(df['高'], errors='coerce').values
    low = pd.to_numeric(df['低'], errors='coerce').values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        zc_v=zc[j]; za_v=za[j]; bsha_v=bsha[j]; kh_v=kh[j]; hd_v=hd[j]
        s=sf[j]; ab=dxab[j]
        is_touch = len(s)>0 and s[-1]=='A'
        # BSHA分级（ZC>0+触顶）
        if zc_v>0 and is_touch and not np.isnan(bsha_v):
            if bsha_v<1: agg_bsha[('BSHA0~1',)].add(nhr)
            elif bsha_v<2: agg_bsha[('BSHA1~2',)].add(nhr)
            elif bsha_v<3: agg_bsha[('BSHA2~3',)].add(nhr)
            elif bsha_v<5: agg_bsha[('BSHA3~5',)].add(nhr)
            elif bsha_v<8: agg_bsha[('BSHA5~8',)].add(nhr)
            elif bsha_v<10: agg_bsha[('BSHA8~10',)].add(nhr)
            else: agg_bsha[('BSHA>=10',)].add(nhr)
        # 最强信号
        if zc_v>0:
            if is_touch and not np.isnan(bsha_v) and bsha_v>=8: agg_最强[('触顶+BSHA≥8',)].add(nhr)
            if is_touch and '乙' in ab and not np.isnan(bsha_v) and bsha_v>=5: agg_最强[('乙+触顶+BSHA≥5',)].add(nhr)
            if is_touch and not np.isnan(hd_v) and hd_v>=3: agg_最强[('触顶+合顶≥3',)].add(nhr)
            if is_touch and not np.isnan(bsha_v) and bsha_v>=8 and not np.isnan(hd_v) and hd_v>=3: agg_最强[('触顶+BSHA≥8+合顶≥3',)].add(nhr)
        # 十字星形态（触顶+BSHA>=8）
        if zc_v>0 and is_touch and not np.isnan(bsha_v) and bsha_v>=8:
            o=opn[j]; c=cls[j]; h=hig[j]; l=low[j]
            if np.isnan(o) or np.isnan(c) or np.isnan(h) or np.isnan(l) or h<=l: continue
            body=abs(c-o); rng=h-l
            if rng<=0: continue
            upper=h-max(o,c)
            is_doji = body < 0.1*rng
            is_long_upper = upper > 2*body and upper > 0.4*rng
            is_yin = c < (cls[j-1] if j>0 else c)
            if is_doji and not is_long_upper:
                agg_十字星[('十字星无长上影',)].add(nhr)
                if not np.isnan(bsha_v):
                    if bsha_v<5: agg_十字星_bsha[('十字星+BSHA<5',)].add(nhr)
                    elif bsha_v<8: agg_十字星_bsha[('十字星+BSHA5~8',)].add(nhr)
                    else: agg_十字星_bsha[('十字星+BSHA≥8',)].add(nhr)
            elif is_long_upper:
                agg_十字星[('长上影',)].add(nhr)
            elif is_yin:
                agg_十字星[('阴柱',)].add(nhr)
            else:
                agg_十字星[('无形态',)].add(nhr)
        # BSHA5 各位置（等5+ZC<0+乙 等）
        if not np.isnan(bsha_v) and bsha_v>5:
            if za_v==-1 and zc_v<0 and '乙' in ab:
                agg_bsha5[('等5+ZC<0+乙+BSHA5',)].add(nhr)

print(f'耗时 {time.time()-t0:.0f}s')
out=[]
out.append('='*70)
out.append('重跑 BSHA 相关数据（用真实BSHA=表头[19]日机警）')
out.append('='*70)
def dump(title, agg, keys):
    out.append(f'【{title}】')
    out.append(f'{"条件":<26s}  {"P3":>7s}  {"P5":>7s}  {"均值":>7s}  {"样本":>10s}')
    out.append('-'*60)
    for k in keys:
        kk=(k,) if isinstance(k,str) else k
        s=agg[kk].stats()
        if s: out.append(f'{str(k):<26s}  {s["P3"]:>6.1f}%  {s["P5"]:>6.1f}%  {s["均值"]:>6.2f}  {s["n"]:>10,d}')
    out.append('')
dump('BSHA 分级（ZC>0+触顶）', agg_bsha, ['BSHA0~1','BSHA1~2','BSHA2~3','BSHA3~5','BSHA5~8','BSHA8~10','BSHA>=10'])
dump('最强信号', agg_最强, ['触顶+BSHA≥8','乙+触顶+BSHA≥5','触顶+合顶≥3','触顶+BSHA≥8+合顶≥3'])
dump('十字星形态（触顶+BSHA≥8）', agg_十字星, ['十字星无长上影','长上影','阴柱','无形态'])
dump('十字星×BSHA', agg_十字星_bsha, ['十字星+BSHA<5','十字星+BSHA5~8','十字星+BSHA≥8'])
dump('等5+ZC<0+乙+BSHA5', agg_bsha5, ['等5+ZC<0+乙+BSHA5'])
result='\n'.join(out)
print(result)
with open('____temp/重跑BSHA_结果.txt','w',encoding='utf-8') as f: f.write(result)
print(f'\n结果已保存: ____temp/重跑BSHA_结果.txt')
