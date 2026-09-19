# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 列[28] 完整分布
c = collections.Counter()
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 62: continue
        c[row[28].strip()] += 1
print('列[28] 分布:')
for k, v in c.most_common(30):
    print(f'  {k!r}: {v}')
