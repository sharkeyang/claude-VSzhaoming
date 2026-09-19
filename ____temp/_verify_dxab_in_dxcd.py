# -*- coding: utf-8 -*-
"""验证用户DXAB分析：DXCD各区域内DXAB的分布与方向性
用户论断：
1. 上/忐 + DXAB=甲乙己 = 优选；其他护型仍属升势非优选
2. 下/忑 + DXAB=丙丁戊 = 实现跌势主要部分；其他仍属跌势
3. 中 + DXAB=丙丁戊 = 需等待变非丙丁戊，但中更可能升势
4. 忠 + DXAB=甲乙己 = 优选，但忠更可能跌势
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# (DXCD, DXAB大类) -> [n, 次日P3, 次日ZC>0, 次日ZA>0]
agg = defaultdict(lambda: [0,0,0,0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[8,9,13,14,26])
    df.columns = ['DXCD','DXAB','日ZA','日ZC','次日高幅']
    for c in ['日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXCD'] = df['DXCD'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA','日ZC'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['护型'] = df['护型码'].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['次日ZC'] = df['日ZC'].shift(-1)
    df['次日ZC正'] = (df['次日ZC']>0).astype(int)

    for (cd, hx), grp in df.groupby(['DXCD','护型']):
        a = agg[(cd, hx)]
        a[0] += len(grp)
        a[1] += grp['P3'].sum()
        a[2] += grp['次日ZC正'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('DXCD × DXAB护型 × 次日方向性')
print('='*70)
for cd in ['上','中','下','忐','忠','忑']:
    print(f'\n--- DXCD={cd} ---')
    print(f"{'护型':<6}{'样本':>10}{'次日P3%':>10}{'次日ZC>0%':>10}")
    for hx in ['甲','乙','丙','丁','戊','己']:
        a = agg[(cd, hx)]
        if a[0] > 0:
            print(f"{hx:<6}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}")