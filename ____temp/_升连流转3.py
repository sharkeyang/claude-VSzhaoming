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
# 用并符串周[51]尾字符分类柱型（权威定义）
wk['前并符'] = wk.groupby('fid')['并符串周'].shift(1)
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z = bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z, '其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['前柱型'] = wk['前并符'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

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
print('升连流转（当前柱型 → 下周柱型，用并符串尾字符）')
print('='*90)
trans('升连', wk['柱型']=='升连')
trans('升孕', wk['柱型']=='升孕')
trans('升吞', wk['柱型']=='升吞')
trans('跌孕', wk['柱型']=='跌孕')
trans('跌吞', wk['柱型']=='跌吞')
trans('跌连', wk['柱型']=='跌连')

print()
print('='*90)
print('进入升连的来源（前柱型 → 当前升连）')
print('='*90)
sub = wk[wk['柱型']=='升连']
n = len(sub)
print(f'  当前升连: n={n:,}')
for t, c in sub['前柱型'].value_counts().items():
    print(f'    {t} → 升连: {c:,} ({c/n*100:.1f}%)')
