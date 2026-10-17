# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
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
wk = wk[wk['WXZC']>0].copy()

# 金银×四波×柱型+盈提 全组合（样本>=1000），P>=70%
grp = wk.groupby([wk['金银']+wk['四波']+wk['柱型名'], wk['盈提']])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
grp.columns = ['n','p3']
grp = grp[grp['n']>=1000]
high = grp[grp['p3']>=70]

# 按 金银×四波×柱型 分组，看每个基础组合的盈提示
print('='*90)
print('按 金银×四波×柱型 分组（每个基础组合的 P≥70% 盈提示）')
print('='*90)
for b, sub in high.groupby(level=0):
    print(f'\n【{b}】')
    for (_, yt), r in sub.sort_values('p3', ascending=False).iterrows():
        print(f'  +盈提={yt}: P3={r["p3"]:.1f}%  n={r["n"]:,}')
