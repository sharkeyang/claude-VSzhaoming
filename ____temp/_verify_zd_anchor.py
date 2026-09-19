# -*- coding: utf-8 -*-
"""验证用户理论：中升忠跌（用次日DXCD判断次日ZD>0）
次日ZD>0 = 次日DXCD∈{上,中,忐}（明确P>EMA60）
次日ZD<0 = 次日DXCD∈{下,忑}（明确P<EMA60）
忠 的P vs EMA60不定，单独看
用户逻辑：长均线(EMA60)是趋势锚
- 中(EMA26>P>EMA60)：价格在EMA60之上 → 更可能升势(次日ZD>0)
- 忠(P>EMA26, EMA26<EMA60)：价格在EMA60之下 → 更可能跌势(次日ZD<0)
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# (DXCD, 护型大类) -> [n, 次日ZD>0, 次日ZC>0, 次日P3]
agg = defaultdict(lambda: [0,0,0,0])
HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[8,9,13,14,26])
    df.columns = ['DXCD','DXAB','日ZA','日ZC','次日高幅']
    for c in ['日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXCD'] = df['DXCD'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA','日ZC'])
    if df.empty: continue
    df['护型'] = df['DXAB'].str[0].map(HX)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    # 次日DXCD
    df['次日DXCD'] = df['DXCD'].shift(-1)
    # 次日ZD>0 = 次日DXCD∈{上,中,忐}
    df['次日ZD正'] = df['次日DXCD'].isin(['上','中','忐']).astype(int)
    # 次日ZC>0 = 次日DXCD∈{上,忐,忠}
    df['次日ZC正'] = df['次日DXCD'].isin(['上','忐','忠']).astype(int)

    for (cd, hx), grp in df.groupby(['DXCD','护型']):
        a = agg[(cd, hx)]
        a[0] += len(grp)
        a[1] += grp['次日ZD正'].sum()
        a[2] += grp['次日ZC正'].sum()
        a[3] += grp['P3'].sum()

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('DXCD × 护型 × 次日ZD>0（长均线锚）')
print('='*70)
for cd in ['上','中','下','忐','忠','忑']:
    print(f'\n--- DXCD={cd} ---')
    print(f"{'护型':<6}{'样本':>10}{'次日ZD>0%':>10}{'次日ZC>0%':>10}{'次日P3%':>10}")
    for hx in ['甲','乙','丙','丁','戊','己']:
        a = agg[(cd, hx)]
        if a[0] > 0:
            print(f"{hx:<6}{a[0]:>10}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>10.2f}{a[3]/a[0]*100:>10.2f}")