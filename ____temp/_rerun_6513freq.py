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

def 今天触顶(sf):
    return bool(sf) and sf[-1] == 'A'

def 昨天触顶(sf):
    return len(sf) >= 2 and sf[-2] == 'A'

# 统计
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
            today = 今天触顶(sf)
            yest = 昨天触顶(sf)
            # 触顶频率
            if not today:
                stats['未触顶'][0] += 1
                if nxt >= 3: stats['未触顶'][1] += 1
            else:
                stats['触顶'][0] += 1
                if nxt >= 3: stats['触顶'][1] += 1
                if cnt5 >= 3:
                    stats['5天>=3次'][0] += 1
                    if nxt >= 3: stats['5天>=3次'][1] += 1
                if cnt5 >= 4:
                    stats['5天>=4次'][0] += 1
                    if nxt >= 3: stats['5天>=4次'][1] += 1
                if cnt5 == 5:
                    stats['5天全触顶'][0] += 1
                    if nxt >= 3: stats['5天全触顶'][1] += 1
                # 连续 vs 中断
                if yest:
                    stats['连续触顶'][0] += 1
                    if nxt >= 3: stats['连续触顶'][1] += 1
                else:
                    stats['中断后触顶'][0] += 1
                    if nxt >= 3: stats['中断后触顶'][1] += 1

print('=== 6.5.1.3 触顶频率（高波池，w=触底已区分） ===')
print(f'{"条件":<16}{"P3":>8}{"样本":>12}')
for k in ['未触顶','触顶','5天>=3次','5天>=4次','5天全触顶','连续触顶','中断后触顶']:
    n, p3 = stats[k]
    if n == 0: continue
    print(f'{k:<16}{p3/n*100:>7.1f}%{n:>12,}')
