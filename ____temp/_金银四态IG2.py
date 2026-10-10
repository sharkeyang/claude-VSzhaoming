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
y = (wk['下周HR'] >= 1).astype(int)
base = y.mean()
H = lambda p: -(p*np.log2(p) + (1-p)*np.log2(1-p)) if 0<p<1 else 0
Hy = H(base)
total = len(y)

def IG(masks):
    ig = Hy
    for m in masks:
        n = m.sum()
        if n==0: continue
        ig -= (n/total)*H(y[m].mean())
    return ig

# 金银
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

# 等类（对照）
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & wk['末位'].isin(['C','D','E','F'])
m3 = (wk['ZA周'] >= 2) & wk['末位'].isin(['A','B'])
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & wk['末位'].isin(['A','B','C','D'])
m7 = (wk['ZA周'] <= -2) & wk['末位'].isin(['E','F'])
eqs = [m1,m2,m3,m5,m6,m7]

# 柱排（对照）
m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)
zp = [m_up,m_ren,m_dn]

# 地型（对照）
def 提取地型(p3):
    if pd.isna(p3): return ''
    f0 = str(p3).split('_')[0]
    return f0[1:] if len(f0) > 1 else ''
wk['地型'] = wk['周策略P3'].apply(提取地型)
dx = [wk['地型']==d for d in ['0橅','1柜','2栅','3桮','6娝','7姗','8姖','9妩']]

print(f'基线 P={base*100:.1f}%  H(y)={Hy:.4f}bit')
print(f'{"维度":<12}{"IG(bit)":<12}{"占H(y)":<10}{"分组数"}')
for name, masks in [('金银',jy),('四态',st),('等类',eqs),('柱排',zp),('地型',dx)]:
    ig = IG(masks)
    print(f'{name:<12}{ig:<12.4f}{ig/Hy*100:<10.1f}%{len(masks)}')
print()
print('叠加(金银×四态):', f'{IG([jm&sm for jm in jy for sm in st]):.4f} bit')
print('叠加(金银×四态×等类):', f'{IG([jm&sm&em for jm in jy for sm in st for em in eqs]):.4f} bit')
