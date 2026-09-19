# -*- coding: utf-8 -*-
"""首升连介入策略：不同时间维度冲高概率(1/2/3/5/10日)"""
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
# 聚合: 条件 -> 时间维度 -> [n, 冲高≥3%]
agg = defaultdict(lambda: defaultdict(lambda: [0,0]))
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    # 未来N日冲高≥3% (rolling max)
    for N in [1,2,3,5,10]:
        df[f'未来{N}日高幅'] = df['次日高幅'].rolling(N, min_periods=1).max()
        df[f'未来{N}日≥3%'] = (df[f'未来{N}日高幅'] >= 3).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    first_sl = sub[sub['首升连']==1]
    if first_sl.empty: continue
    def add(cls, grp):
        for N in [1,2,3,5,10]:
            a = agg[cls][N]; a[0]+=len(grp); a[1]+=grp[f'未来{N}日≥3%'].sum()
    add('首升连(无限制)', first_sl)
    add('首升连+涨幅≥2%', first_sl[first_sl['涨幅']>=2])
    add('首升连+涨幅≥2.5%', first_sl[first_sl['涨幅']>=2.5])
    add('首升连+涨幅≥3%', first_sl[first_sl['涨幅']>=3])
    add('首升连+涨幅<2%', first_sl[first_sl['涨幅']<2])
    add('基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连介入策略：不同时间维度冲高≥3%概率')
print('='*70)
order = ['首升连(无限制)','首升连+涨幅≥2%','首升连+涨幅≥2.5%','首升连+涨幅≥3%','首升连+涨幅<2%','基线(甲乙己ZC>0)']
print(f"{'条件':<22}{'样本':>10}{'1日':>8}{'2日':>8}{'3日':>8}{'5日':>8}{'10日':>8}")
for cls in order:
    if cls not in agg: continue
    n = agg[cls][1][0]
    if n < 1000: continue
    vals = []
    for N in [1,2,3,5,10]:
        cnt, hit = agg[cls][N]
        vals.append(hit/cnt*100)
    print(f"{cls:<22}{n:>10}{vals[0]:>8.2f}{vals[1]:>8.2f}{vals[2]:>8.2f}{vals[3]:>8.2f}{vals[4]:>8.2f}")
