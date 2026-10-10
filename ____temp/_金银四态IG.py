# -*- coding: utf-8 -*-
import pandas as pd, glob, io, sys, numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for i,f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2:
            df['fid']=i
            dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周HR'])
wk['势型'] = wk['周势型(WXCD护型)'].astype(str)
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')

# 目标：下周HR>=1（冲高达标）
y = (wk['下周HR'] >= 1).astype(int)
base = y.mean()

def 信息增益(mask_list):
    """IG = H(y) - sum(p(c)*H(y|c))，衡量分组对y的预测力"""
    H = lambda p: -(p*np.log2(p) + (1-p)*np.log2(1-p)) if 0<p<1 else 0
    Hy = H(base)
    total = len(y)
    ig = Hy
    for m in mask_list:
        n = m.sum()
        if n==0: continue
        p = y[m].mean()
        ig -= (n/total)*H(p)
    return ig

# 金银分类
m_gold = wk['势型'].str.contains('金', na=False)
m_silver = wk['势型'].str.contains('银', na=False)
m_xi = wk['势型'].str.contains('唏', na=False)
m_xu = wk['势型'].str.contains('嘘', na=False)
m_niao = wk['势型'].str.contains('尿', na=False)
m_shi = wk['势型'].str.contains('屎', na=False)
jy = [m_gold,m_silver,m_xi,m_xu,m_niao,m_shi]

# 四态
m_shengzhu = (wk['WXAB']>0) & (wk['WXZB']>0)
m_jiangzhu = (wk['WXAB']<0) & (wk['WXZB']<0)
m_jiangzhuan = (wk['WXAB']<0) & (wk['WXZB']>0)
m_shengzhuan = (wk['WXAB']>0) & (wk['WXZB']<0)
st = [m_shengzhu,m_jiangzhu,m_jiangzhuan,m_shengzhuan]

# 叠加
叠加 = [jm & sm for jm in jy for sm in st]

print(f'基线 P(HR>=1) = {base*100:.1f}%')
print(f'H(y) = {-(base*np.log2(base)+(1-base)*np.log2(1-base)):.4f} bit')
print()
print(f'方案A 仅金银: IG = {信息增益(jy):.4f} bit')
print(f'方案B 仅四态: IG = {信息增益(st):.4f} bit')
print(f'方案C 叠加:   IG = {信息增益(叠加):.4f} bit')
print()
# 信息增益提升
ig_a = 信息增益(jy); ig_b = 信息增益(st); ig_c = 信息增益(叠加)
print(f'叠加 vs 金银: +{ig_c-ig_a:.4f} bit ({(ig_c-ig_a)/ig_a*100:.1f}%)')
print(f'叠加 vs 四态: +{ig_c-ig_b:.4f} bit ({(ig_c-ig_b)/ig_b*100:.1f}%)')
print(f'金银 vs 四态: +{ig_a-ig_b:.4f} bit')
