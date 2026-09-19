# -*- coding: utf-8 -*-
"""验证DXZE<0+DXCD上忐忠的累计收益(受DJE压制)"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
# 聚合: DXZE符号 × DXCD护级 -> [n, 未来5天累计收益, 未来5天最高收益, 未来5天突破DJE]
agg = defaultdict(lambda: [0,0.0,0.0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,9,15,26])
    df.columns = ['收','DXAB','日ZE','次日高幅']
    for c in ['收','日ZE','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['收','次日高幅'])
    if df.empty: continue
    df['护级'] = df['DXAB'].str[3]
    # 未来5天累计收益(相对当前收盘)
    df['未来5天收'] = df['收'].shift(-5)
    df['未来5天累计收益'] = (df['未来5天收']/df['收']-1)*100
    # 未来5天最高收益(用次日高幅累计近似)
    df['未来5天最高'] = df['次日高幅'].rolling(5, min_periods=1).max()
    # 未来5天突破DJE(日ZE从<0变>0)
    df['未来5天ZE'] = df['日ZE'].rolling(5, min_periods=1).max().shift(-4)
    df['未来5天破DJE'] = (df['未来5天ZE']>0).astype(int)
    for ze, grp in df.groupby(df['日ZE']>0):
        ze_label = 'DXZE>0' if ze else 'DXZE<0'
        for hx, g in grp.groupby('护级'):
            a = agg[f'{ze_label}+{hx}']
            a[0]+=len(g)
            a[1]+=g['未来5天累计收益'].fillna(0).sum()
            a[2]+=g['未来5天最高'].fillna(0).sum()
            a[3]+=g['未来5天破DJE'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\nDXZE × DXCD护级 累计收益:')
print(f"{'场景':<16}{'样本':>10}{'5天累计%':>10}{'5天最高%':>10}{'5天破DJE%':>10}")
rows = []
for k, (n, cum, hi, brk) in agg.items():
    if n >= 1000: rows.append((k, n, cum/n, hi/n, brk/n*100))
rows.sort(key=lambda r: -r[2])
for k, n, cum, hi, brk in rows:
    print(f"{k:<16}{n:>10}{cum:>10.2f}{hi:>10.2f}{brk:>10.2f}")
print('\n' + '='*70)
print('DXZE<0 vs DXZE>0 各护级累计收益对比:')
print('='*70)
for hx in ['上','忐','忠','中','下','忑']:
    k0 = f'DXZE<0+{hx}'
    k1 = f'DXZE>0+{hx}'
    if k0 in agg and k1 in agg:
        n0, c0, h0, b0 = agg[k0]; n1, c1, h1, b1 = agg[k1]
        print(f"{hx}: DXZE<0累计={c0/n0:.2f}%破DJE={b0/n0*100:.1f}% vs DXZE>0累计={c1/n1:.2f}%破DJE={b1/n1*100:.1f}%")
