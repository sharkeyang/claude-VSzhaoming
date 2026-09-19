# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\@VSwork\VS昭明计划VBA优化\_产出物\_工具')
from 随机抽样工具 import 加载市板映射, 是核心池

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
加载市板映射(r'D:\@VSwork\VS昭明计划VBA优化\____temp\市板映射.csv')
files = glob.glob(DATA_DIR + '/谕组日_*.csv')
gb_files = [f for f in files if 是核心池(f.split('谕组日_')[1].replace('.csv',''))]

def 触顶次数5(sf):
    if not sf: return 0
    return sf.count('A')

stats = collections.defaultdict(lambda: [0, 0])
for fp in gb_files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 31: continue
            try:
                zc = int(row[14])
                nxt = float(row[26])
            except:
                continue
            if zc <= 0: continue
            sf = row[30].strip()
            cnt5 = 触顶次数5(sf)
            today = bool(sf) and sf[-1] == 'A'
            if today and cnt5 == 1:
                stats['5天仅1次'][0] += 1
                if nxt >= 3: stats['5天仅1次'][1] += 1

print('=== 6.5.1.3 震荡偶尔触顶(5天仅1次) ===')
for k, (n, p3) in stats.items():
    print(f'{k}: P3={p3/n*100:.1f}% n={n:,}')
