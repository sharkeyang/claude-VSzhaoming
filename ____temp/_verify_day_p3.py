# -*- coding: utf-8 -*-
"""验证折中方案：入管后逐日P3，特别是DJB出管多容忍的区间(第6-8天)
入管：触哼+ZA>0+第二柱ZA>0
验证：入管后第1-10天逐日P3，看多容忍的区间是否有价值
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

# 列：col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串
# 入管后第k天P3（k=1..10）
day_p3 = defaultdict(lambda: [0,0])  # day -> [n, P3]
# 入管后第k天，是否仍为甲乙己(在管)
day_ab = defaultdict(lambda: [0,0])  # day -> [n, 仍甲乙己]

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
    df['ZA正'] = (df['日ZA']>0).astype(int)
    df['触哼'] = df['上符串'].str.contains('B').astype(int)
    df['甲乙己'] = df['护型'].isin(['甲','乙','己']).astype(int)

    za = df['ZA正'].values
    ch = df['触哼'].values
    ab = df['甲乙己'].values
    p3 = df['P3'].values
    n = len(df)

    for j in range(n-2):
        if ch[j]==1 and za[j]==1 and za[j+1]==1:
            for k in range(1, 11):
                if j+k < n:
                    day_p3[k][0]+=1; day_p3[k][1]+=p3[j+k]
                    day_ab[k][0]+=1; day_ab[k][1]+=ab[j+k]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('入管后逐日P3 + 仍为甲乙己比例（折中方案）')
print('='*70)
print(f"{'入管后第k天':<12}{'样本':>10}{'P3%':>10}{'仍甲乙己%':>10}")
for k in range(1, 11):
    a = day_p3[k]
    b = day_ab[k]
    if a[0] > 0:
        print(f"{k:<12}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{b[1]/b[0]*100:>10.2f}")