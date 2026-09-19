# -*- coding: utf-8 -*-
"""垒升持续持有验证：用'未来N天收盘都获利'区分垒升与平移(高波动标的)"""
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
# 聚合: 波动水平 -> 涨幅档 -> [n, 未来5天收盘都≥3%(持续持有), 未来5天最高≥3%(冲高)]
agg = defaultdict(lambda: defaultdict(lambda: [0,0,0]))
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,5,9,10,13,14,26])
    df.columns = ['收','涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['收','涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','收'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['前收'] = df['收'].shift(1)
    df = df.dropna(subset=['前收'])
    if df.empty: continue
    # 未来5天收盘涨幅(相对当日收盘)
    df['未来收盘涨幅'] = df['收'].shift(-5) / df['收'] - 1
    df['未来5天收盘≥3%'] = (df['未来收盘涨幅'] >= 0.03).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天冲高≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['均涨幅20'] = df['涨幅'].abs().rolling(20, min_periods=5).mean()
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    shenglian = sub[sub['柱排类']=='升连']
    if shenglian.empty: continue
    for wl, grp in shenglian.groupby(pd.cut(shenglian['均涨幅20'], bins=[0,1,2,3,5,100], labels=['<1%','1-2%','2-3%','3-5%','>5%'])):
        for b, g in grp.groupby(pd.cut(grp['涨幅'].abs(), bins=[0,1,2,3,100], labels=['<1','1-2','2-3','>3'])):
            a = agg[wl][f'涨幅{b}']
            a[0]+=len(g); a[1]+=g['未来5天收盘≥3%'].sum(); a[2]+=g['未来5天冲高≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
for wl in ['<1%','1-2%','2-3%','3-5%','>5%']:
    if wl not in agg: continue
    print(f'\n--- 波动水平 {wl} ---')
    print(f"{'涨幅档':<8}{'样本':>10}{'5天收盘≥3%(持有)':>18}{'5天冲高≥3%(波段)':>18}")
    rows = []
    for b, (n, hold, spike) in agg[wl].items():
        if n >= 500: rows.append((b, n, hold/n*100, spike/n*100))
    rows.sort(key=lambda r: -r[2])
    for b, n, h, s in rows:
        print(f"{b:<8}{n:>10}{h:>18.2f}{s:>18.2f}")
