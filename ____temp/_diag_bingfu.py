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
# 并符串周[51] 格式
print('=== 并符串周 前15个不同值 ===')
for v in wk['并符串周'].astype(str).unique()[:15]:
    print(f'  [{v}]')
print()
# 尾字符分布
print('=== 并符串周 尾字符分布 ===')
print(wk['并符串周'].astype(str).str[-1].value_counts())
print()
# 柱排周 前缀 vs 并符串周 尾字符 的关系
print('=== 柱排周前缀 与 并符串尾字符 交叉 ===')
s_zp = wk['柱排周'].astype(str)
s_bf = wk['并符串周'].astype(str)
# 升.尾连 的并符串尾字符
sub = wk[s_zp.str.startswith('升.尾连')]
print('升.尾连 的并符串尾字符:', sub['并符串周'].astype(str).str[-1].value_counts().to_dict())
sub = wk[s_zp.str.startswith('升.尾吞')]
print('升.尾吞 的并符串尾字符:', sub['并符串周'].astype(str).str[-1].value_counts().to_dict())
sub = wk[s_zp.str.startswith('跌.尾连')]
print('跌.尾连 的并符串尾字符:', sub['并符串周'].astype(str).str[-1].value_counts().to_dict())
