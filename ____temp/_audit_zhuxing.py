# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 看柱型[27]和等型[44]的分布
c27 = collections.Counter()
c44 = collections.Counter()
n = 0
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 45: continue
        n += 1
        c27[row[27].strip()] += 1
        c44[row[44].strip()] += 1
        if n > 5000: break
print('=== 柱型[27] 分布 ===')
for k, v in c27.most_common(20):
    print(f'  {k!r}: {v}')
print('=== 等型[44] 分布 ===')
for k, v in c44.most_common(20):
    print(f'  {k!r}: {v}')
