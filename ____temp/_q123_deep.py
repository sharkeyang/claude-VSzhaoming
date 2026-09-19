# -*- coding: utf-8 -*-
"""问题1-3深入
Q1: 各护型次日高幅阈值（DXZC>0口径 + 乙戊ZA拆分 + 5天口径）
Q2: 三连跌深入（按段内位置/段长度/护型）
Q3: 镜面对称（护型构成 + 甲乙己在ZC>0是否需要退出）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def hx_split(code, za):
    h = HX.get(code, '')
    if h == '乙':
        return '乙ZA>0' if za > 0 else '乙ZA<0'
    if h == '戊':
        return '戊ZA>0' if za > 0 else '戊ZA<0'
    return h

# Q1: (ZC口径, 护型) -> [n, >=0,>=1,>=2,>=3,>=5, 5天>=3, 5天>=5, 均高幅]
q1 = defaultdict(lambda: [0,0,0,0,0,0,0,0,0.0])
# Q2: 段内位置 -> [n, DXZA<0]；护型->[n, DXZA<0]
q2_pos = defaultdict(lambda: [0,0])
q2_hx = defaultdict(lambda: [0,0])
# Q3: (ZC符号, 护型) -> [n, P3, 5天P3, 均高幅]
q3 = defaultdict(lambda: [0,0,0,0.0])
# Q3: 甲乙己ZC>0 次日维持
q3_ab_keep = defaultdict(lambda: [0,0])
# 护型构成 (ZC符号) -> 护型 -> n
q3_comp = defaultdict(lambda: defaultdict(int))

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
    df['护型拆分'] = [hx_split(c, z) for c, z in zip(df['护型码'], df['日ZA'])]
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['P5'] = (df['次日高幅']>=5).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['5天P5'] = (df['未来5天高幅']>=5).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)
    df['ZC正'] = (df['日ZC']>0).astype(int)
    df['ZC负'] = (df['日ZC']<0).astype(int)
    df['护型码_次日'] = df['护型码'].shift(-1)

    # Q1: DXZC>0 各护型（拆分乙戊ZA）
    zc0 = df[df['ZC正']==1]
    for hs, grp in zc0.groupby('护型拆分'):
        a = q1[('ZC>0', hs)]
        a[0] += len(grp)
        a[1] += (grp['次日高幅']>=0).sum()
        a[2] += (grp['次日高幅']>=1).sum()
        a[3] += (grp['次日高幅']>=2).sum()
        a[4] += grp['P3'].sum()
        a[5] += grp['P5'].sum()
        a[6] += grp['5天P3'].sum()
        a[7] += grp['5天P5'].sum()
        a[8] += grp['次日高幅'].sum()
    # Q1对照: 全样本各护型
    for hs, grp in df.groupby('护型拆分'):
        a = q1[('全样本', hs)]
        a[0] += len(grp)
        a[1] += (grp['次日高幅']>=0).sum()
        a[2] += (grp['次日高幅']>=1).sum()
        a[3] += (grp['次日高幅']>=2).sum()
        a[4] += grp['P3'].sum()
        a[5] += grp['P5'].sum()
        a[6] += grp['5天P3'].sum()
        a[7] += grp['5天P5'].sum()
        a[8] += grp['次日高幅'].sum()

    # Q2: 三连跌段内位置分析
    zf = df['涨幅'].values
    za = df['日ZA'].values
    hx = df['护型'].values
    n = len(zf)
    j = 0
    while j < n:
        if zf[j] < 0:
            k = j
            while k < n and zf[k] < 0:
                k += 1
            length = k - j
            if length >= 3:
                for m in range(j, k):
                    pos = m - j + 1
                    key = f'第{pos}柱/段长{length}'
                    q2_pos[key][0] += 1
                    if za[m] < 0: q2_pos[key][1] += 1
                    q2_hx[hx[m]][0] += 1
                    if za[m] < 0: q2_hx[hx[m]][1] += 1
            j = k
        else:
            j += 1

    # Q3: 护型构成
    for sign, mask, key in [('ZC>0', df['ZC正']==1, 'ZC>0'), ('ZC<0', df['ZC负']==1, 'ZC<0')]:
        sub = df[mask]
        for hx_v, grp in sub.groupby('护型'):
            q3_comp[key][hx_v] += len(grp)

    # Q3: ZC>0时甲乙己 P3 + 次日转移
    zc0_ab = df[(df['ZC正']==1) & (df['护型'].isin(['甲','乙','己']))]
    for hx_v, grp in zc0_ab.groupby('护型'):
        a = q3[('ZC>0', hx_v)]
        a[0] += len(grp)
        a[1] += grp['P3'].sum()
        a[2] += grp['5天P3'].sum()
        a[3] += grp['次日高幅'].sum()
        next_hx = grp['护型码_次日'].map(HX)
        still_ab = next_hx.isin(['甲','乙','己']).sum()
        q3_ab_keep[hx_v][0] += len(grp)
        q3_ab_keep[hx_v][1] += still_ab

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q1: 次日高幅阈值概率（DXZC>0 口径，乙戊拆分ZA）')
print('='*70)
print(f"{'护型':<10}{'样本':>10}{'>=0%':>7}{'>=1%':>7}{'>=2%':>7}{'>=3%':>7}{'>=5%':>7}{'5天>=3%':>8}{'5天>=5%':>8}{'次日均':>7}")
for hs in ['甲','乙ZA>0','乙ZA<0','丙','丁','戊ZA>0','戊ZA<0','己']:
    a = q1[('ZC>0', hs)]
    if a[0] > 0:
        print(f"{hs:<10}{a[0]:>10}{a[1]/a[0]*100:>7.2f}{a[2]/a[0]*100:>7.2f}{a[3]/a[0]*100:>7.2f}{a[4]/a[0]*100:>7.2f}{a[5]/a[0]*100:>7.2f}{a[6]/a[0]*100:>8.2f}{a[7]/a[0]*100:>8.2f}{a[8]/a[0]:>7.2f}")

print('\n' + '='*70)
print('Q1对照: 全样本口径（不分ZC）')
print('='*70)
print(f"{'护型':<10}{'样本':>10}{'>=0%':>7}{'>=1%':>7}{'>=2%':>7}{'>=3%':>7}{'>=5%':>7}{'5天>=3%':>8}{'5天>=5%':>8}{'次日均':>7}")
for hs in ['甲','乙ZA>0','乙ZA<0','丙','丁','戊ZA>0','戊ZA<0','己']:
    a = q1[('全样本', hs)]
    if a[0] > 0:
        print(f"{hs:<10}{a[0]:>10}{a[1]/a[0]*100:>7.2f}{a[2]/a[0]*100:>7.2f}{a[3]/a[0]*100:>7.2f}{a[4]/a[0]*100:>7.2f}{a[5]/a[0]*100:>7.2f}{a[6]/a[0]*100:>8.2f}{a[7]/a[0]*100:>8.2f}{a[8]/a[0]:>7.2f}")

print('\n' + '='*70)
print('Q2: 三连跌段内位置 × DXZA<0率')
print('='*70)
print(f"{'位置/段长':<16}{'样本':>10}{'DXZA<0%':>10}")
for pos in [1,2,3,4,5]:
    keys = [k for k in q2_pos if k.startswith(f'第{pos}柱')]
    total_n = sum(q2_pos[k][0] for k in keys)
    total_neg = sum(q2_pos[k][1] for k in keys)
    if total_n > 0:
        print(f"{f'第{pos}柱':<16}{total_n:>10}{total_neg/total_n*100:>10.2f}")
print()
print(f"{'位置×段长':<16}{'样本':>10}{'DXZA<0%':>10}")
for length in [3,4,5,6,7,8]:
    keys = [k for k in q2_pos if f'/段长{length}' in k]
    if not keys: continue
    for k in sorted(keys, key=lambda x: int(x.split('第')[1].split('柱')[0])):
        n, neg = q2_pos[k]
        if n > 0:
            print(f"{k:<16}{n:>10}{neg/n*100:>10.2f}")

print('\n' + '='*70)
print('Q2: 三连跌段内护型 × DXZA<0率')
print('='*70)
print(f"{'护型':<6}{'样本':>10}{'DXZA<0%':>10}")
for hx in ['甲','乙','丙','丁','戊','己']:
    n, neg = q2_hx[hx]
    if n > 0:
        print(f"{hx:<6}{n:>10}{neg/n*100:>10.2f}")

print('\n' + '='*70)
print('Q3: 护型构成（按ZC符号）')
print('='*70)
for sign in ['ZC>0','ZC<0']:
    comp = q3_comp[sign]
    total = sum(comp.values())
    print(f'\n{sign}: 总样本 {total}')
    for hx in ['甲','乙','丙','丁','戊','己']:
        c = comp.get(hx, 0)
        print(f'  {hx}: {c} ({c/total*100:.2f}%)')

print('\n' + '='*70)
print('Q3: ZC>0 时 甲乙己 P3 + 次日维持率')
print('='*70)
print(f"{'护型':<6}{'样本':>10}{'次日P3%':>10}{'5天P3%':>10}{'次日均高幅':>10}{'次日仍甲乙己%':>14}")
for hx in ['甲','乙','己']:
    a = q3[('ZC>0', hx)]
    k = q3_ab_keep[hx]
    if a[0] > 0:
        print(f"{hx:<6}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]:>10.2f}{k[1]/k[0]*100:>14.2f}")
