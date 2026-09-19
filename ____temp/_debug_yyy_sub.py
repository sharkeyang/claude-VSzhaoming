# -*- coding: utf-8 -*-
"""调试：阴-阳-阴 子类型分布"""
import pandas as pd, glob, sys
from collections import defaultdict, Counter
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

yyy_sub = Counter()
yyy_total = 0
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10])
    df.columns = ['柱排']
    cls = [classify_zp(v) for v in df['柱排'].astype(str).tolist()]
    yy = [yinyang(c) for c in cls]
    for j in range(len(cls)-2):
        if (yy[j], yy[j+1], yy[j+2]) == ('阴','阳','阴'):
            yyy_total += 1
            yyy_sub[(cls[j], cls[j+1], cls[j+2])] += 1
    if (i+1) % 100 == 0:
        print(f'  {i+1} files', flush=True)

print(f'\n阴-阳-阴 总数(500文件): {yyy_total}')
print(f'不同子类型数: {len(yyy_sub)}')
print('\n=== 阴-阳-阴 子类型分布 ===')
for s, n in yyy_sub.most_common(30):
    print(f'  {s}: {n}')
