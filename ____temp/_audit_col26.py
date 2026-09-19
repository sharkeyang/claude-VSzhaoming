# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 看列[26] 和 列[28] 的数值分布
c26 = collections.Counter()
c28 = collections.Counter()
n = 0
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 29: continue
        n += 1
        c26[row[26].strip()] += 1
        c28[row[28].strip()] += 1
        if n > 5000: break
print('=== 列[26] 分布 ===')
for k, v in c26.most_common(15):
    print(f'  {k!r}: {v}')
print('=== 列[28] 分布 ===')
for k, v in c28.most_common(15):
    print(f'  {k!r}: {v}')
