# -*- coding: utf-8 -*-
"""验证用户数学理论框架：DXCD六类的方向性
用户论断：
1. 上/忐（P>EMA26且P>EMA60）= 升势（两条均线都支持）
2. 下/忑（P<EMA26且P<EMA60）= 跌势
3. 中/忠（一条之上一条之下）= 待定
   用户判断：中更可能升势，忠更可能跌势
关键验证点：
- 上 vs 忐 的差异（均线排列方向不同：上=多头，忐=空头）
- 下 vs 忑 的差异
- 中 vs 忠 的方向（用户判断中升忠跌，数学直觉中跌忠升）
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# DXCD在col8，日ZA在col13，日ZC在col14，次日高幅在col26
# 验证：DXCD六类 × 次日P3 / 次日均高幅 / 次日ZC>0率 / 次日ZA>0率
agg = defaultdict(lambda: [0,0,0.0,0,0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[8,13,14,26])
    df.columns = ['DXCD','日ZA','日ZC','次日高幅']
    for c in ['日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXCD'] = df['DXCD'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA','日ZC'])
    if df.empty: continue
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['ZC正'] = (df['日ZC']>0).astype(int)
    df['ZA正'] = (df['日ZA']>0).astype(int)
    # 次日ZC/ZA（shift -1）
    df['次日ZC'] = df['日ZC'].shift(-1)
    df['次日ZA'] = df['日ZA'].shift(-1)
    df['次日ZC正'] = (df['次日ZC']>0).astype(int)
    df['次日ZA正'] = (df['次日ZA']>0).astype(int)

    for cd, grp in df.groupby('DXCD'):
        a = agg[cd]
        a[0] += len(grp)
        a[1] += grp['P3'].sum()
        a[2] += grp['次日高幅'].sum()
        a[3] += grp['次日ZC正'].sum()
        a[4] += grp['次日ZA正'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('DXCD六类 × 次日方向性')
print('='*70)
print(f"{'DXCD':<6}{'样本':>10}{'次日P3%':>10}{'次日均高幅':>10}{'次日ZC>0%':>10}{'次日ZA>0%':>10}")
for cd in ['上','中','下','忐','忠','忑']:
    a = agg[cd]
    if a[0] > 0:
        print(f"{cd:<6}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]:>10.2f}{a[3]/a[0]*100:>10.2f}{a[4]/a[0]*100:>10.2f}")