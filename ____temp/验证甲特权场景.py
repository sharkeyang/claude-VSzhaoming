# -*- coding: utf-8 -*-
"""
验证甲的特权：首次回踩DJA反弹 + 连阳后第一阴柱(vV)
========================================
假设3：甲的特权（DXAB刚正交）
- 首次回踩DJA后一般有反弹
- 优选连阳后第一个阴柱（vV）

磁盘CSV列序：5=涨幅, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 聚合：key=场景 → [n, 次日冲高n, 次日收阳n]
agg = defaultdict(lambda: [0, 0, 0])

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
    # 只看 ZC>0 且 甲（a）
    df = df[(df['日ZC'] > 0) & (df['护型码'] == 'a')]
    if df.empty:
        continue
    # 场景1：首次回踩DJA = 当日日ZA=1 且 前一日日ZA>1
    df['前日ZA'] = df['日ZA'].shift(1)
    df['首次回踩'] = (df['日ZA'] == 1) & (df['前日ZA'] > 1)
    # 场景2：连阳后第一阴柱 = 当日阴 且 前一日阳 且 前二日阳
    df['前日阴阳'] = df['阴阳'].shift(1)
    df['前二日阴阳'] = df['阴阳'].shift(2)
    df['连阳后首阴'] = (df['阴阳'] == '阴') & (df['前日阴阳'] == '阳') & (df['前二日阴阳'] == '阳')
    # 场景3：刚正交阴柱 = 持续1-2 且 阴
    df['刚正交阴'] = (df['持续'].between(1, 2)) & (df['阴阳'] == '阴')

    for 场景, mask in [('首次回踩DJA', df['首次回踩']), ('连阳后首阴vV', df['连阳后首阴']), ('刚正交阴柱', df['刚正交阴'])]:
        sub = df[mask]
        if sub.empty:
            continue
        a = agg[场景]
        a[0] += len(sub)
        a[1] += sub['冲高'].sum()
        a[2] += sub['次日收阳'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print('\n=== 甲的特权场景验证 (ZC>0) ===')
print(f"{'场景':<16}{'样本':>10}{'次日冲高%':>10}{'次日收阳%':>10}")
for 场景, (n, 冲高n, 收阳n) in agg.items():
    if n < 100:
        continue
    print(f"{场景:<16}{n:>10}{冲高n/n*100:>10.2f}{收阳n/n*100:>10.2f}")
