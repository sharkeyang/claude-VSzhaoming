# -*- coding: utf-8 -*-
"""跌连成群结队分DXZC验证：DXZC>0(甲乙己) vs DXZC<0(全护型)"""
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
agg_dielian = defaultdict(lambda: defaultdict(lambda: [0,0,0]))
agg_after = defaultdict(lambda: [0,0,0])
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
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是跌连'] = (df['柱排类']=='跌连').astype(int)
    # DXZC>0 场景: 甲乙己
    sub_pos = df[(df['日ZC']>0) & (df['护型码'].isin(['a','b','r']))].copy()
    if not sub_pos.empty:
        sub_pos['跌连段id'] = (sub_pos['是跌连'] != sub_pos['是跌连'].shift()).cumsum()
        for segid, grp in sub_pos[sub_pos['是跌连']==1].groupby('跌连段id'):
            n = len(grp)
            if n > 15: continue
            a = agg_dielian['DXZC>0'][n]; a[0]+=1; a[1]+=grp['未来5天≥3%'].iloc[0]; a[2]+=grp['未来5天≥3%'].iloc[-1]
        # DXZC>0 跌连后介入
        sub_pos['prev柱排'] = sub_pos['柱排类'].shift(1)
        sub_pos['prev跌连'] = (sub_pos['prev柱排']=='跌连').astype(int)
        after = sub_pos[(sub_pos['prev跌连']==1) & (sub_pos['柱排类']!='跌连')]
        if not after.empty:
            agg_after['DXZC>0跌连后转非跌连'][0] += len(after)
            agg_after['DXZC>0跌连后转非跌连'][1] += after['未来5天≥3%'].sum()
            agg_after['DXZC>0跌连后转非跌连'][2] += (after['柱排类'].isin(['升连','升吞','升反孕'])).sum()
        dl = sub_pos[sub_pos['柱排类']=='跌连']
        agg_after['DXZC>0跌连当日'][0] += len(dl)
        agg_after['DXZC>0跌连当日'][1] += dl['未来5天≥3%'].sum()
    # DXZC<0 场景: 全护型
    sub_neg = df[df['日ZC']<=0].copy()
    if not sub_neg.empty:
        sub_neg['跌连段id'] = (sub_neg['是跌连'] != sub_neg['是跌连'].shift()).cumsum()
        for segid, grp in sub_neg[sub_neg['是跌连']==1].groupby('跌连段id'):
            n = len(grp)
            if n > 15: continue
            a = agg_dielian['DXZC<0'][n]; a[0]+=1; a[1]+=grp['未来5天≥3%'].iloc[0]; a[2]+=grp['未来5天≥3%'].iloc[-1]
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
for zc_label in ['DXZC>0','DXZC<0']:
    print('\n' + '='*70)
    print(f'跌连链长分布 ({zc_label})')
    print('='*70)
    print(f"{'链长':<6}{'链数':>10}{'首日≥3%':>10}{'末日≥3%':>10}")
    rows = []
    for n, (cnt, first, last) in agg_dielian[zc_label].items():
        if cnt >= 100: rows.append((n, cnt, first/cnt*100, last/cnt*100))
    rows.sort(key=lambda r: r[0])
    for n, cnt, f, l in rows[:15]:
        print(f"{n:<6}{cnt:>10}{f:>10.2f}{l:>10.2f}")
    total = sum(cnt for n, cnt, _, _ in rows)
    multi = sum(cnt for n, cnt, _, _ in rows if n >= 2)
    if total > 0:
        print(f"  跌连链长≥2比例 = {multi/total*100:.1f}%")
print('\n' + '='*70)
print('DXZC>0 跌连介入策略')
print('='*70)
for cls, (n, p3, zhuan) in agg_after.items():
    if n >= 500:
        print(f"{cls}: n={n}, 5天≥3%={p3/n*100:.2f}%, 转升排比例={zhuan/n*100:.2f}%")
