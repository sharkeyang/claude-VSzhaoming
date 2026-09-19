# -*- coding: utf-8 -*-
"""首升连深入分析2：升连链长度 + 管宽/BSHA + 持有期收益 + 止损规则"""
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
agg_chain = defaultdict(lambda: [0,0])     # ③ 首升连后升连链长度
agg_bsha = defaultdict(lambda: [0,0])      # ⑤ 首升连+涨幅≥2% 按BSHA
agg_hold = defaultdict(lambda: [0,0,0])    # ⑧ 持有期累计收益(1/3/5/10日)
agg_stop = defaultdict(lambda: [0,0])      # ⑨ 止损信号
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,5,9,10,13,14,19,26])
    df.columns = ['收','涨幅','DXAB','柱排','日ZA','日ZC','BSHA','次日高幅']
    for c in ['收','涨幅','日ZA','日ZC','BSHA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','收'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['前收'] = df['收'].shift(1)
    df = df.dropna(subset=['前收'])
    if df.empty: continue
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    # 持有期累计收益: 未来N天收盘相对当日收盘
    for N in [1,3,5,10]:
        df[f'未来{N}日收盘'] = df['收'].shift(-N)
        df[f'未来{N}日收益'] = df[f'未来{N}日收盘'] / df['收'] - 1
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    first_sl = sub[sub['首升连']==1]
    if first_sl.empty: continue
    fs2 = first_sl[first_sl['涨幅']>=2]
    # ③ 升连链长度: 首升连后连续升连天数
    for idx in fs2.index:
        # 从首升连开始数连续升连
        chain_len = 1
        j = idx + 1
        while j in sub.index and sub.loc[j, '是升连']==1:
            chain_len += 1
            j += 1
        agg_chain[chain_len][0] += 1
        agg_chain[chain_len][1] += sub.loc[idx, '未来5天≥3%']
    # ⑤ BSHA
    for b, grp in fs2.groupby(pd.cut(fs2['BSHA'], bins=[-100,0,2,5,8,100], labels=['<0','0-2','2-5','5-8','>8'])):
        a = agg_bsha[b]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # ⑧ 持有期累计收益
    for N in [1,3,5,10]:
        a = agg_hold[N]; a[0]+=len(fs2); a[1]+=fs2[f'未来{N}日收益'].sum(); a[2]+=fs2[f'未来{N}日收益'].notna().sum()
    # ⑨ 止损信号: 首升连后未来5天是否出现跌连/跌吞/跌破DJA
    for idx in fs2.index:
        window = sub.loc[idx:idx+5]
        if len(window) < 2: continue
        has_dielian = (window['柱排类']=='跌连').any()
        has_dietun = (window['柱排类']=='跌吞').any()
        has_podja = (window['日ZA']<0).any()
        if has_dielian:
            agg_stop['未来5天出现跌连'][0] += 1
            agg_stop['未来5天出现跌连'][1] += sub.loc[idx, '未来5天≥3%']
        if has_dietun:
            agg_stop['未来5天出现跌吞'][0] += 1
            agg_stop['未来5天出现跌吞'][1] += sub.loc[idx, '未来5天≥3%']
        if has_podja:
            agg_stop['未来5天跌破DJA'][0] += 1
            agg_stop['未来5天跌破DJA'][1] += sub.loc[idx, '未来5天≥3%']
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('③ 首升连+涨幅≥2% 后升连链长度')
print('='*70)
rows = []
for n, (cnt, p3) in agg_chain.items():
    if cnt >= 100: rows.append((n, cnt, p3/cnt*100))
rows.sort(key=lambda r: r[0])
print(f"{'链长':<6}{'样本':>10}{'5天≥3%':>10}")
for n, cnt, p3 in rows[:12]:
    print(f"{n:<6}{cnt:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('⑤ 首升连+涨幅≥2% 按BSHA')
print('='*70)
rows = []
for b, (n, p3) in agg_bsha.items():
    if n >= 1000: rows.append((b, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'BSHA':<10}{'样本':>10}{'5天≥3%':>10}")
for b, n, p3 in rows:
    print(f"{b:<10}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('⑧ 首升连+涨幅≥2% 持有期累计收益')
print('='*70)
print(f"{'持有期':<8}{'样本':>10}{'平均收益':>10}")
for N in [1,3,5,10]:
    n, total, valid = agg_hold[N]
    if valid > 0:
        print(f"{N}日".ljust(8) + f"{n:>10}" + f"{total/valid*100:>10.2f}%")
print('\n' + '='*70)
print('⑨ 首升连+涨幅≥2% 止损信号(未来5天)')
print('='*70)
rows = []
for k, (n, p3) in agg_stop.items():
    if n >= 1000: rows.append((k, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'信号':<20}{'样本':>10}{'5天≥3%':>10}")
for k, n, p3 in rows:
    print(f"{k:<20}{n:>10}{p3:>10.2f}")
