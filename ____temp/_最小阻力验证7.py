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
wk['前柱排'] = wk.groupby('fid')['柱排周'].shift(1)
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下周涨','下周HR'])
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(z):
    if not isinstance(z,str): return ''
    if z.startswith('升.尾连'): return '升连'
    if z.startswith('升.尾吞'): return '升吞'
    if z.startswith('升.尾反孕'): return '升孕'
    if z.startswith('跌.尾吞'): return '跌吞'
    if z.startswith('跌.尾连'): return '跌连'
    if z.startswith('跌.尾反孕'): return '跌孕'
    return '其他'
wk['柱型'] = wk['柱排周'].astype(str).apply(柱型)
wk['前柱型'] = wk['前柱排'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

def show(name, mask, min_n=300):
    sub = wk[mask]
    n = len(sub)
    if n < min_n:
        print(f'  {name}: n={n} 样本不足')
        return
    yang = (sub['下周涨']>0).mean()*100
    hr0 = (sub['下周HR']>0).mean()*100
    hr1 = (sub['下周HR']>=1).mean()*100
    hr3 = (sub['下周HR']>=3).mean()*100
    print(f'  {name}: n={n:,}  涨>0={yang:.1f}%  HR>0={hr0:.1f}%  HR≥1%={hr1:.1f}%  HR≥3%={hr3:.1f}%')

print('='*90)
print('假设4 重新理解: 跌孕/跌吞→跌连(当前跌连,前柱跌孕/跌吞)')
print('='*90)
show('前柱跌孕+当前跌连', (wk['前柱型']=='跌孕')&(wk['柱型']=='跌连'))
show('前柱跌吞+当前跌连', (wk['前柱型']=='跌吞')&(wk['柱型']=='跌连'))
show('前柱跌孕/跌吞+当前跌连', (wk['前柱型'].isin(['跌孕','跌吞']))&(wk['柱型']=='跌连'))

print()
print('='*90)
print('假设4 补充: 升连链后出现跌连(前柱升连,当前跌连)')
print('='*90)
show('前柱升连+当前跌连', (wk['前柱型']=='升连')&(wk['柱型']=='跌连'))
