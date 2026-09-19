# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 上符串[30]末位分布（全量）
last = collections.Counter()
n = 0
for fp in files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 31: continue
            n += 1
            s = row[30].strip()
            if s:
                last[s[-1]] += 1
print(f'总样本: {n}')
print('=== 上符串[30] 末位分布 ===')
for k, v in last.most_common():
    print(f'  {k!r}: {v} ({v/n*100:.1f}%)')
