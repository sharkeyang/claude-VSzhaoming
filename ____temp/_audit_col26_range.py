# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
# 列[26] 完整数值分布
vals = []
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 27: continue
        try:
            vals.append(float(row[26]))
        except:
            pass
vals.sort()
n = len(vals)
print(f'列[26] 样本: {n}')
print(f'  min={vals[0]}, max={vals[-1]}')
print(f'  >=3 占比: {sum(1 for v in vals if v>=3)/n*100:.1f}%')
print(f'  >=2 占比: {sum(1 for v in vals if v>=2)/n*100:.1f}%')
print(f'  >=1 占比: {sum(1 for v in vals if v>=1)/n*100:.1f}%')
print(f'  >0 占比: {sum(1 for v in vals if v>0)/n*100:.1f}%')
print(f'  中位数: {vals[n//2]}')
