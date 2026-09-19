# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')
import sys as _s
if len(_s.argv) > 1:
    files = files[:int(_s.argv[1])]

# 列映射（VBA导出权威）:
# [14] 日ZC, [26] 次日高幅, [30] 上符串
# P3 = 次日高幅[26] >= 3

def classify(sf):
    """上符串末位 -> 触顶状态"""
    if not sf: return '_'
    c = sf[-1]
    return c  # A/B/v/w/_

# 6.5.1.2: ZC方向 × 触顶状态
stats = collections.defaultdict(lambda: [0, 0])  # key -> [n, p3_cnt]
for fp in files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 31: continue
            try:
                zc = int(row[14])
                nxt = float(row[26])
            except:
                continue
            state = classify(row[30].strip())
            key = ('ZC>0' if zc > 0 else 'ZC<=0', state)
            stats[key][0] += 1
            if nxt >= 3:
                stats[key][1] += 1

print('=== 6.5.1.2 ZC方向 × 触顶状态 核心模型（新数据，w=触底已区分） ===')
print(f'{"条件":<28}{"P3":>8}{"样本":>12}')
for (zc, state), (n, p3) in sorted(stats.items()):
    if n == 0: continue
    print(f'{zc}+{state:<22}{p3/n*100:>7.1f}%{n:>12,}')
