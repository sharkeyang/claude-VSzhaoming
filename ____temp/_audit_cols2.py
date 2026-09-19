# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
# 用 glob 动态定位，避免硬编码中文路径
files = glob.glob(r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911\谕组日_sz000001.csv')
print('找到文件:', files)
if files:
    with open(files[0], encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for i, row in enumerate(r):
            if i >= 5: break
            hx = row[9]
            print(f'行{i}: 护型={hx!r} 护型[1]={hx[1]!r}')
            print(f'      顶型={row[43]!r}')
