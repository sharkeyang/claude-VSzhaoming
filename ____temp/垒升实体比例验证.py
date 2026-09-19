# -*- coding: utf-8 -*-
"""
垒升实体比例验证：柱体/振幅比例 vs 绝对涨幅阈值
========================================
用户建议: 用柱体与高低差的比例(实体/振幅)得到更通用的垒升定义
  实体 = |今收-前收| (柱体大小)
  振幅 = 今高-今低 (高低差)
  实体/振幅 = 收盘位置在当日振幅中的占比(无量纲，不依赖价格水平)

验证: 甲乙DXZA>0己，DXZC>0，升连柱按实体/振幅比例分档 vs 按绝对涨幅分档
数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 1=收, 3=高, 4=低, 5=涨幅, 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
agg_ratio = defaultdict(lambda: [0,0,0])   # 实体/振幅比例分档
agg_abs = defaultdict(lambda: [0,0,0])     # 绝对涨幅分档
def classify_zp(v):
    v = str(v)
    if '尾连' in v: return '升连' if v.startswith('升') else ('跌连' if v.startswith('跌') else '人连')
    if '尾吞' in v: return '升吞' if v.startswith('升') else ('跌吞' if v.startswith('跌') else '人吞')
    if '尾反孕' in v: return '升反孕' if v.startswith('升') else ('跌反孕' if v.startswith('跌') else '人反孕')
    if '连后吞' in v: return '连后吞'
    if '吞吞' in v: return '吞吞'
    if '孕孕' in v: return '孕孕'
    return '其他'
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,3,4,5,9,10,13,14,26])
    df.columns = ['收','高','低','涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['收','高','低','涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','收','高','低'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['前收'] = df['收'].shift(1)
    df = df.dropna(subset=['前收'])
    if df.empty: continue
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['未来5天≥5%'] = (df['未来5天高幅'] >= 5).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    sub['实体'] = (sub['收']-sub['前收']).abs()
    sub['振幅'] = (sub['高']-sub['低']).abs()
    sub['实体比'] = sub['实体'] / sub['振幅'].replace(0, float('nan'))
    sub['涨幅abs'] = sub['涨幅'].abs()
    shenglian = sub[sub['柱排类']=='升连']
    # 实体/振幅比例分档
    bins_r = [0, 0.3, 0.5, 0.7, 0.9, 1.1]
    labels_r = ['<0.3','0.3-0.5','0.5-0.7','0.7-0.9','>0.9']
    for b, grp in shenglian.groupby(pd.cut(shenglian['实体比'], bins=bins_r, labels=labels_r)):
        a = agg_ratio[f'实体比{b}']; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    # 绝对涨幅分档
    bins_a = [0, 1, 2, 3, 5, 100]
    labels_a = ['<1','1-2','2-3','3-5','>5']
    for b, grp in shenglian.groupby(pd.cut(shenglian['涨幅abs'], bins=bins_a, labels=labels_a)):
        a = agg_abs[f'涨幅{b}']; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
for name, agg in [('实体/振幅比例(无量纲)', agg_ratio), ('绝对涨幅阈值(%)', agg_abs)]:
    print('\n' + '='*70)
    print(f'{name} 对升连后续获利区分度')
    print('='*70)
    rows = []
    for cls, (n, p3, p5) in agg.items():
        if n >= 500:
            rows.append((cls, n, p3/n*100, p5/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'类别':<16}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
    for cls, n, p3, p5 in rows:
        print(f"{cls:<16}{n:>10}{p3:>10.2f}{p5:>10.2f}")
    if rows:
        print(f"  区分度 = {max(r[2] for r in rows)-min(r[2] for r in rows):.1f}pp")
