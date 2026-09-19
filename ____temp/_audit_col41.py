# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 检查列[41] 日层BTZA 和 列[42] 日层BT连阳 的内容
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for i, row in enumerate(r):
        if i >= 5: break
        print(f'行{i}: [41]={row[41]!r} [42]={row[42]!r} [43]={row[43]!r} [44]={row[44]!r}')
