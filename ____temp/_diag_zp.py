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
# 柱排周 取值模式
print('=== 柱排周 前20个不同值 ===')
for v in wk['柱排周'].astype(str).unique()[:20]:
    print(f'  [{v}]')
print()
print('=== 柱排周 是否含(升)/(跌)前缀 ===')
s = wk['柱排周'].astype(str)
print(f'  含(升): {(s.str.contains("(升)")).sum()}')
print(f'  含(跌): {(s.str.contains("(跌)")).sum()}')
print(f'  以升开头: {(s.str.startswith("升")).sum()}')
print(f'  以跌开头: {(s.str.startswith("跌")).sum()}')
print(f'  含升(任意): {(s.str.contains("升")).sum()}')
print(f'  含跌(任意): {(s.str.contains("跌")).sum()}')
