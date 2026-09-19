# -*- coding: utf-8 -*-
"""验证用户新入管思路：用DJB(EMA12)作为管边界
用户思路：
1. 入管：变为甲乙己(DXZB>0)后，首先触哼就开始判断是否入管
2. 在管：即使下破DXZA多柱(跌破DJA)，只要还是甲乙己(没跌破DJB)，仍在管
3. 出管：下破DJB(变为丙丁戊，DXZB<0)才判断出管

对比：之前准则(触哼入管，DJA边界) vs 新思路(DJB边界)
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串
agg = defaultdict(lambda: [0,0,0,0.0,0])  # [n, 次日P3, 5天P3, 均高幅, 3天出管率]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,26,30])
    df.columns = ['DXAB','日ZA','次日高幅','上符串']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触哼'] = df['上符串'].str.contains('B').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)

    za = df['ZA正'].values
    ch = df['触哼'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    n = len(df)

    # 新思路入管：变为甲乙己后第一次触哼（本柱甲乙己+触哼，前柱非甲乙己或前柱非触哼）
    # 简化：本柱甲乙己+触哼（且前柱非甲乙己，即刚变为甲乙己）
    for j in range(n-2):
        # 新思路：本柱甲乙己+触哼（刚变为甲乙己：前柱非甲乙己）
        if ab[j]==1 and ch[j]==1 and (j==0 or not ab[j-1]):
            a = agg['新思路_变甲乙己后触哼入管']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3
        # 新思路变体：本柱甲乙己+触哼（不限前柱）
        if ab[j]==1 and ch[j]==1:
            a = agg['新思路_甲乙己+触哼(不限前柱)']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3
        # 之前准则：触哼+本柱ZA>0+第二柱ZA>0
        if ch[j]==1 and za[j]==1 and za[j+1]==1:
            a = agg['旧思路_触哼+ZA>0+第二柱ZA>0']
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
print('新思路(DJB边界) vs 旧思路(DJA边界)')
print('='*70)
print(f"{'条件':<28}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}{'3天出管%':>10}")
for k in ['基线_甲乙己','旧思路_触哼+ZA>0+第二柱ZA>0','新思路_甲乙己+触哼(不限前柱)','新思路_变甲乙己后触哼入管']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<28}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}{a[4]/a[0]*100:>10.2f}")