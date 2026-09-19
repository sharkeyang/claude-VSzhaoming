# -*- coding: utf-8 -*-
"""验证用户新入管判定准则（完整版）
用户新准则（只针对DXAB甲乙己，不考虑DXZC）：
1. 入管：上破DXZA>0后第一次触哼，本柱和第二柱DXZA>0
2. 管中模式：巨宽(连阳触顶)/中宽(阴阳交错或缓慢升连)/窄管(十字星低波)
3. 出管：连阴/阴阳阴(除非下一柱触顶)；下破DJA后未触哈不进跌管；升连/阳阴阳预示跌管出管；DXAB变非甲乙己=出管

核心验证：新准则 vs 旧准则(DTZA>=3) 的 P≥3% 和 出管率(误判诱多)
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col5=涨幅, col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串, col43=顶型
agg = defaultdict(lambda: [0,0,0,0.0,0])  # [n, 次日P3, 5天P3, 均高幅, 出管率]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,13,26,30,43])
    df.columns = ['涨幅','DXAB','日ZA','次日高幅','上符串','顶型']
    for c in ['涨幅','日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df['顶型'] = df['顶型'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA','涨幅'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触哼'] = df['上符串'].str.contains('B').astype(int)
    df['触顶'] = df['上符串'].str.contains('A').astype(int)
    df['触哈'] = df['上符串'].str.contains('v').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)
    df['阳柱'] = (df['涨幅']>0).astype(int)
    df['阴柱'] = (df['涨幅']<0).astype(int)

    za = df['ZA正'].values
    ch = df['触哼'].values
    ct = df['触顶'].values
    cha = df['触哈'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    yang = df['阳柱'].values
    yin = df['阴柱'].values
    hx = df['护型'].values
    n = len(df)

    # 新准则入管：上破DXZA>0后第一次触哼 + 本柱和第二柱ZA>0
    # 简化：本柱触哼 + 本柱ZA>0 + 第二柱ZA>0（且本柱是甲乙己）
    # 出管率：入管后3天内DXAB变非甲乙己
    for j in range(n-2):
        if not ab[j]: continue
        # 新准则入管
        if ch[j]==1 and za[j]==1 and za[j+1]==1:
            a = agg['新准则_触哼入管']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            # 出管率：3天内变非甲乙己
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3
        # 旧准则 DTZA>=3
        if df['日ZA'].values[j] >= 3:
            a = agg['旧准则_DTZA>=3']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3
        # 基线甲乙己
        a = agg['基线_甲乙己']
        a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
        exit3 = 0
        for k in range(1,4):
            if j+k < n and not ab[j+k]:
                exit3 = 1; break
        a[4]+=exit3

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('入管判定：新准则(触哼) vs 旧准则(DTZA>=3)')
print('='*70)
print(f"{'条件':<22}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}{'3天出管%':>10}")
for k in ['基线_甲乙己','旧准则_DTZA>=3','新准则_触哼入管']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<22}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}{a[4]/a[0]*100:>10.2f}")