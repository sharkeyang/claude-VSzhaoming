# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 对每列采样几个非空值，判断真实含义
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    rows = []
    for i, row in enumerate(r):
        if i >= 5: break
        rows.append(row)
# 打印每列的前3个非空值
for j in range(62):
    vals = []
    for row in rows:
        if j < len(row) and row[j].strip():
            vals.append(row[j].strip())
    if vals:
        print(f'[{j}] {vals[:3]}')
