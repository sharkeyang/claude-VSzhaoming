# -*- coding: utf-8 -*-
"""首升连介入策略回测：DXZC>0 甲乙己 首升连+涨幅≥2% 持有N天"""
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
# 聚合: 持有期 -> [交易次数, 总收益, 盈利次数, 亏损次数]
agg = defaultdict(lambda: [0,0,0,0])
# 按年份统计
agg_year = defaultdict(lambda: defaultdict(lambda: [0,0,0,0]))
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[0,1,5,9,10,13,14,26])
    df.columns = ['日期','收','涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['收','涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','收'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
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
    if fs2.empty: continue
    # 持有N天收益: 未来N天收盘相对当日收盘
    for N in [2,3,5]:
        for idx in fs2.index:
            j = idx + N
            if j not in sub.index: continue
            ret = sub.loc[j, '收'] / sub.loc[idx, '收'] - 1
            a = agg[N]; a[0]+=1; a[1]+=ret; a[2]+= (ret>0); a[3]+= (ret<0)
            # 年份
            yr = str(sub.loc[idx, '日期'])[:4]
            b = agg_year[N][yr]; b[0]+=1; b[1]+=ret; b[2]+= (ret>0); b[3]+= (ret<0)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连+涨幅≥2% 介入策略回测（持有N天）')
print('='*70)
print(f"{'持有期':<8}{'交易次数':>10}{'平均收益':>10}{'胜率':>10}{'累计收益':>10}")
for N in [2,3,5]:
    n, total, win, loss = agg[N]
    if n > 0:
        print(f"{N}日".ljust(8) + f"{n:>10}" + f"{total/n*100:>10.2f}%" + f"{win/n*100:>10.2f}%" + f"{total*100:>10.2f}%")
print('\n' + '='*70)
print('按年份（持有3日）')
print('='*70)
print(f"{'年份':<8}{'交易次数':>10}{'平均收益':>10}{'胜率':>10}")
for yr in sorted(agg_year[3].keys()):
    n, total, win, loss = agg_year[3][yr]
    if n > 0:
        print(f"{yr:<8}{n:>10}{total/n*100:>10.2f}%{win/n*100:>10.2f}%")
