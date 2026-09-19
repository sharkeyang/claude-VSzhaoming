# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
print('文件数:', len(files))
if files:
    with open(files[0], encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        hdr = next(r)
        print('列数:', len(hdr))
        for i, h in enumerate(hdr):
            print(f'[{i}] {h}')
