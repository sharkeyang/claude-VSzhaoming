# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 扫描所有列，找末位是 w/v/_ (上符底/哈/无) 的列
col_last = collections.defaultdict(collections.Counter)
n = 0
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 62: continue
        n += 1
        for j, v in enumerate(row):
            s = v.strip()
            if s:
                col_last[j][s[-1]] += 1
        if n > 3000: break
print(f'样本: {n}')
for j in range(62):
    c = col_last[j]
    # 找末位含 w/v/_ 的列
    hits = {k: v for k, v in c.items() if k in 'wv_'}
    if hits:
        print(f'列[{j}]: 末位 w/v/_ = {hits}')
