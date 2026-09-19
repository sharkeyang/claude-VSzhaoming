# -*- coding: utf-8 -*-
"""验证"只有DXZB<0才退出，不破DJB就不退出"规则"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
def classify_zp(v):
    v = str(v)
    if '尾连' in v: return '升连' if v.startswith('升') else ('跌连' if v.startswith('跌') else '人连')
    if '尾吞' in v: return '升吞' if v.startswith('升') else ('跌吞' if v.startswith('跌') else '人吞')
    if '尾反孕' in v: return '升反孕' if v.startswith('升') else ('跌反孕' if v.startswith('跌') else '人反孕')
    if '连后吞' in v: return '连后吞'
    if '吞吞' in v: return '吞吞'
    if '孕孕' in v: return '孕孕'
    return '其他'
# 聚合: DXZB符号 -> 护型 -> [n, 未来5天≥3%]
agg = defaultdict(lambda: defaultdict(lambda: [0,0]))
# 未来5天跌破DJB概率
agg_break = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['护级'] = df['DXAB'].str[3]  # 第3字符=护级
    df['DXZB>0'] = df['护级'].isin(['上','中','忐'])
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    # 按 DXZB 符号 × 护型
    for zb, grp in sub.groupby(sub['DXZB>0']):
        zb_label = 'DXZB>0(不破DJB)' if zb else 'DXZB<0(破DJB)'
        for hx, g in grp.groupby('护型码'):
            a = agg[zb_label][hx]; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 未来5天跌破DJB概率(护级从>0变<0)
    sub['未来5天破DJB'] = sub['DXZB>0'].rolling(5, min_periods=1).min().shift(-4).fillna(1)
    for zb, grp in sub.groupby(sub['DXZB>0']):
        zb_label = 'DXZB>0(不破DJB)' if zb else 'DXZB<0(破DJB)'
        agg_break[zb_label][0] += len(grp)
        agg_break[zb_label][1] += (grp['未来5天破DJB']==0).sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('DXZB符号 × 护型 → 未来5天≥3%')
print('='*70)
for zb in ['DXZB>0(不破DJB)','DXZB<0(破DJB)']:
    print(f'\n--- {zb} ---')
    rows = []
    for hx, (n, p3) in agg[zb].items():
        if n >= 1000: rows.append((hx, n, p3/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'护型':<6}{'样本':>10}{'5天≥3%':>10}")
    for hx, n, p3 in rows:
        print(f"{hx:<6}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('未来5天跌破DJB概率')
print('='*70)
for zb, (n, brk) in agg_break.items():
    if n >= 1000:
        print(f"{zb}: n={n}, 未来5天破DJB={brk/n*100:.2f}%")
