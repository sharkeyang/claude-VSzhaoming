# -*- coding: utf-8 -*-
"""探索柱排/上符串/柱型列的值分布"""
import pandas as pd, glob, sys
from collections import Counter
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 只读前几个文件探索值
cnt_zp = Counter()   # 柱排[10]
cnt_sfs = Counter()  # 上符串[30]
cnt_zx = Counter()   # 柱型[27]
cnt_ding = Counter() # 顶型[43]
cnt_ding2 = Counter()# 顶型[45]

for i, f in enumerate(files[:30]):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,27,30,43,45])
    for v in df[10].astype(str): cnt_zp[v] += 1
    for v in df[30].astype(str): cnt_sfs[v] += 1
    for v in df[27].astype(str): cnt_zx[v] += 1
    for v in df[43].astype(str): cnt_ding[v] += 1
    for v in df[45].astype(str): cnt_ding2[v] += 1

print('\n=== 柱排[10] 值分布 ===')
for v, c in cnt_zp.most_common(40):
    print(f'  {v!r}: {c}')
print('\n=== 上符串[30] 值分布 ===')
for v, c in cnt_sfs.most_common(40):
    print(f'  {v!r}: {c}')
print('\n=== 柱型[27] 值分布 ===')
for v, c in cnt_zx.most_common(40):
    print(f'  {v!r}: {c}')
print('\n=== 顶型[43] 值分布 ===')
for v, c in cnt_ding.most_common(40):
    print(f'  {v!r}: {c}')
print('\n=== 顶型[45] 值分布 ===')
for v, c in cnt_ding2.most_common(40):
    print(f'  {v!r}: {c}')
