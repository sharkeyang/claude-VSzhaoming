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

def yinyang(c):
    if c in ('跌吞','跌孕','跌连'): return '阴'
    if c in ('升吞','升孕','升连'): return '阳'
    return '其他'

mode_cnt = Counter()  # 阴阳模式
yyy = Counter()       # 阴-阳-阴 子类型
n3 = 0
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10])
    cls = [classify_zp(v) for v in df[10].astype(str).tolist()]
    yy = [yinyang(c) for c in cls]
    for j in range(len(cls)-2):
        n3 += 1
        mode = (yy[j], yy[j+1], yy[j+2])
        mode_cnt[mode] += 1
        if mode == ('阴','阳','阴'):
            yyy[(cls[j], cls[j+1], cls[j+2])] += 1
    if (i+1) % 2000 == 0:
        print(f'  {i+1}', flush=True)

print(f'\n3连总窗口: {n3}')
print('\n=== 阴阳模式 ===')
for m in [('阴','阳','阴'),('阴','阳','阳'),('阳','阳','阴'),('阳','阴','阴'),('阳','阴','阳'),('阴','阴','阳'),('阴','阴','阴'),('阳','阳','阳')]:
    print(f'  {"".join(m)}: {mode_cnt.get(m,0)}')
print(f'\n阴-阳-阴 子类型数: {len(yyy)}')
for s, n in yyy.most_common(30):
    print(f'  {s}: {n}')
