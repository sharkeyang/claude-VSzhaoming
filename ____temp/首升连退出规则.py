# -*- coding: utf-8 -*-
"""首升连退出规则：固定持有期 vs 信号退出"""
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
# 聚合: 退出规则 -> [n, 平均收益, 胜率]
agg = defaultdict(lambda: [0,0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,5,9,10,13,14,26])
    df.columns = ['收','涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['收','涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','收'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    df['前收'] = df['收'].shift(1)
    df = df.dropna(subset=['前收'])
    if df.empty: continue
    # 未来N日收盘涨幅(相对首升连收盘)
    for N in [2,3,5]:
        df[f'未来{N}日收盘'] = df['收'].shift(-N) / df['收'] - 1
    # 未来5天是否出现跌吞/跌破DJA
    df['未来跌吞'] = df['柱排类'].shift(-1).isin(['跌吞']).rolling(5, min_periods=1).max().fillna(0)
    df['未来跌破DJA'] = (df['日ZA'].shift(-1) < 0).rolling(5, min_periods=1).max().fillna(0)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r'])) & (df['首升连']==1) & (df['涨幅']>=2)
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    def add(cls, grp, N):
        a = agg[cls]; a[0]+=len(grp)
        ret = grp[f'未来{N}日收盘'].dropna()
        a[1]+=ret.sum(); a[2]+=(ret>0).sum()
    # 固定持有期
    add('固定2日', sub, 2)
    add('固定3日', sub, 3)
    add('固定5日', sub, 5)
    # 信号退出: 出现跌吞就退出(最多持有5日)
    # 简化: 用未来跌吞分组看收益
    for sig in [0,1]:
        g = sub[sub['未来跌吞']==sig]
        add(f'未来5天{("有" if sig else "无")}跌吞', g, 5)
    for sig in [0,1]:
        g = sub[sub['未来跌破DJA']==sig]
        add(f'未来5天{("跌破" if sig else "未破")}DJA', g, 5)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连+涨幅≥2% 退出规则')
print('='*70)
rows = []
for cls, (n, ret, win) in agg.items():
    if n >= 1000: rows.append((cls, n, ret/n*100, win/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'规则':<20}{'样本':>10}{'平均收益':>10}{'胜率':>10}")
for cls, n, r, w in rows:
    print(f"{cls:<20}{n:>10}{r:>10.2f}{w:>10.2f}")
