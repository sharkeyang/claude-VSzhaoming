# -*- coding: utf-8 -*-
"""首升连三维交叉：触顶×BSHA×日等型×护型"""
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
# 聚合: 组合 -> [n, 5天≥3%]
agg = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,19,26,30,44])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','BSHA','次日高幅','上符串','日等型']
    for c in ['涨幅','日ZA','日ZC','BSHA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df['日等型'] = df['日等型'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['触顶'] = df['上符串'].str.endswith('A')
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r'])) & (df['首升连']==1) & (df['涨幅']>=2)
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # 触顶×BSHA
    for t in [True, False]:
        for b in ['BSHA<2','BSHA2-5','BSHA≥5']:
            if b=='BSHA<2': g = sub[(sub['触顶']==t) & (sub['BSHA']<2)]
            elif b=='BSHA2-5': g = sub[(sub['触顶']==t) & (sub['BSHA']>=2) & (sub['BSHA']<5)]
            else: g = sub[(sub['触顶']==t) & (sub['BSHA']>=5)]
            add(f'触顶={t}×{b}', g)
    # 触顶×日等型
    for t in [True, False]:
        for e in ['等1','等2','等3']:
            g = sub[(sub['触顶']==t) & (sub['日等型']==e)]
            add(f'触顶={t}×{e}', g)
    # 护型×BSHA
    for hx in ['a','b','r']:
        for b in ['BSHA<2','BSHA2-5','BSHA≥5']:
            if b=='BSHA<2': g = sub[(sub['护型码']==hx) & (sub['BSHA']<2)]
            elif b=='BSHA2-5': g = sub[(sub['护型码']==hx) & (sub['BSHA']>=2) & (sub['BSHA']<5)]
            else: g = sub[(sub['护型码']==hx) & (sub['BSHA']>=5)]
            add(f'护型{hx}×{b}', g)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连+涨幅≥2% 三维交叉')
print('='*70)
rows = []
for cls, (n, p3) in agg.items():
    if n >= 1000: rows.append((cls, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'组合':<28}{'样本':>10}{'5天≥3%':>10}")
for cls, n, p3 in rows:
    print(f"{cls:<28}{n:>10}{p3:>10.2f}")
