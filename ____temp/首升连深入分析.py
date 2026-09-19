# -*- coding: utf-8 -*-
"""首升连深入分析：护型交叉 + 触顶 + 前一日柱排 + 日等型 + 波动水平"""
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
agg_hx = defaultdict(lambda: [0,0])      # 首升连+涨幅≥2% 按护型
agg_touch = defaultdict(lambda: [0,0])   # 首升连+涨幅≥2% 按触顶
agg_prev = defaultdict(lambda: [0,0])    # 首升连+涨幅≥2% 按前一日柱排
agg_deng = defaultdict(lambda: [0,0])    # 首升连+涨幅≥2% 按日等型
agg_wl = defaultdict(lambda: [0,0])      # 首升连+涨幅≥2% 按波动水平
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26,30,44])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅','上符串','日等型']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['上符串'] = df['上符串'].astype(str)
    df['日等型'] = df['日等型'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['触顶'] = df['上符串'].str.endswith('A')
    df['均涨幅20'] = df['涨幅'].abs().rolling(20, min_periods=5).mean()
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    df['prev柱排'] = df['柱排类'].shift(1)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    first_sl = sub[sub['首升连']==1]
    if first_sl.empty: continue
    # 只取涨幅≥2%的首升连
    fs2 = first_sl[first_sl['涨幅']>=2]
    if fs2.empty: continue
    def add(agg, key, grp):
        a = agg[key]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # 护型
    for hx, grp in fs2.groupby('护型码'):
        add(agg_hx, {'a':'甲','b':'乙','r':'己'}.get(hx,hx), grp)
    # 触顶
    for t, grp in fs2.groupby('触顶'):
        add(agg_touch, f'触顶={t}', grp)
    # 前一日柱排
    for zp, grp in fs2.groupby('prev柱排'):
        add(agg_prev, zp, grp)
    # 日等型
    for d, grp in fs2.groupby('日等型'):
        add(agg_deng, d, grp)
    # 波动水平
    for wl, grp in fs2.groupby(pd.cut(fs2['均涨幅20'], bins=[0,1,2,3,5,100], labels=['<1%','1-2%','2-3%','3-5%','>5%'])):
        add(agg_wl, wl, grp)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
def show(title, agg):
    print('\n' + '='*70)
    print(f'{title}')
    print('='*70)
    rows = []
    for k, (n, p3) in agg.items():
        if n >= 1000: rows.append((k, n, p3/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'类别':<16}{'样本':>10}{'5天≥3%':>10}")
    for k, n, p3 in rows:
        print(f"{k:<16}{n:>10}{p3:>10.2f}")
show('① 首升连+涨幅≥2% 按护型', agg_hx)
show('② 首升连+涨幅≥2% 按触顶', agg_touch)
show('④ 首升连+涨幅≥2% 按前一日柱排', agg_prev)
show('⑥ 首升连+涨幅≥2% 按日等型', agg_deng)
show('⑦ 首升连+涨幅≥2% 按波动水平', agg_wl)
