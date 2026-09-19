# -*- coding: utf-8 -*-
"""问题1-3分析
Q1: 区分乙/戊的次日高幅阈值概率（含所有护型，乙戊单独划分）
Q2: 三连跌是否都会导致DXZA<0（深入验证14.71%）
Q3: 镜面对称原则检查（DXZC>0甲乙己 vs DXZC<0丙丁戊）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# Q1: 护型 -> [n, 次日高幅>=0, >=1, >=2, >=3, >=5, 次日均高幅]
q1 = defaultdict(lambda: [0,0,0,0,0,0,0.0])
# Q2: 三连跌段内DXZA<0率 + 三连跌后DXZA
q2_3lian_za = defaultdict(lambda: [0,0])   # 三连跌段内柱 -> [n, DXZA<0]
q2_3lian_end = defaultdict(lambda: [0,0])  # 三连跌段末柱 -> [n, DXZA<0]
q2_zc0_3lian = [0,0]  # DXZC>0 且处于三连跌及以上 -> [n, DXZA<0]
q2_zc0_all = [0,0]    # DXZC>0 全部 -> [n, DXZA<0]
# Q3: 镜面对称
q3 = defaultdict(lambda: [0,0,0,0])  # (ZC符号, 护型) -> [n, 次日P3, 5天P3, 次日均高幅]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,13,14,26])
    df.columns = ['涨幅','DXAB','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','日ZA','日ZC'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['护型'] = df['护型码'].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['P5'] = (df['次日高幅']>=5).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)
    df['ZC正'] = (df['日ZC']>0).astype(int)
    df['ZC负'] = (df['日ZC']<0).astype(int)

    # Q1: 全护型次日高幅阈值
    for hx, grp in df.groupby('护型'):
        a = q1[hx]
        a[0] += len(grp)
        a[1] += (grp['次日高幅']>=0).sum()
        a[2] += (grp['次日高幅']>=1).sum()
        a[3] += (grp['次日高幅']>=2).sum()
        a[4] += grp['P3'].sum()
        a[5] += grp['P5'].sum()
        a[6] += grp['次日高幅'].sum()

    # Q2: 三连跌段分析（涨幅<0连续3天及以上）
    zf = df['涨幅'].values
    za = df['日ZA'].values
    zc = df['日ZC'].values
    n = len(zf)
    j = 0
    while j < n:
        if zf[j] < 0:
            k = j
            while k < n and zf[k] < 0:
                k += 1
            length = k - j
            if length >= 3:
                # 段内每柱
                for m in range(j, k):
                    q2_3lian_za['段内'][0] += 1
                    if za[m] < 0: q2_3lian_za['段内'][1] += 1
                    if zc[m] > 0:
                        q2_zc0_3lian[0] += 1
                        if za[m] < 0: q2_zc0_3lian[1] += 1
                # 段末柱
                q2_3lian_end['段末'][0] += 1
                if za[k-1] < 0: q2_3lian_end['段末'][1] += 1
            j = k
        else:
            j += 1
    # Q2: DXZC>0 全部
    zc0_mask = zc > 0
    q2_zc0_all[0] += zc0_mask.sum()
    q2_zc0_all[1] += (za[zc0_mask] < 0).sum()

    # Q3: 镜面对称
    for zc_sign, zc_mask in [('ZC>0', df['ZC正']==1), ('ZC<0', df['ZC负']==1)]:
        sub = df[zc_mask]
        for hx, grp in sub.groupby('护型'):
            key = (zc_sign, hx)
            a = q3[key]
            a[0] += len(grp)
            a[1] += grp['P3'].sum()
            a[2] += grp['5天P3'].sum()
            a[3] += grp['次日高幅'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q1: 各护型 次日高幅阈值概率（含乙戊单独划分）')
print('='*70)
print(f"{'护型':<6}{'样本':>10}{'≥0%':>8}{'≥1%':>8}{'≥2%':>8}{'≥3%':>8}{'≥5%':>8}{'次日均高幅':>10}")
for hx in ['甲','乙','丙','丁','戊','己']:
    a = q1[hx]
    if a[0] > 0:
        print(f"{hx:<6}{a[0]:>10}{a[1]/a[0]*100:>8.2f}{a[2]/a[0]*100:>8.2f}{a[3]/a[0]*100:>8.2f}{a[4]/a[0]*100:>8.2f}{a[5]/a[0]*100:>8.2f}{a[6]/a[0]:>10.2f}")

print('\n' + '='*70)
print('Q2: 三连跌是否导致DXZA<0')
print('='*70)
n, neg = q2_3lian_za['段内']
print(f'三连跌段内所有柱: n={n}, DXZA<0率={neg/n*100:.2f}%')
n, neg = q2_3lian_end['段末']
print(f'三连跌段末柱: n={n}, DXZA<0率={neg/n*100:.2f}%')
n, neg = q2_zc0_3lian
print(f'DXZC>0且处于三连跌及以上: n={n}, DXZA<0率={neg/n*100:.2f}%')
n, neg = q2_zc0_all
print(f'DXZC>0全部: n={n}, DXZA<0率={neg/n*100:.2f}%')
print(f'DXZC>0且处于三连跌及以上占比: {n/q2_zc0_all[0]*100:.2f}%')

print('\n' + '='*70)
print('Q3: 镜面对称（ZC>0 vs ZC<0 各护型）')
print('='*70)
for zc_sign in ['ZC>0','ZC<0']:
    print(f'\n--- {zc_sign} ---')
    print(f"{'护型':<6}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均高幅':>10}")
    for hx in ['甲','乙','丙','丁','戊','己']:
        a = q3[(zc_sign, hx)]
        if a[0] > 0:
            print(f"{hx:<6}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>10.2f}")
