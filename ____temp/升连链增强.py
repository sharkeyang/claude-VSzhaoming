# -*- coding: utf-8 -*-
"""升连链增强：把升连后停顿一天(跌孕/跌吞)也纳入升连链，看是否增强聚集性"""
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
# 聚合: 链长 -> [链数, 链内首日获利, 链内末日获利]
agg_strict = defaultdict(lambda: [0,0,0])   # 严格升连链(只算连续升连)
agg_loose = defaultdict(lambda: [0,0,0])    # 宽松升连链(升连+跌孕/跌吞停顿)
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    # 严格升连: 是升连
    sub['严格升连'] = (sub['柱排类']=='升连').astype(int)
    # 宽松升连: 升连 或 (跌孕/跌吞停顿)
    sub['宽松升连'] = sub['柱排类'].isin(['升连','跌反孕','跌吞']).astype(int)
    # 严格链
    sub['严格段id'] = (sub['严格升连'] != sub['严格升连'].shift()).cumsum()
    for segid, grp in sub[sub['严格升连']==1].groupby('严格段id'):
        n = len(grp)
        if n > 15: continue
        a = agg_strict[n]; a[0]+=1; a[1]+=grp['未来5天≥3%'].iloc[0]; a[2]+=grp['未来5天≥3%'].iloc[-1]
    # 宽松链
    sub['宽松段id'] = (sub['宽松升连'] != sub['宽松升连'].shift()).cumsum()
    for segid, grp in sub[sub['宽松升连']==1].groupby('宽松段id'):
        n = len(grp)
        if n > 15: continue
        a = agg_loose[n]; a[0]+=1; a[1]+=grp['未来5天≥3%'].iloc[0]; a[2]+=grp['未来5天≥3%'].iloc[-1]
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
for name, agg in [('严格升连链(只算连续升连)', agg_strict), ('宽松升连链(升连+跌孕/跌吞停顿)', agg_loose)]:
    print('\n' + '='*70)
    print(f'{name}')
    print('='*70)
    print(f"{'链长':<6}{'链数':>10}{'首日≥3%':>10}{'末日≥3%':>10}")
    rows = []
    for n, (cnt, first, last) in agg.items():
        if cnt >= 100: rows.append((n, cnt, first/cnt*100, last/cnt*100))
    rows.sort(key=lambda r: r[0])
    for n, cnt, f, l in rows:
        print(f"{n:<6}{cnt:>10}{f:>10.2f}{l:>10.2f}")
    # 汇总: 链长≥2的比例
    total = sum(cnt for n, cnt, _, _ in rows)
    multi = sum(cnt for n, cnt, _, _ in rows if n >= 2)
    print(f"  链长≥2比例 = {multi/total*100:.1f}%")
