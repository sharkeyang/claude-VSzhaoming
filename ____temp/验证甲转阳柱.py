# -*- coding: utf-8 -*-
"""
验证甲的特权：阴柱后转阳柱概率 + 首次回踩DJA反弹
========================================
假设3：甲的特权（DXAB刚正交）
- 0<DXAB≤4内出现阴柱，基本转阳柱（次日收阳概率）
- 首次回踩DJA后一般有反弹

磁盘CSV列序：5=涨幅, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 聚合1：key=(护型码, 持续天数, 当日阴阳) → [n, 次日收阳n, 次日冲高n]
agg1 = defaultdict(lambda: [0, 0, 0])
# 聚合2：key=(护型码, 是否首次回踩DJA) → [n, 次日冲高n]
# 首次回踩DJA = 当日日ZA=1（刚站上DJA）且前一日日ZA>1

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,13,14,26])
    df.columns = ['涨幅','DXAB','日ZA','日ZC','次日高幅']
    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df = df.dropna(subset=['DXAB','涨幅','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['持续'] = df['DXAB'].str.extract(r'([0-9]+)').astype(float)
    df['阴阳'] = df['涨幅'].apply(lambda x: '阳' if x > 0 else ('阴' if x < 0 else '平'))
    df['次日收阳'] = (df['涨幅'].shift(-1) > 0).astype(int)
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    # 只看 ZC>0
    df = df[df['日ZC'] > 0]
    # 只看甲（a）
    df = df[df['护型码'] == 'a']
    # 聚合1：持续1-4 × 阴阳
    df1 = df[df['持续'].between(1, 4)]
    for (持续, 阴阳), grp in df1.groupby(['持续','阴阳']):
        a = agg1[(持续, 阴阳)]
        a[0] += len(grp)
        a[1] += grp['次日收阳'].sum()
        a[2] += grp['冲高'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print('\n=== 甲 × DXAB持续天数 × 阴阳 次日收阳/冲高概率 (ZC>0) ===')
print(f"{'持续':<6}{'阴阳':<4}{'样本':>10}{'次日收阳%':>10}{'次日冲高%':>10}")
rows = []
for (持续, 阴阳), (n, 收阳n, 冲高n) in agg1.items():
    if n < 100:
        continue
    rows.append((持续, 阴阳, n, 收阳n/n*100, 冲高n/n*100))
rows.sort(key=lambda r: (r[0], r[1]))
for 持续, 阴阳, n, 收阳p, 冲高p in rows:
    print(f"{持续:<6}{阴阳:<4}{n:>10}{收阳p:>10.2f}{冲高p:>10.2f}")
