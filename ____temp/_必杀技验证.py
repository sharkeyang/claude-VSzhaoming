# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys, re
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
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
def 四波(row):
    a,b = row['WXAB'], row['WXZB']
    if a>0 and b>0: return '龙'
    if a<0 and b>0: return '武'
    if a<0 and b<0: return '虎'
    if a>0 and b<0: return '雀'
    return ''
wk['四波'] = wk.apply(四波, axis=1)
wk['金银'] = wk['周势型(WXCD护型)'].astype(str).str[1]
wk['柱型'] = wk['并符串周'].astype(str).str[-1]
zx_map = {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}
wk['柱型名'] = wk['柱型'].map(zx_map)
wk['盈提'] = wk['盈提示'].astype(str)
wk['末位'] = wk['中符串周'].astype(str).str[-1]
def 等类(row):
    za = row['WXZA']
    mw = row['末位']
    if za == 1: return '等1'
    if za >= 2 and mw in ['C','D','E','F']: return '等2'
    if za >= 2 and mw in ['A','B']: return '等3'
    if za == -1: return '等5'
    if za <= -2 and mw in ['A','B','C','D']: return '等6'
    if za <= -2 and mw in ['E','F']: return '等7'
    return ''
wk['等类'] = wk.apply(等类, axis=1)
wk['护级'] = wk['护型'].astype(str).str[3]
wk['顶触'] = wk['顶触周'].astype(str)
wk = wk[wk['WXZC']>0].copy()

# 必杀技候选组合
cands = [
    ('金龙升连+宽高', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高'))),
    ('金龙升连+宽高连3', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高连3'))),
    ('唏龙跌孕+宽高', (wk['金银']=='唏')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽高'))),
    ('银龙跌孕+宽高', (wk['金银']=='银')&(wk['四波']=='龙')&(wk['柱型名']=='跌孕')&(wk['盈提'].str.contains('宽高'))),
    ('金龙升连+宽高连4', (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高连4'))),
]
print('='*90)
print('必杀技候选组合 验证（P≥3% + 稳定性）')
print('='*90)
for name, mask in cands:
    sub = wk[mask]
    n = len(sub)
    if n < 300: 
        print(f'  {name}: n={n} 样本不足')
        continue
    p3 = (sub['下周HR']>=3).mean()*100
    avg = sub['下周HR'].mean()
    # 分年稳定性
    sub['年'] = sub['主期'].astype(str).str[:4]
    years = sub.groupby('年')['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
    years.columns = ['n','p3']
    years = years[years['n']>=50]
    stable = years['p3'].min() if len(years)>0 else 0
    print(f'  {name}: P3={p3:.1f}%  期望HR={avg:.2f}%  n={n:,}  最差年={stable:.1f}%  年数={len(years)}')

# 尝试叠加更多维度（金龙升连+宽高 基础上）
print()
print('='*90)
print('金龙升连+宽高 基础上叠加更多维度（找85%+）')
print('='*90)
base_mask = (wk['金银']=='金')&(wk['四波']=='龙')&(wk['柱型名']=='升连')&(wk['盈提'].str.contains('宽高'))
base = wk[base_mask]
print(f'基线 金龙升连+宽高: P3={(base["下周HR"]>=3).mean()*100:.1f}%  n={len(base):,}')
for dim_name, dim_vals in [('等类',wk['等类']),('护级',wk['护级']),('顶触',wk['顶触'])]:
    grp = base.groupby(dim_vals)['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
    grp.columns = ['n','p3']
    grp = grp[grp['n']>=200]
    if len(grp)==0: continue
    best = grp['p3'].idxmax()
    print(f'  +{dim_name}={best}: P3={grp.loc[best,"p3"]:.1f}%  n={grp.loc[best,"n"]:,}')
