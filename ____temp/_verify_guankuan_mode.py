# -*- coding: utf-8 -*-
"""验证管中模式：巨宽/中宽/窄管（只针对DXAB甲乙己）
用户定义：
- 巨宽：连阳不断触顶推高顶部（上符串含A，连阳），垒升典型形态
- 中宽：维持固定管宽，阴阳交错或缓慢升连，也可能是垒升
- 窄管：大多数是十字星低波，没有有效的升排
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col5=涨幅, col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串, col43=顶型
agg = defaultdict(lambda: [0,0,0,0.0])

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
    df['触顶'] = df['上符串'].str.contains('A').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)
    df['阳柱'] = (df['涨幅']>0).astype(int)
    df['阴柱'] = (df['涨幅']<0).astype(int)
    df['低波'] = (df['涨幅'].abs()<1).astype(int)  # 十字星低波

    za = df['ZA正'].values
    ct = df['触顶'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    yang = df['阳柱'].values
    yin = df['阴柱'].values
    low = df['低波'].values
    n = len(df)

    # 管中模式：本柱ZA>0（在管中）且甲乙己
    for j in range(n-2):
        if not ab[j] or not za[j]: continue
        # 巨宽：本柱触顶 + 本柱阳柱 + 前柱阳柱（连阳触顶）
        if ct[j]==1 and yang[j]==1 and yang[j-1]==1:
            a = agg['巨宽_连阳触顶']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
        # 中宽：阴阳交错（本柱阴柱+前柱阳柱 或 本柱阳柱+前柱阴柱）
        elif (yang[j]==1 and yin[j-1]==1) or (yin[j]==1 and yang[j-1]==1):
            a = agg['中宽_阴阳交错']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
        # 窄管：低波（十字星）
        elif low[j]==1:
            a = agg['窄管_低波十字星']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]
        # 其他（缓慢升连等）
        else:
            a = agg['其他_缓慢升连']
            a[0]+=1; a[1]+=p3[j]; a[2]+=p5[j]; a[3]+=hf[j]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('管中模式：巨宽/中宽/窄管（甲乙己，ZA>0在管中）')
print('='*70)
print(f"{'模式':<20}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均':>8}")
for k in ['巨宽_连阳触顶','中宽_阴阳交错','窄管_低波十字星','其他_缓慢升连']:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<20}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>8.2f}")