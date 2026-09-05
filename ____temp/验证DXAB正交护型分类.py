# -*- coding: utf-8 -*-
"""
验证DXAB正交护型分类假设（全量增量聚合）
========================================
假设1：DXAB正交护型分类
- 可能负转正：己、戊(DXZA>0)
- 正交：甲、乙(DXZA>0)、乙(DXZA<0)
- 可能正转负：戊
- 无需持有：丁、戊(DXZA<0)

假设2：分类对DXZC>0更有效，DXZC<0视情况而定

输出：各护型×日ZA正负×日ZC正负 的次日冲高(≥3%)概率
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = glob.glob(DATA_DIR + '谕组日_*.csv')
print(f'共 {len(files)} 个文件')

# 护型码 → 中文
护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

# 聚合器：key=(护型码, 日ZA正负, 日ZC正负) → [n, 冲高n, 涨幅和]
agg = defaultdict(lambda: [0, 0, 0.0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','日ZA','日ZC','次日高幅','涨幅'])
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df = df.dropna(subset=['DXAB','日ZA','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['ZA正负'] = df['日ZA'].apply(lambda x: 'ZA>0' if x > 0 else ('ZA=0' if x == 0 else 'ZA<0'))
    df['ZC正负'] = df['日ZC'].apply(lambda x: 'ZC>0' if x > 0 else ('ZC=0' if x == 0 else 'ZC<0'))
    df['冲高'] = (df['次日高幅'] >= 3).astype(int)
    for (护型码, za, zc), grp in df.groupby(['护型码','ZA正负','ZC正负']):
        a = agg[(护型码, za, zc)]
        a[0] += len(grp)
        a[1] += grp['冲高'].sum()
        a[2] += grp['涨幅'].sum()
    if (i+1) % 1000 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print('\n=== 各护型 × 日ZA正负 × 日ZC正负 次日冲高(≥3%)概率 ===')
print(f"{'护型':<4}{'ZA':<6}{'ZC':<6}{'样本':>10}{'冲高%':>8}{'均涨%':>8}")
rows = []
for (护型码, za, zc), (n, 冲高n, 涨和) in agg.items():
    if n < 500:
        continue
    护型 = 护型映射.get(护型码, 护型码)
    rows.append((护型, za, zc, n, 冲高n/n*100, 涨和/n*100))
rows.sort(key=lambda r: (r[0], r[1], r[2]))
for 护型, za, zc, n, 冲高p, 均涨 in rows:
    print(f"{护型:<4}{za:<6}{zc:<6}{n:>10}{冲高p:>8.2f}{均涨:>8.2f}")
