# -*- coding: utf-8 -*-
"""验证出管判定（只针对DXAB甲乙己）
用户定义：
1. 在管中时，未能维持管宽（连阴/阴阳阴），除非下一柱触顶，否则预示出管
2. 下破DJA后，只要未触哈都不考虑进跌管
3. 升连/阳阴阳预示跌管出管
4. DXAB变非甲乙己 = 出管
核心验证：出管信号后是否真的转跌（DXAB变非甲乙己 / 次日P3低）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col5=涨幅, col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串
agg = defaultdict(lambda: [0,0,0,0.0,0])  # [n, 次日P3, 5天P3, 均高幅, 3天出管率]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,13,26,30])
    df.columns = ['涨幅','DXAB','日ZA','次日高幅','上符串']
    for c in ['涨幅','日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA','涨幅'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触顶'] = df['上符串'].str.contains('A').astype(int)
    df['触哈'] = df['上符串'].str.contains('v').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)
    df['阳柱'] = (df['涨幅']>0).astype(int)
    df['阴柱'] = (df['涨幅']<0).astype(int)

    za = df['ZA正'].values
    ct = df['触顶'].values
    cha = df['触哈'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    yang = df['阳柱'].values
    yin = df['阴柱'].values
    n = len(df)

    # 出管信号验证（在管中：甲乙己 + ZA>0）
    for j in range(n-2):
        if not ab[j] or not za[j]: continue
        # 连阴（本柱阴柱 + 前柱阴柱）
        if yin[j]==1 and yin[j-1]==1:
            # 下一柱触顶 vs 未触顶
            if ct[j+1]==1:
                a = agg['连阴_下一柱触顶(维持管宽)']
            else:
                a = agg['连阴_下一柱未触顶(预示出管)']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3
        # 阴阳阴（本柱阴柱 + 前柱阳柱 + 前前柱阴柱）
        elif yin[j]==1 and yang[j-1]==1 and yin[j-2]==1:
            if ct[j+1]==1:
                a = agg['阴阳阴_下一柱触顶(维持管宽)']
            else:
                a = agg['阴阳阴_下一柱未触顶(预示出管)']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
            exit3 = 0
            for k in range(1,4):
                if j+k < n and not ab[j+k]:
                    exit3 = 1; break
            a[4]+=exit3

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('出管判定：连阴/阴阳阴 × 下一柱是否触顶（甲乙己，ZA>0在管中）')
print('='*70)
print(f"{'条件':<28}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}{'3天出管%':>10}")
for k in ['连阴_下一柱触顶(维持管宽)','连阴_下一柱未触顶(预示出管)',
          '阴阳阴_下一柱触顶(维持管宽)','阴阳阴_下一柱未触顶(预示出管)']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<28}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}{a[4]/a[0]*100:>10.2f}")