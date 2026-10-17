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
wk['下周柱排'] = wk.groupby('fid')['柱排周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(z):
    if not isinstance(z,str): return ''
    if z.startswith('升.尾连'): return '升连'
    if z.startswith('升.尾吞'): return '升吞'
    if z.startswith('升.尾反孕'): return '升孕'
    if z.startswith('跌.尾吞'): return '跌吞'
    if z.startswith('跌.尾连'): return '跌连'
    if z.startswith('跌.尾反孕'): return '跌孕'
    return '人排/首柱'
wk['柱型'] = wk['柱排周'].astype(str).apply(柱型)
wk['前柱型'] = wk['前柱排'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周柱排'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()

def trans(name, mask):
    sub = wk[mask]
    n = len(sub)
    if n < 300:
        print(f'  {name}: n={n} 样本不足')
        return
    print(f'  {name}: n={n:,}')
    for t, c in sub['下周柱型'].value_counts().items():
        print(f'    → {t}: {c:,} ({c/n*100:.1f}%)')

print('='*90)
print('升连流转（当前柱型 → 下周柱型）')
print('='*90)
trans('升连', wk['柱型']=='升连')
trans('升孕', wk['柱型']=='升孕')
trans('升吞', wk['柱型']=='升吞')
trans('跌孕', wk['柱型']=='跌孕')
trans('跌吞', wk['柱型']=='跌吞')
trans('跌连', wk['柱型']=='跌连')
trans('人排/首柱', wk['柱型']=='人排/首柱')

print()
print('='*90)
print('进入升连的来源（前柱型 → 当前升连）')
print('='*90)
sub = wk[wk['柱型']=='升连']
n = len(sub)
print(f'  当前升连: n={n:,}')
for t, c in sub['前柱型'].value_counts().items():
    print(f'    {t} → 升连: {c:,} ({c/n*100:.1f}%)')
