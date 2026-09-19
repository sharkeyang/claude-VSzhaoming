# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
print('文件数:', len(files))

# 权威列映射（VBA导出顺序）
# [39] 宽哈JC, [53] 日龟BT顶, [54] 日龟BT哼, [55] 日龟顶触, [56] 日龟BT合顶哼
# 检查"底"和"哈"相关列
cols = {
    39: '宽哈JC',
    53: '日龟BT顶',
    54: '日龟BT哼',
    55: '日龟顶触',
    56: '日龟BT合顶哼',
}
for j, name in cols.items():
    c = collections.Counter()
    with open(files[0], encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 62: continue
            c[row[j].strip()] += 1
    print(f'\n=== [{j}] {name} 分布 ===')
    for k, v in c.most_common(8):
        print(f'  {k!r}: {v}')
