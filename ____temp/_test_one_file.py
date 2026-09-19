# -*- coding: utf-8 -*-
import pandas as pd, glob, sys
from collections import Counter
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))

def classify_zp(v):
    v = str(v)
    if '尾连' in v:
        if v.startswith('升'): return '升连'
        if v.startswith('跌'): return '跌连'
        return '人连'
    if '尾吞' in v:
        if v.startswith('升'): return '升吞'
        if v.startswith('跌'): return '跌吞'
        return '人吞'
    if '尾反孕' in v:
        if v.startswith('升'): return '升孕'
        if v.startswith('跌'): return '跌孕'
        return '人孕'
    if '连后吞' in v: return '连后吞'
    if '吞吞' in v: return '吞吞'
    if '孕孕' in v: return '孕孕'
    return '其他'

def yinyang(zp_cls):
    if zp_cls in ('跌吞','跌孕','跌连'): return '阴'
    if zp_cls in ('升吞','升孕','升连'): return '阳'
    return '其他'

# 测试第一个文件
df = pd.read_csv(files[0], encoding='gbk', header=None, usecols=[10])
df.columns = ['柱排']
print(f'文件: {files[0]}')
print(f'总行数: {len(df)}')
vals = df['柱排'].astype(str).tolist()
print('\n前10个柱排值:')
for v in vals[:10]:
    print(f'  {v!r} -> {classify_zp(v)} -> {yinyang(classify_zp(v))}')
cls = [classify_zp(v) for v in vals]
yy = [yinyang(c) for c in cls]
print('\n柱排类分布:', Counter(cls))
print('阴阳分布:', Counter(yy))
# 找3连
n_yyy = 0
n_total = 0
yyy_examples = []
for j in range(len(cls)-2):
    n_total += 1
    if (yy[j], yy[j+1], yy[j+2]) == ('阴','阳','阴'):
        n_yyy += 1
        if len(yyy_examples) < 5:
            yyy_examples.append((vals[j], vals[j+1], vals[j+2]))
print(f'\n3连总数: {n_total}')
print(f'阴-阳-阴 数: {n_yyy}')
for e in yyy_examples:
    print(f'  例: {e}')
