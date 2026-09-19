# -*- coding: utf-8 -*-
"""
阴阳镜面对称原则验证
========================================
验证用户提出的对称原则 + 发现新的对称原则

原则2: DXCD中 是否很可能再次站上DJC（次日/未来N天ZC转正率）
原则7: 阴区介入时机（DXZC<0时，等5/等6超跌反弹的P3）
对称10: 触底(上符串末位w)在阴区的介入价值

数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 8=DXCD, 9=DXAB护型, 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 44=日等型
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

agg_zhong = defaultdict(lambda: [0,0,0,0])  # DXCD -> [n,次日ZC转正,3天ZC转正,5天ZC转正]
agg_yin_deng = defaultdict(lambda: [0,0])   # DXZC<0×等型 -> [n,次日P3]
agg_yang_deng = defaultdict(lambda: [0,0])  # DXZC>0×等型 -> [n,次日P3]
agg_chudi = defaultdict(lambda: [0,0])      # 上符末位w -> [n,次日P3]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[8,9,13,14,26,30,44])
    df.columns = ['DXCD','DXAB','日ZA','日ZC','次日高幅','上符串','日等型']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['日等型'] = df['日等型'].astype(str)
    df['DXCD'] = df['DXCD'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['P3'] = (df['次日高幅'] >= 3).astype(int)
    df['ZC转正'] = (df['日ZC'] > 0).astype(int)
    df['3天ZC转正'] = df['ZC转正'].rolling(3, min_periods=1).max().shift(-2).fillna(0).astype(int)
    df['5天ZC转正'] = df['ZC转正'].rolling(5, min_periods=1).max().shift(-4).fillna(0).astype(int)
    # 原则2: DXCD中/下/忑 (DXZC<0) 未来ZC转正率
    for h in ['中','下','忑','忠','上','忐']:
        sub = df[df['DXCD']==h]
        a = agg_zhong[h]
        a[0]+=len(sub); a[1]+=sub['ZC转正'].sum(); a[2]+=sub['3天ZC转正'].sum(); a[3]+=sub['5天ZC转正'].sum()
    # 原则7: DXZC<0 × 日等型
    yin = df[df['日ZC']<0]
    for deng, grp in yin.groupby('日等型'):
        a = agg_yin_deng[deng]; a[0]+=len(grp); a[1]+=grp['P3'].sum()
    # 对照: DXZC>0 × 日等型
    yang = df[df['日ZC']>0]
    for deng, grp in yang.groupby('日等型'):
        a = agg_yang_deng[deng]; a[0]+=len(grp); a[1]+=grp['P3'].sum()
    # 对称10: 触底(上符末位w)
    chudi = df[df['上符串'].str.endswith('w')]
    agg_chudi['触底w'][0] += len(chudi)
    agg_chudi['触底w'][1] += chudi['P3'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('原则2: DXCD各护级 未来ZC转正率（验证"中反复站上DJC"）')
print('='*70)
print(f"{'DXCD':<6}{'样本':>10}{'次日转正%':>10}{'3天转正%':>10}{'5天转正%':>10}")
for h in ['上','忐','忠','中','下','忑']:
    n, c1, c3, c5 = agg_zhong[h]
    if n > 0:
        print(f"{h:<6}{n:>10}{c1/n*100:>10.2f}{c3/n*100:>10.2f}{c5/n*100:>10.2f}")

print('\n' + '='*70)
print('原则7: DXZC<0 × 日等型 次日P3（阴区介入时机）')
print('='*70)
rows = []
for deng, (n, p3) in agg_yin_deng.items():
    if n >= 1000:
        rows.append((deng, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'等型':<8}{'样本':>10}{'次日P3%':>10}")
for deng, n, p in rows:
    print(f"{deng:<8}{n:>10}{p:>10.2f}")

print('\n' + '='*70)
print('对照: DXZC>0 × 日等型 次日P3（阳区介入时机）')
print('='*70)
rows = []
for deng, (n, p3) in agg_yang_deng.items():
    if n >= 1000:
        rows.append((deng, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'等型':<8}{'样本':>10}{'次日P3%':>10}")
for deng, n, p in rows:
    print(f"{deng:<8}{n:>10}{p:>10.2f}")

print('\n' + '='*70)
print('对称10: 触底(上符末位w) 次日P3')
print('='*70)
n, p3 = agg_chudi['触底w']
print(f"触底w: n={n}, 次日P3={p3/n*100:.2f}%")
