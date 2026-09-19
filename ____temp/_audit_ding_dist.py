# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 统计顶型[45] 和 日龟BT顶[53]/日龟BT哼[54] 的分布
ding = collections.Counter()
bt_top = collections.Counter()
bt_heng = collections.Counter()
n = 0
for fp in files[:200]:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 62: continue
            n += 1
            ding[row[45].strip()] += 1
            bt_top[row[53].strip()] += 1
            bt_heng[row[54].strip()] += 1
print(f'样本: {n}')
print('\n=== 顶型[45] 分布 ===')
for k, v in ding.most_common(20):
    print(f'  {k!r}: {v}')
print('\n=== 日龟BT顶[53] 分布 ===')
for k, v in bt_top.most_common(10):
    print(f'  {k!r}: {v}')
print('\n=== 日龟BT哼[54] 分布 ===')
for k, v in bt_heng.most_common(10):
    print(f'  {k!r}: {v}')
