# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os, glob, json, time
from collections import defaultdict
DATA_DIR = '昭明算展/谕组日'
with open('_产出物/MP1_花册分类映射.json', encoding='utf-8') as f: board_map = json.load(f)
目标板块 = {'Qic', 'Qim', 'Qit'}
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))

class A:
    def __init__(self): self.n=0; self.s=0.0; self.p3=0; self.p5=0
    def add(self, x):
        self.n+=1; self.s+=x
        if x>=3: self.p3+=1
        if x>=5: self.p5+=1
    def stats(self):
        if self.n==0: return None
        return {'n':self.n,'P3':self.p3/self.n*100,'P5':self.p5/self.n*100,'均值':self.s/self.n}

# 聚合器
agg_上符 = defaultdict(A)
agg_上符_zc = defaultdict(A)
agg_zc_touch = defaultdict(A)
agg_合顶 = defaultdict(A)
agg_护型 = defaultdict(A)
agg_护型合顶 = defaultdict(A)
agg_bsha = defaultdict(A)
agg_最强 = defaultdict(A)
agg_触顶持续 = defaultdict(A)
agg_十字星 = defaultdict(A)
agg_十字星_bsha = defaultdict(A)

t0=time.time()
for i,f in enumerate(files):
    if i%1000==0: print(f'  {i}/{len(files)}', flush=True)
    try: df = pd.read_csv(f, encoding='gbk', usecols=['高幅','日ZC','日ZA','层界','BSHA','宽哼JC','DXAB','日龟BT合顶哼','开','收','高','低'])
    except: continue
    cidl = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 目标板块: continue
    hr = pd.to_numeric(df['高幅'], errors='coerce').values
    next_hr = np.roll(hr,-1); next_hr[-1]=np.nan
    zc = pd.to_numeric(df['日ZC'], errors='coerce').values
    bsha = pd.to_numeric(df['BSHA'], errors='coerce').values
    hd = pd.to_numeric(df['日龟BT合顶哼'], errors='coerce').values
    sf = df['层界'].astype(str).values
    dxab = df['DXAB'].astype(str).values
    opn = pd.to_numeric(df['开'], errors='coerce').values
    cls = pd.to_numeric(df['收'], errors='coerce').values
    hig = pd.to_numeric(df['高'], errors='coerce').values
    low = pd.to_numeric(df['低'], errors='coerce').values
    n=len(df)
    for j in range(n-1):
        nhr=next_hr[j]
        if np.isnan(nhr): continue
        zc_v=zc[j]; bsha_v=bsha[j]; hd_v=hd[j]
        s=sf[j]; ab=dxab[j]
        is_touch = len(s)>0 and s[-1]=='A'
        # ① 上符串末位
        if len(s)>0:
            sym=s[-1]
            agg_上符[(sym,)].add(nhr)
            if zc_v>0: agg_上符_zc[('ZC>0',sym)].add(nhr)
        # ② ZC × 触顶
        if zc_v>0:
            if is_touch: agg_zc_touch[('ZC>0+触顶',)].add(nhr)
            else: agg_zc_touch[('ZC>0+非触顶',)].add(nhr)
        else:
            if is_touch: agg_zc_touch[('ZC<=0+触顶',)].add(nhr)
            else: agg_zc_touch[('ZC<=0+非触顶',)].add(nhr)
        # ③ 合顶天数(真值)
        if zc_v>0 and not np.isnan(hd_v):
            if hd_v>0:
                if hd_v<=5: agg_合顶[(hd_v,)].add(nhr)
                elif hd_v<=10: agg_合顶[('6-10',)].add(nhr)
                elif hd_v<=15: agg_合顶[('11-15',)].add(nhr)
                elif hd_v<=20: agg_合顶[('16-20',)].add(nhr)
                else: agg_合顶[('21+',)].add(nhr)
            else: agg_合顶[('未触顶',)].add(nhr)
        # ④ 护型 × 触顶
        if zc_v>0 and is_touch:
            if '乙' in ab: agg_护型[('乙+触顶',)].add(nhr)
            elif '甲' in ab: agg_护型[('甲+触顶',)].add(nhr)
            elif '己' in ab: agg_护型[('己+触顶',)].add(nhr)
            elif '戊' in ab: agg_护型[('戊+触顶',)].add(nhr)
            elif '丙' in ab: agg_护型[('丙+触顶',)].add(nhr)
        # ⑤ 护型 × 合顶≥3
        if zc_v>0 and is_touch and not np.isnan(hd_v):
            hd3 = hd_v>=3
            if '乙' in ab:
                if hd3: agg_护型合顶[('乙+合顶≥3',)].add(nhr)
                else: agg_护型合顶[('乙+合顶<3',)].add(nhr)
            elif '甲' in ab:
                if hd3: agg_护型合顶[('甲+合顶≥3',)].add(nhr)
                else: agg_护型合顶[('甲+合顶<3',)].add(nhr)
            elif '己' in ab:
                if hd3: agg_护型合顶[('己+合顶≥3',)].add(nhr)
                else: agg_护型合顶[('己+合顶<3',)].add(nhr)
        # ⑨ BSHA 分级
        if zc_v>0 and is_touch and not np.isnan(bsha_v):
            if bsha_v<1: agg_bsha[('BSHA0~1',)].add(nhr)
            elif bsha_v<2: agg_bsha[('BSHA1~2',)].add(nhr)
            elif bsha_v<3: agg_bsha[('BSHA2~3',)].add(nhr)
            elif bsha_v<5: agg_bsha[('BSHA3~5',)].add(nhr)
            elif bsha_v<8: agg_bsha[('BSHA5~8',)].add(nhr)
            elif bsha_v<10: agg_bsha[('BSHA8~10',)].add(nhr)
            else: agg_bsha[('BSHA>=10',)].add(nhr)
        # ⑩ 最强信号
        if zc_v>0:
            if is_touch and not np.isnan(bsha_v) and bsha_v>=8: agg_最强[('触顶+BSHA≥8',)].add(nhr)
            if is_touch and '乙' in ab and not np.isnan(bsha_v) and bsha_v>=5: agg_最强[('乙+触顶+BSHA≥5',)].add(nhr)
            if is_touch and not np.isnan(hd_v) and hd_v>=3: agg_最强[('触顶+合顶≥3',)].add(nhr)
            if is_touch and not np.isnan(bsha_v) and bsha_v>=8 and not np.isnan(hd_v) and hd_v>=3: agg_最强[('触顶+BSHA≥8+合顶≥3',)].add(nhr)
        # ⑥ 触顶持续性
        if is_touch and j+1<n-1:
            sf_next = sf[j+1]
            next_touch = len(sf_next)>0 and sf_next[-1]=='A'
            if next_touch: agg_触顶持续[('次日仍触顶',)].add(nhr)
            else: agg_触顶持续[('次日不触顶',)].add(nhr)
        # 十字星形态（触顶+BSHA≥8 子集）
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

print(f'耗时 {time.time()-t0:.0f}s')
out=[]
out.append('='*70)
out.append('5.4 触顶信号体系（高波池全量）重跑')
out.append('='*70)
def dump(title, agg, keys):
    out.append(f'【{title}】')
    out.append(f'{"条件":<22s}  {"P3":>7s}  {"P5":>7s}  {"均值":>7s}  {"样本":>10s}')
    out.append('-'*60)
    for k in keys:
        kk=(k,) if isinstance(k,str) else k
        s=agg[kk].stats()
        if s: out.append(f'{str(k):<22s}  {s["P3"]:>6.1f}%  {s["P5"]:>6.1f}%  {s["均值"]:>6.2f}  {s["n"]:>10,d}')
    out.append('')
dump('① 上符串末位（全样本）', agg_上符, ['A','B','v','w','_'])
dump('① 上符串末位（ZC>0）', agg_上符_zc, [('ZC>0','A'),('ZC>0','B'),('ZC>0','v'),('ZC>0','w'),('ZC>0','_')])
dump('② ZC × 触顶', agg_zc_touch, ['ZC>0+触顶','ZC>0+非触顶','ZC<=0+触顶','ZC<=0+非触顶'])
dump('③ 合顶天数（真值）', agg_合顶, ['未触顶',1,2,3,4,5,'6-10','11-15','16-20','21+'])
dump('④ 护型 × 触顶', agg_护型, ['乙+触顶','甲+触顶','己+触顶','戊+触顶','丙+触顶'])
dump('⑤ 护型 × 合顶≥3', agg_护型合顶, ['乙+合顶≥3','乙+合顶<3','甲+合顶≥3','甲+合顶<3','己+合顶≥3','己+合顶<3'])
dump('⑨ BSHA 分级', agg_bsha, ['BSHA0~1','BSHA1~2','BSHA2~3','BSHA3~5','BSHA5~8','BSHA8~10','BSHA>=10'])
dump('⑩ 最强信号', agg_最强, ['触顶+BSHA≥8','乙+触顶+BSHA≥5','触顶+合顶≥3','触顶+BSHA≥8+合顶≥3'])
dump('⑥ 触顶持续性', agg_触顶持续, ['次日仍触顶','次日不触顶'])
dump('5.4.2.1 失败情形（触顶+BSHA≥8）', agg_十字星, ['十字星无长上影','长上影','阴柱','无形态'])
dump('5.4.2.2 十字星 × BSHA', agg_十字星_bsha, ['十字星+BSHA<5','十字星+BSHA5~8','十字星+BSHA≥8'])
result='\n'.join(out)
print(result)
with open('____temp/重跑54_结果.txt','w',encoding='utf-8') as f: f.write(result)
print(f'\n结果已保存: ____temp/重跑54_结果.txt')
