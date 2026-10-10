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

# 金银
m_gold = wk['势型'].str.contains('金', na=False)
m_silver = wk['势型'].str.contains('银', na=False)
m_xi = wk['势型'].str.contains('唏', na=False)
m_xu = wk['势型'].str.contains('嘘', na=False)
m_niao = wk['势型'].str.contains('尿', na=False)
m_shi = wk['势型'].str.contains('屎', na=False)
jy = [('金',m_gold),('银',m_silver),('唏',m_xi),('嘘',m_xu),('尿',m_niao),('屎',m_shi)]

# 四态
m_shengzhu = (wk['WXAB']>0) & (wk['WXZB']>0)
m_jiangzhu = (wk['WXAB']<0) & (wk['WXZB']<0)
m_jiangzhuan = (wk['WXAB']<0) & (wk['WXZB']>0)
m_shengzhuan = (wk['WXAB']>0) & (wk['WXZB']<0)
st = [('升主龙',m_shengzhu),('降主虎',m_jiangzhu),('降转武',m_jiangzhuan),('升转雀',m_shengzhuan)]

# 目标：平均周涨（方向预测）
y = wk['周涨']
base = y.mean()

def 极差(masks, min_n=1000):
    ps = []
    for name, m in masks:
        n = m.sum()
        if n < min_n: continue
        ps.append((y[m].mean(), n))
    if not ps: return None
    ps.sort()
    return ps[-1][0] - ps[0][0], ps[-1][0], ps[0][0]

print(f'基线平均周涨 = {base:.3f}%')
print()
print('=== 方案A：仅金银（对平均周涨）===')
r = 极差(jy)
print(f'  极差: {r[0]:.3f}pp  最高: {r[1]:.3f}%  最低: {r[2]:.3f}%')
print('=== 方案B：仅四态（对平均周涨）===')
r = 极差(st)
print(f'  极差: {r[0]:.3f}pp  最高: {r[1]:.3f}%  最低: {r[2]:.3f}%')
print('=== 方案C：金银×四态叠加（对平均周涨）===')
叠加 = [(f'{jn}+{sn}', jm & sm) for jn, jm in jy for sn, sm in st]
r = 极差(叠加)
print(f'  极差: {r[0]:.3f}pp  最高: {r[1]:.3f}%  最低: {r[2]:.3f}%')
print()
# 叠加最优组合
print('=== 叠加最优/最差组合 ===')
combs = []
for name, m in 叠加:
    n = m.sum()
    if n < 1000: continue
    combs.append((y[m].mean(), name, n))
combs.sort(reverse=True)
print('  最优5:')
for p, name, n in combs[:5]:
    print(f'    {name}: 平均周涨={p:.3f}%  n={n}')
print('  最差5:')
for p, name, n in combs[-5:]:
    print(f'    {name}: 平均周涨={p:.3f}%  n={n}')
