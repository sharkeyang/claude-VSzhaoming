# -*- coding: utf-8 -*-
"""验证管宽哼JA>60 案例的市场分布（bj北交所 vs sh/sz沪深）
管宽哼JA = (最近5日最高价/EMA5 - 1)*100
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))

# 按市场前缀统计 >60 案例
market_gt60 = defaultdict(int)
market_total = defaultdict(int)
for fp in files:
    base = os.path.basename(fp)
    # 文件名如 谕组日_bj920000.csv / 谕组日_sh600000.csv / 谕组日_sz000001.csv
    mkt = base.replace('谕组日_','').replace('.csv','')[:2]
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 31: continue
            try:
                gk = row[23].strip()
                if gk == '': continue
                gkv = float(gk)
            except: continue
            market_total[mkt] += 1
            if gkv > 60:
                market_gt60[mkt] += 1

print('=== 管宽哼JA>60 案例的市场分布 ===')
for mkt in sorted(market_total.keys()):
    t = market_total[mkt]
    g = market_gt60[mkt]
    print(f'{mkt}: 管宽哼JA有值={t}, >60={g} ({g/t*100:.3f}%)')
