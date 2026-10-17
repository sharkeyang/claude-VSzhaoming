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
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z = bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z, '其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()
print(f'WXZC>0 样本: {len(wk)}')

order = ['升连','升吞','升孕','跌吞','跌连','跌孕']
print()
print('='*90)
print('完整 6x6 流转矩阵（当前柱型 -> 下周柱型，WXZC>0 周类）')
print('='*90)
header = '当前/下周'.ljust(8) + ''.join(t.rjust(10) for t in order)
print(header)
for cur in order:
    sub = wk[wk['柱型']==cur]
    n = len(sub)
    cells = []
    for nxt in order:
        c = (sub['下周柱型']==nxt).sum()
        pct = c/n*100 if n>0 else 0
        cells.append(f'{pct:>9.1f}%')
    print(cur.ljust(8) + ''.join(cells) + f'  n={n:,}')

print()
print('='*90)
print('样本数矩阵')
print('='*90)
print(header)
for cur in order:
    sub = wk[wk['柱型']==cur]
    cells = []
    for nxt in order:
        c = (sub['下周柱型']==nxt).sum()
        cells.append(f'{c:>10,}')
    print(cur.ljust(8) + ''.join(cells))
