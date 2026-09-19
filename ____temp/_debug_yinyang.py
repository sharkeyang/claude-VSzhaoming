# -*- coding: utf-8 -*-
"""调试：为什么阴阳阴3连序列样本为0"""
import pandas as pd, glob, sys
from collections import Counter, defaultdict
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

# 统计每个柱排类的出现次数 + 找具体3连序列
cls_count = Counter()
seq_count = Counter()
# 找包含 跌吞/升孕/跌吞 的具体柱排值
val_die_tun = Counter()  # 跌吞的具体值
val_sheng_yun = Counter()  # 升孕的具体值

for i, f in enumerate(files[:200]):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10])
    df.columns = ['柱排']
    vals = df['柱排'].astype(str).tolist()
    cls = [classify_zp(v) for v in vals]
    for c in cls: cls_count[c] += 1
    for v, c in zip(vals, cls):
        if c == '跌吞': val_die_tun[v] += 1
        if c == '升孕': val_sheng_yun[v] += 1
    # 3连序列
    for j in range(len(cls)-2):
        seq_count[(cls[j], cls[j+1], cls[j+2])] += 1
    if (i+1) % 50 == 0:
        print(f'  {i+1} files', flush=True)

print('\n=== 柱排类分布（前200文件） ===')
for c, n in cls_count.most_common():
    print(f'  {c}: {n}')

print('\n=== 跌吞的具体柱排值 ===')
for v, n in val_die_tun.most_common(20):
    print(f'  {v!r}: {n}')
print('\n=== 升孕的具体柱排值 ===')
for v, n in val_sheng_yun.most_common(20):
    print(f'  {v!r}: {n}')

print('\n=== 3连序列分布（前30） ===')
for s, n in seq_count.most_common(30):
    print(f'  {s}: {n}')

# 检查是否有 跌吞+升孕+跌吞
target = ('跌吞','升孕','跌吞')
print(f'\n=== 目标序列 {target} 出现次数: {seq_count.get(target, 0)} ===')
# 检查跌吞开头的序列
print('\n=== 跌吞开头的3连序列 ===')
for s, n in seq_count.most_common():
    if s[0] == '跌吞':
        print(f'  {s}: {n}')
