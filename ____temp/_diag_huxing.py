# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))[:50]
dfs=[]
for f in files:
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2: dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
# 护型列[4] 格式
print('=== 护型列 前15个不同值 ===')
for v in wk['护型'].astype(str).unique()[:15]:
    print(f'  [{v}]')
print()
# 护型首字符分布
print('=== 护型首字符分布 ===')
print(wk['护型'].astype(str).str[0].value_counts())
print()
# 柱排周 六种分类
print('=== 柱排周 六种柱型(升吞O/升连Q/升孕o/跌吞V/跌连W/跌孕v) ===')
s = wk['柱排周'].astype(str)
for kw, name in [('升.尾吞','升吞O'),('升.尾连','升连Q'),('升.尾反孕','升孕o'),('跌.尾吞','跌吞V'),('跌.尾连','跌连W'),('跌.尾反孕','跌孕v')]:
    print(f'  {name}: {(s.str.startswith(kw)).sum()}')
print(f'  其他(首柱/人排等): {(~s.str.startswith("升.尾") & ~s.str.startswith("跌.尾")).sum()}')
