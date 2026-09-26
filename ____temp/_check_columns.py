# -*- coding: utf-8 -*-
"""验证忠/中方向倾向：DXCD维持状态时，DXZC/DXZD交叉次数对比"""
import io, os, glob, csv, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 谕组日 CSV 目录
DATA_DIR = '昭明算展/谕组日'

# 列映射（VBA权威，勿信表头）
# col8=DXCD, col13=日ZA, col14=日ZC, col15=日ZE
# 需要确认 DXZD 列。先看表头
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 读取第一个文件确认列结构
with io.open(files[0], encoding='gbk', errors='replace') as f:
    header = f.readline().strip().split(',')
    print('表头列数:', len(header))
    for i, h in enumerate(header):
        print(f'col{i}: {h}')

# 确认 DXCD/DXZC/DXZD 列
# 从表头找 DXCD, 日ZC, 日ZD
for i, h in enumerate(header):
    if 'DXCD' in h or '日ZC' in h or '日ZD' in h or '日ZA' in h:
        print(f'  -> col{i} = {h}')