# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

def parse_ding(s):
    if not s: return None, None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

# 用当前存在的 谕组日 目录
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
print('文件数:', len(files))
n_total=0; n_hx=0
for fp in files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 44: continue
            n_total += 1
            try:
                hx = row[9][1] if len(row[9])>1 else None
                if hx == '甲': n_hx += 1
            except: continue
print('总行数:', n_total)
print('甲护型行数:', n_hx)
