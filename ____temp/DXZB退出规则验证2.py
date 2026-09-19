# -*- coding: utf-8 -*-
"""验证"只有DXZB<0才退出，不破DJB就不退出"规则 - 获利性"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
agg = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,13,14,26])
    df.columns = ['DXAB','日ZA','日ZC','次日高幅']
    for c in ['日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['护级'] = df['DXAB'].str[3]
    df['DXZB>0'] = df['护级'].isin(['上','中','忐'])
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    # 按 DXZB 符号
    for zb, grp in df.groupby(df['DXZB>0']):
        zb_label = 'DXZB>0(不退出)' if zb else 'DXZB<0(退出)'
        a = agg[zb_label]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # 按 DXZC × DXZB
    for zc, grp in df.groupby(df['日ZC']>0):
        zc_label = 'DXZC>0' if zc else 'DXZC<0'
        for zb, g in grp.groupby(grp['DXZB>0']):
            zb_label = 'DXZB>0' if zb else 'DXZB<0'
            a = agg[f'{zc_label}+{zb_label}']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\nDXZB 退出规则验证（全样本）:')
print(f"{'场景':<20}{'样本':>10}{'5天≥3%':>10}")
rows = []
for k, (n, p3) in agg.items():
    if n >= 1000: rows.append((k, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
for k, n, p3 in rows:
    print(f"{k:<20}{n:>10}{p3:>10.2f}")
