# -*- coding: utf-8 -*-
"""验证：为何研发新规则——即使升排/上破DJA/触顶仍会诱多
用户论点：即使满足旧规则入管条件（升排/上破DJA/触顶），仍会出现诱多（出管）
验证：甲乙己中，满足各入管条件后，3天出管率（诱多率）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col9=DXAB, col10=柱排, col13=日ZA, col26=次日高幅, col30=上符串
agg = defaultdict(lambda: [0,0,0,0.0,0])  # [n, 次日P3, 5天P3, 均高幅, 3天出管率]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,26,30])
    df.columns = ['DXAB','柱排','日ZA','次日高幅','上符串']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['柱排'] = df['柱排'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触顶'] = df['上符串'].str.contains('A').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)
    df['升排'] = df['柱排'].str.startswith('升').astype(int)

    za = df['ZA正'].values
    ct = df['触顶'].values
    ab = df['甲乙己'].values
    sp = df['升排'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    n = len(df)

    for j in range(n-2):
        if not ab[j]: continue
        # 各入管条件
        conds = {
            '基线_甲乙己': True,
            '上破DJA(DXZA>0)': za[j]==1,
            '升排': sp[j]==1,
            '触顶(上符串含A)': ct[j]==1,
            '上破DJA+升排': za[j]==1 and sp[j]==1,
            '上破DJA+触顶': za[j]==1 and ct[j]==1,
            '上破DJA+升排+触顶': za[j]==1 and sp[j]==1 and ct[j]==1,
        }
        for k, cond in conds.items():
            if cond:
                a = agg[k]
                a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
                exit3 = 0
                for m in range(1,4):
                    if j+m < n and not ab[j+m]:
                        exit3 = 1; break
                a[4]+=exit3

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('为何研发新规则：即使升排/上破DJA/触顶仍会诱多（甲乙己）')
print('='*70)
print(f"{'条件':<24}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}{'3天出管%(诱多)':>14}")
for k in ['基线_甲乙己','上破DJA(DXZA>0)','升排','触顶(上符串含A)',
          '上破DJA+升排','上破DJA+触顶','上破DJA+升排+触顶']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<24}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}{a[4]/a[0]*100:>14.2f}")