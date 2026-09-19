# -*- coding: utf-8 -*-
"""垒升综合验证：阈值精确化 + 柱体×触顶交叉 + 其他柱排 + 升连聚集性"""
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
# 聚合容器
agg_thresh = defaultdict(lambda: [0,0,0])   # 涨幅阈值精确化(升连)
agg_touch = defaultdict(lambda: [0,0,0])    # 柱体×触顶交叉(升连)
agg_other = defaultdict(lambda: [0,0,0])    # 其他柱排(升吞/升孕)按涨幅
agg_cluster = defaultdict(lambda: [0,0])    # 升连聚集性: 连续升连天数->[段数, 段内平均后续获利]
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26,30])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅','上符串']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['触顶'] = df['上符串'].str.endswith('A')
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['未来5天≥5%'] = (df['未来5天高幅'] >= 5).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    sub['涨幅abs'] = sub['涨幅'].abs()
    shenglian = sub[sub['柱排类']=='升连']
    # 1. 阈值精确化: 升连按涨幅0.5步进
    bins_t = [0,0.5,1,1.5,2,2.5,3,4,5,100]
    labels_t = ['<0.5','0.5-1','1-1.5','1.5-2','2-2.5','2.5-3','3-4','4-5','>5']
    for b, grp in shenglian.groupby(pd.cut(shenglian['涨幅abs'], bins=bins_t, labels=labels_t)):
        a = agg_thresh[f'涨幅{b}']; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    # 2. 柱体×触顶交叉: 升连按(涨幅≥2%, 触顶)四象限
    for big in [True, False]:
        for t in [True, False]:
            g = shenglian[(shenglian['涨幅abs']>=2)==big]
            g = g[g['触顶']==t]
            a = agg_touch[f'柱体{"≥2%" if big else "<2%"}_触顶={t}']
            a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum(); a[2]+=g['未来5天≥5%'].sum()
    # 3. 其他柱排(升吞/升孕)按涨幅
    for zp in ['升吞','升反孕']:
        g = sub[sub['柱排类']==zp]
        for big in [True, False]:
            gg = g[(g['涨幅abs']>=2)==big]
            a = agg_other[f'{zp}_柱体{"≥2%" if big else "<2%"}']
            a[0]+=len(gg); a[1]+=gg['未来5天≥3%'].sum(); a[2]+=gg['未来5天≥5%'].sum()
    # 4. 升连聚集性: 连续升连段
    sub['是升连'] = (sub['柱排类']=='升连').astype(int)
    # 用文件内连续段(跨文件会断，但占比小)
    sub['段id'] = (sub['是升连'] != sub['是升连'].shift()).cumsum()
    for segid, grp in sub[sub['是升连']==1].groupby('段id'):
        n = len(grp)
        agg_cluster[n][0] += 1
        agg_cluster[n][1] += grp['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
# 输出
print('\n' + '='*70)
print('1. 阈值精确化: 升连按涨幅0.5步进')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg_thresh.items():
    if n >= 500: rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<12}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<12}{n:>10}{p3:>10.2f}{p5:>10.2f}")
print('\n' + '='*70)
print('2. 柱体×触顶交叉: 升连四象限')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg_touch.items():
    if n >= 500: rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<20}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<20}{n:>10}{p3:>10.2f}{p5:>10.2f}")
print('\n' + '='*70)
print('3. 其他柱排(升吞/升孕)按柱体大小')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg_other.items():
    if n >= 500: rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<20}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<20}{n:>10}{p3:>10.2f}{p5:>10.2f}")
print('\n' + '='*70)
print('4. 升连聚集性: 连续升连天数分布')
print('='*70)
rows = []
for n, (cnt, p3) in agg_cluster.items():
    if cnt >= 100: rows.append((n, cnt, p3/cnt*100))
rows.sort(key=lambda r: r[0])
print(f"{'连续升连天数':<12}{'段数':>10}{'段内5天≥3%':>12}")
for n, cnt, p3 in rows[:20]:
    print(f"{n:<12}{cnt:>10}{p3:>12.2f}")
