# -*- coding: utf-8 -*-
"""读取谕组日数据，理解 DXCD/DXZC/DXZD 结构"""
import io, os, glob, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))

# 读取几个文件，打印 DXCD(col8), 日ZC(col14), 日ZA(col13) 的值
for fp in files[:3]:
    print(f'=== {os.path.basename(fp)} ===')
    with io.open(fp, encoding='gbk', errors='replace') as f:
        header = f.readline()
        for i, line in enumerate(f):
            if i >= 20:
                break
            row = line.strip().split(',')
            if len(row) < 15:
                continue
            print(f'  DXCD={row[8]} 日ZA={row[13]} 日ZC={row[14]} 日ZE={row[15]}')
    print()