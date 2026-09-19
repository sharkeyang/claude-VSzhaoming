# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\@VSwork\VS昭明计划VBA优化\_产出物\_工具')
from 随机抽样工具 import 加载市板映射, 是核心池

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
加载市板映射(r'D:\@VSwork\VS昭明计划VBA优化\____temp\市板映射.csv')
files = glob.glob(DATA_DIR + '/谕组日_*.csv')
gb_files = [f for f in files if 是核心池(f.split('谕组日_')[1].replace('.csv',''))]
print(f'高波池文件数: {len(gb_files)}', flush=True)

def 合顶天数(sf):
    """上符串末位往前连续 A 的个数"""
    if not sf: return 0
    cnt = 0
    for c in reversed(sf):
        if c == 'A': cnt += 1
        else: break
    return cnt

def 触顶次数5(sf):
    """5位上符串里 A 的个数"""
    if not sf: return 0
    return sf.count('A')

# 6.5.1.3: 合顶天数 × P3（高波池）
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
            sf = row[30].strip()
            hd = 合顶天数(sf)
            stats[hd][0] += 1
            if nxt >= 3:
                stats[hd][1] += 1
    if (fi+1) % 500 == 0:
        print(f'  已处理 {fi+1}/{len(gb_files)}', flush=True)

print('=== 6.5.1.3 合顶天数 × P3（高波池，w=触底已区分） ===')
print(f'{"合顶天数":<10}{"P3":>8}{"样本":>12}')
for hd in sorted(stats.keys()):
    n, p3 = stats[hd]
    if n == 0: continue
    print(f'{hd:<10}{p3/n*100:>7.1f}%{n:>12,}')
