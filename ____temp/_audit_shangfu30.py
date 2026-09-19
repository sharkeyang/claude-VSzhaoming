# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 上符串在列[30]，检查末位分布（底=w/哈=v/无=_）
last = collections.Counter()
full = collections.Counter()
n = 0
for fp in files[:200]:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 31: continue
            n += 1
            s = row[30].strip()
            full[s] += 1
            if s:
                last[s[-1]] += 1
print(f'样本: {n}')
print('\n=== 上符串[30] 末位分布 ===')
for k, v in last.most_common():
    print(f'  {k!r}: {v} ({v/n*100:.1f}%)')
print('\n=== 上符串[30] 完整值 top25 ===')
for k, v in full.most_common(25):
    print(f'  {k!r}: {v}')
