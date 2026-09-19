# -*- coding: utf-8 -*-
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911\谕组日_sz000001.csv', encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for i, row in enumerate(r):
        if i >= 5: break
        hx = row[9]
        print(f'行{i}: 护型={hx!r} 护型[1]={hx[1]!r}')
        print(f'      顶型={row[43]!r}')
