# -*- coding: utf-8 -*-
"""升连聚集性深入研究：连续升连段的结构特征"""
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
# 聚合: 连续升连段长度 -> [段数, 段内首日后续获利, 段内末日后续获利, 段内平均涨幅]
agg_seg = defaultdict(lambda: [0,0,0,0])
# 升连段内位置 -> 后续获利(第1天/第2天/...)
agg_pos = defaultdict(lambda: [0,0])
# 升连段前一日柱排 -> 段数
agg_prev = defaultdict(lambda: [0,0])
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
    sub['是升连'] = (sub['柱排类']=='升连').astype(int)
    sub['段id'] = (sub['是升连'] != sub['是升连'].shift()).cumsum()
    # 遍历连续升连段
    for segid, grp in sub[sub['是升连']==1].groupby('段id'):
        n = len(grp)
        if n > 15: continue  # 只看≤15天段
        a = agg_seg[n]
        a[0] += 1
        a[1] += grp['未来5天≥3%'].iloc[0]   # 首日
        a[2] += grp['未来5天≥3%'].iloc[-1]  # 末日
        a[3] += grp['涨幅'].abs().mean()     # 段内平均涨幅
        # 段内位置
        for pos, row in grp.iterrows():
            agg_pos[n][0] += 1
            agg_pos[n][1] += row['未来5天≥3%']
        # 前一日柱排
        prev_idx = grp.index[0] - 1
        if prev_idx in sub.index:
            prev_zp = sub.loc[prev_idx, '柱排类']
            agg_prev[prev_zp][0] += 1
            agg_prev[prev_zp][1] += grp['未来5天≥3%'].iloc[0]
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('升连聚集性: 连续升连段长度 -> 首日/末日后续获利')
print('='*70)
print(f"{'连续天数':<8}{'段数':>10}{'首日≥3%':>10}{'末日≥3%':>10}{'段均涨幅':>10}")
rows = []
for n, (cnt, first, last, avg) in agg_seg.items():
    if cnt >= 100: rows.append((n, cnt, first/cnt*100, last/cnt*100, avg/cnt))
rows.sort(key=lambda r: r[0])
for n, cnt, f, l, a in rows:
    print(f"{n:<8}{cnt:>10}{f:>10.2f}{l:>10.2f}{a:>10.2f}")
print('\n' + '='*70)
print('升连段内位置 -> 后续获利(第1天到第N天)')
print('='*70)
print(f"{'连续天数':<8}{'位置':<6}{'样本':>10}{'该位置≥3%':>10}")
for n in sorted(agg_pos.keys()):
    if n < 2 or n > 8: continue
    total, hits = agg_pos[n]
    # 按位置细分需要重新存，这里只显示整体
    print(f"{n:<8}{'整体':<6}{total:>10}{hits/total*100:>10.2f}")
print('\n' + '='*70)
print('升连段前一日柱排 -> 段数/首日获利')
print('='*70)
rows = []
for zp, (cnt, first) in agg_prev.items():
    if cnt >= 100: rows.append((zp, cnt, first/cnt*100))
rows.sort(key=lambda r: -r[1])
print(f"{'前一日柱排':<12}{'段数':>10}{'首日≥3%':>10}")
for zp, cnt, f in rows:
    print(f"{zp:<12}{cnt:>10}{f:>10.2f}")
