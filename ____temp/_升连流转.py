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
print(f'WXZC>0 样本: {len(wk)}')

# ① 什么形态转为升连（前柱型 → 当前升连）
print('='*90)
print('① 什么形态转为升连（前柱型 → 当前升连）')
print('='*90)
sub = wk[wk['柱型']=='升连']
print(f'当前升连 样本: {len(sub):,}')
print('前柱型分布:')
for t, n in sub['前柱型'].value_counts().items():
    print(f'  {t}: {n:,} ({n/len(sub)*100:.1f}%)')

# ② 升连维持（当前升连 → 下周柱型）
print()
print('='*90)
print('② 升连维持（当前升连 → 下周柱型）')
print('='*90)
sub = wk[wk['柱型']=='升连']
print(f'当前升连 样本: {len(sub):,}')
print('下周柱型分布:')
for t, n in sub['下周柱型'].value_counts().items():
    print(f'  {t}: {n:,} ({n/len(sub)*100:.1f}%)')

# ③ 升连转为非升连（当前升连 → 下周非升连，细分）
print()
print('='*90)
print('③ 升连转为非升连（当前升连 → 下周非升连）')
print('='*90)
sub = wk[(wk['柱型']=='升连')&(wk['下周柱型']!='升连')]
print(f'升连→非升连 样本: {len(sub):,}')
print('下周柱型分布:')
for t, n in sub['下周柱型'].value_counts().items():
    print(f'  {t}: {n:,} ({n/len(sub)*100:.1f}%)')
