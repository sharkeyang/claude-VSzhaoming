# -*- coding: utf-8 -*-
"""验证DXZE<0时DXCD上忐忠是否鸡肋(受大均线压制)"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
# 聚合: DXZE符号 × DXCD护级 -> [n, 5天≥3%]
agg = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,15,26])
    df.columns = ['DXAB','日ZE','次日高幅']
    for c in ['日ZE','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['护级'] = df['DXAB'].str[3]
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    for ze, grp in df.groupby(df['日ZE']>0):
        ze_label = 'DXZE>0' if ze else 'DXZE<0'
        for hx, g in grp.groupby('护级'):
            a = agg[f'{ze_label}+{hx}']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\nDXZE × DXCD护级 获利性:')
print(f"{'场景':<16}{'样本':>10}{'5天≥3%':>10}")
rows = []
for k, (n, p3) in agg.items():
    if n >= 1000: rows.append((k, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
for k, n, p3 in rows:
    print(f"{k:<16}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('DXZE<0 vs DXZE>0 各护级对比:')
print('='*70)
for hx in ['上','忐','忠','中','下','忑']:
    k0 = f'DXZE<0+{hx}'
    k1 = f'DXZE>0+{hx}'
    if k0 in agg and k1 in agg:
        n0, p0 = agg[k0]; n1, p1 = agg[k1]
        print(f"{hx}: DXZE<0={p0/n0*100:.2f}%(n={n0}) vs DXZE>0={p1/n1*100:.2f}%(n={n1}) 差={p1/n1*100-p0/n0*100:.2f}pp")
