# -*- coding: utf-8 -*-
"""首个升连介入策略验证：DXZC>0 甲乙己 首个升连(两个连续阳柱)介入"""
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
# 聚合: 限制条件 -> [n, 次日冲高≥3%, 5天≥3%, 次日平均高幅]
agg = defaultdict(lambda: [0,0,0,0])
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
    df['次日≥3%'] = (df['次日高幅'] >= 3).astype(int)
    df['柱排类'] = df['柱排'].apply(classify_zp)
    # 首个升连: 当日是升连且前一日不是升连(升连链首柱)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    first_sl = sub[sub['首升连']==1]
    if first_sl.empty: continue
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['次日≥3%'].sum(); a[2]+=grp['未来5天≥3%'].sum(); a[3]+=grp['次日高幅'].sum()
    # 基础: 首个升连
    add('首升连(无限制)', first_sl)
    # 涨幅限制
    for t in [1, 1.5, 2, 2.5, 3]:
        g = first_sl[first_sl['涨幅']>=t]
        add(f'首升连+涨幅≥{t}%', g)
        g_lt = first_sl[first_sl['涨幅']<t]
        add(f'首升连+涨幅<{t}%', g_lt)
    # 首升连 vs 非首升连(升连链中后段)
    non_first = sub[(sub['是升连']==1) & (sub['首升连']==0)]
    add('升连链中后段', non_first)
    # 基线
    add('基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首个升连介入策略验证（DXZC>0 甲乙己）')
print('='*70)
rows = []
for cls, (n, p1, p5, avg) in agg.items():
    if n >= 1000: rows.append((cls, n, p1/n*100, p5/n*100, avg/n))
# 按类别排序
order = ['首升连(无限制)','首升连+涨幅≥1%','首升连+涨幅<1%','首升连+涨幅≥1.5%','首升连+涨幅<1.5%',
         '首升连+涨幅≥2%','首升连+涨幅<2%','首升连+涨幅≥2.5%','首升连+涨幅<2.5%',
         '首升连+涨幅≥3%','首升连+涨幅<3%','升连链中后段','基线(甲乙己ZC>0)']
rows.sort(key=lambda r: order.index(r[0]) if r[0] in order else 99)
print(f"{'类别':<22}{'样本':>10}{'次日≥3%':>10}{'5天≥3%':>10}{'次日均高幅':>10}")
for cls, n, p1, p5, avg in rows:
    print(f"{cls:<22}{n:>10}{p1:>10.2f}{p5:>10.2f}{avg:>10.2f}")
