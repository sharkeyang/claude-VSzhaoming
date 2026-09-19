# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')

def classify(sf):
    if not sf: return '_'
    return sf[-1]

# 单文件验证 6.5.1.2
stats = collections.defaultdict(lambda: [0, 0])
parse_fail = 0
n = 0
with open(files[0], encoding='gbk', errors='replace') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 31: continue
        n += 1
        try:
            zc = int(row[14])
            nxt = float(row[26])
        except Exception as e:
            parse_fail += 1
            continue
        state = classify(row[30].strip())
        key = ('ZC>0' if zc > 0 else 'ZC<=0', state)
        stats[key][0] += 1
        if nxt >= 3:
            stats[key][1] += 1

print(f'文件: {files[0]}')
print(f'总行: {n}, 解析失败: {parse_fail}')
print('=== 6.5.1.2 单文件 ===')
for (zc, state), (cnt, p3) in sorted(stats.items()):
    if cnt == 0: continue
    print(f'{zc}+{state:<22}{p3/cnt*100:>7.1f}%{cnt:>10,}')
