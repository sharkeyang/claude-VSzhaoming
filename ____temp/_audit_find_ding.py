# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 扫描所有列，找包含 a龙/b龙 的列
col_hits = collections.defaultdict(collections.Counter)
n = 0
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 62: continue
        n += 1
        for j, v in enumerate(row):
            if 'a龙' in v or 'b龙' in v or '雀' in v or '虎' in v:
                col_hits[j][v.strip()] += 1
        if n > 2000: break
print(f'样本: {n}')
for j, c in sorted(col_hits.items()):
    print(f'列[{j}]: {dict(list(c.most_common(5)))}')
