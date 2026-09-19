# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 检查几列的内容，找"底"和"哈"
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for i, row in enumerate(r):
        if i >= 8: break
        print(f'行{i}:')
        print(f'  顶型[45]={row[45]!r}')
        print(f'  日等型[46]={row[46]!r}')
        print(f'  仓日类[47]={row[47]!r}')
        print(f'  宽哈JC[41]={row[41]!r}')
        print(f'  日龟BT顶[53]={row[53]!r}')
        print(f'  日龟BT哼[54]={row[54]!r}')
        print(f'  日龟顶触[55]={row[55]!r}')
        print(f'  日龟BT合顶哼[56]={row[56]!r}')
