# -*- coding: utf-8 -*-
"""深入验证：下破DXZA多柱但仍为甲乙己(没跌破DJB)是否仍在管
用户思路：即使下破DXZA多柱(跌破DJA)，只要还是甲乙己(没跌破DJB)，仍在管
验证：甲乙己中，按DXZA状态分组，P3如何？
- DXZA>0（在DJA之上）
- DXZA<0但甲乙己（下破DJA但仍为甲乙己，没跌破DJB）
- 按下破DXZA柱数分组（DXZA=-1/-2/-3...）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col9=DXAB, col13=日ZA, col26=次日高幅
agg = defaultdict(lambda: [0,0,0,0.0])  # [n, 次日P3, 5天P3, 均高幅]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,26])
    df.columns = ['DXAB','日ZA','次日高幅']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)

    za = df['日ZA'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    n = len(df)

    for j in range(n-2):
        if not ab[j]: continue  # 只针对甲乙己
        z = za[j]
        if z > 0:
            k = '甲乙己_DXZA>0(在DJA之上)'
        elif z == -1:
            k = '甲乙己_DXZA=-1(下破1柱)'
        elif z == -2:
            k = '甲乙己_DXZA=-2(下破2柱)'
        elif z <= -3:
            k = '甲乙己_DXZA<=-3(下破3柱+)'
        else:
            k = '甲乙己_DXZA=0'
        a = agg[k]
        a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('甲乙己中，下破DXZA多柱但仍为甲乙己(没跌破DJB)的P3')
print('='*70)
print(f"{'条件':<32}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}")
for k in ['甲乙己_DXZA>0(在DJA之上)','甲乙己_DXZA=0','甲乙己_DXZA=-1(下破1柱)',
          '甲乙己_DXZA=-2(下破2柱)','甲乙己_DXZA<=-3(下破3柱+)']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<32}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}")