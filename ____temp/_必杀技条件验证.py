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

# 简化必杀技条件：金银×四波×柱型(42组合之一) 且 盈提含 宽高/高连/宽连/高/宽
# 先定义42组合
p3_combos = set()
grp = wk.groupby(wk['金银']+wk['四波']+wk['柱型名'])['下周HR'].agg(['count'])
grp.columns=['n']
p3_combos = set(grp[grp['n']>=1000].index)
print(f'42组合数: {len(p3_combos)}')

# 简化条件
mask = (wk['金银']+wk['四波']+wk['柱型名']).isin(p3_combos) & wk['盈提'].str.contains('宽高|高连|宽连|高|宽', regex=True)
sub = wk[mask]
p3 = (sub['下周HR']>=3).mean()*100
print(f'简化必杀技条件: P3={p3:.1f}%  n={len(sub):,}')

# 检查是否误纳 P<70% 的组合
# 按 金银×四波×柱型+盈提 分组，看简化条件内的组合 P≥3%
grp2 = sub.groupby([sub['金银']+sub['四波']+sub['柱型名'], sub['盈提']])['下周HR'].agg(['count', lambda x: (x>=3).mean()*100])
grp2.columns = ['n','p3']
grp2 = grp2[grp2['n']>=1000]
low = grp2[grp2['p3']<70]
print(f'简化条件内 P<70% 的组合数: {len(low)}')
if len(low)>0:
    print('P<70% 的组合（误纳）:')
    for (b,yt), r in low.sort_values('p3').iterrows():
        print(f'  {b}+盈提={yt}: P3={r["p3"]:.1f}%  n={r["n"]:,}')
