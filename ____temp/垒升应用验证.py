# -*- coding: utf-8 -*-
"""垒升应用验证：高波动十字星阈值 + 跌连聚集性 + 介入策略"""
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
# 聚合
agg_high = defaultdict(lambda: [0,0])   # 高波动升连按涨幅
agg_dielian = defaultdict(lambda: [0,0,0])  # 跌连链长->[链数,首日,末日]
agg_strategy = defaultdict(lambda: [0,0])   # 介入策略->[n,5天≥3%]
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
    df['均涨幅20'] = df['涨幅'].abs().rolling(20, min_periods=5).mean()
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    # 1. 高波动(>3%)升连按涨幅细分
    high = sub[sub['均涨幅20']>3]
    sl_high = high[high['柱排类']=='升连']
    for b, grp in sl_high.groupby(pd.cut(sl_high['涨幅'].abs(), bins=[0,0.5,1,1.5,2,3,100], labels=['<0.5','0.5-1','1-1.5','1.5-2','2-3','>3'])):
        a = agg_high[f'高波动升连涨幅{b}']; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # 2. 跌连链长(镜面映射)
    sub['是跌连'] = (sub['柱排类']=='跌连').astype(int)
    sub['跌连段id'] = (sub['是跌连'] != sub['是跌连'].shift()).cumsum()
    for segid, grp in sub[sub['是跌连']==1].groupby('跌连段id'):
        n = len(grp)
        if n > 15: continue
        a = agg_dielian[n]; a[0]+=1; a[1]+=grp['未来5天≥3%'].iloc[0]; a[2]+=grp['未来5天≥3%'].iloc[-1]
    # 3. 介入策略
    sub['prev柱排'] = sub['柱排类'].shift(1)
    # 策略A: 升连后介入(当日是升连)
    g = sub[sub['柱排类']=='升连']
    a = agg_strategy['A_升连当日介入']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 策略B: 跌连后不介入(当日是跌连)
    g = sub[sub['柱排类']=='跌连']
    a = agg_strategy['B_跌连当日(不介入)']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 策略C: 跌连后转人排/升排再介入(前一日跌连,当日非跌连)
    g = sub[(sub['prev柱排']=='跌连') & (sub['柱排类']!='跌连')]
    a = agg_strategy['C_跌连后转非跌连介入']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 策略D: 跌连后转升排再介入(前一日跌连,当日升连/升吞/升孕)
    g = sub[(sub['prev柱排']=='跌连') & (sub['柱排类'].isin(['升连','升吞','升反孕']))]
    a = agg_strategy['D_跌连后转升排介入']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 策略E: 跌连后转人排再介入(前一日跌连,当日人排)
    g = sub[(sub['prev柱排']=='跌连') & (sub['柱排类'].isin(['连后吞','吞吞','孕孕']))]
    a = agg_strategy['E_跌连后转人排介入']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    # 基线
    a = agg_strategy['基线(甲乙己ZC>0)']; a[0]+=len(sub); a[1]+=sub['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('1. 高波动(>3%)升连按涨幅细分(十字星阈值)')
print('='*70)
rows = []
for cls, (n, p3) in agg_high.items():
    if n >= 500: rows.append((cls, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<20}{'样本':>10}{'5天≥3%':>10}")
for cls, n, p3 in rows:
    print(f"{cls:<20}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('2. 跌连链长(镜面映射)')
print('='*70)
print(f"{'链长':<6}{'链数':>10}{'首日≥3%':>10}{'末日≥3%':>10}")
rows = []
for n, (cnt, first, last) in agg_dielian.items():
    if cnt >= 100: rows.append((n, cnt, first/cnt*100, last/cnt*100))
rows.sort(key=lambda r: r[0])
for n, cnt, f, l in rows[:15]:
    print(f"{n:<6}{cnt:>10}{f:>10.2f}{l:>10.2f}")
total = sum(cnt for n, cnt, _, _ in rows)
multi = sum(cnt for n, cnt, _, _ in rows if n >= 2)
print(f"  跌连链长≥2比例 = {multi/total*100:.1f}%")
print('\n' + '='*70)
print('3. 介入策略')
print('='*70)
rows = []
for cls, (n, p3) in agg_strategy.items():
    if n >= 500: rows.append((cls, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'策略':<24}{'样本':>10}{'5天≥3%':>10}")
for cls, n, p3 in rows:
    print(f"{cls:<24}{n:>10}{p3:>10.2f}")
