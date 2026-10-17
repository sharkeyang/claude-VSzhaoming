# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))[:50]
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
# 当前升连的前柱排 具体值
sub = wk[wk['柱排周'].astype(str).str.startswith('升.尾连')]
print('当前升连 前柱排 前20个不同值:')
for v in sub['前柱排'].astype(str).unique()[:20]:
    print(f'  [{v}]')
print()
# 首柱 出现情况
print('首柱 出现次数:', (wk['柱排周'].astype(str)=='首柱').sum())
print('首柱 前柱排:', (wk[wk['柱排周'].astype(str)=='首柱']['前柱排'].astype(str).unique()[:5]))
