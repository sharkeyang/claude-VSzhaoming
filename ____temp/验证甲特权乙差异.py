# -*- coding: utf-8 -*-
"""
验证甲的特权与乙的差异（聚焦持续天数1-8）
========================================
假设3：甲的特权（DXAB刚正交）
- 0<DXAB≤4内出现阴柱，基本转阳柱
- 优选连阳后第一个阴柱（vV）
- 第一次回踩DJA后一般有反弹

假设4：乙的差异（再次突破DXZA）
- 没有DXAB由负转正的特权
- 必须形成突破回踩、启动结构

磁盘CSV列序：5=涨幅, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 聚合：key=(护型码, DXAB持续天数, 当日阴阳) → [n, 次日冲高n]
agg = defaultdict(lambda: [0, 0])

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
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    # 只看 ZC>0（假设2：更有效）
    df = df[df['日ZC'] > 0]
    # 只看持续天数 1-8
    df = df[df['持续'].between(1, 8)]
    for (护型码, 持续, 阴阳), grp in df.groupby(['护型码','持续','阴阳']):
        a = agg[(护型码, 持续, 阴阳)]
        a[0] += len(grp)
        a[1] += grp['冲高'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

print('\n=== 甲/乙 × DXAB持续天数 × 阴阳 次日冲高(≥3%)概率 (ZC>0, 持续1-8) ===')
print(f"{'护型':<4}{'持续':<6}{'阴阳':<4}{'样本':>10}{'冲高%':>8}")
rows = []
for (护型码, 持续, 阴阳), (n, 冲高n) in agg.items():
    if n < 100:
        continue
    护型 = 护型映射.get(护型码, 护型码)
    if 护型 not in ('甲','乙'):
        continue
    rows.append((护型, 持续, 阴阳, n, 冲高n/n*100))
rows.sort(key=lambda r: (r[0], r[1], r[2]))
for 护型, 持续, 阴阳, n, 冲高p in rows:
    print(f"{护型:<4}{持续:<6}{阴阳:<4}{n:>10}{冲高p:>8.2f}")
