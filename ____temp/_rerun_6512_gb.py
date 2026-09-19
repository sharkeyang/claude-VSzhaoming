# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\@VSwork\VS昭明计划VBA优化\_产出物\_工具')
from 随机抽样工具 import 加载市板映射, 是核心池

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
加载市板映射(r'D:\@VSwork\VS昭明计划VBA优化\____temp\市板映射.csv')
files = glob.glob(DATA_DIR + '/谕组日_*.csv')
# 高波池 = Qic+Qim+Qit
gb_files = [f for f in files if 是核心池(f.split('谕组日_')[1].replace('.csv',''))]
print(f'高波池文件数: {len(gb_files)}', flush=True)

def classify(sf):
    if not sf: return '_'
    return sf[-1]

stats = collections.defaultdict(lambda: [0, 0])
for fi, fp in enumerate(gb_files):
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
    if (fi+1) % 500 == 0:
        print(f'  已处理 {fi+1}/{len(gb_files)}', flush=True)

print('=== 6.5.1.2 ZC方向 × 触顶状态 核心模型（高波池，w=触底已区分） ===')
print(f'{"条件":<28}{"P3":>8}{"样本":>12}')
for (zc, state), (n, p3) in sorted(stats.items()):
    if n == 0: continue
    print(f'{zc}+{state:<22}{p3/n*100:>7.1f}%{n:>12,}')
