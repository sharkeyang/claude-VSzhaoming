# -*- coding: utf-8 -*-
"""首升连×大盘环境：用上证指数涨幅作为大盘环境"""
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
# 加载上证指数(大盘环境)
idx = pd.read_csv(DATA_DIR + '谕组日_sh000001.csv', encoding='gbk', header=None, usecols=[0,5])
idx.columns = ['日期','大盘涨幅']
idx['日期'] = pd.to_datetime(idx['日期'], errors='coerce')
idx['大盘涨幅'] = pd.to_numeric(idx['大盘涨幅'], errors='coerce')
idx = idx.dropna()
idx_map = dict(zip(idx['日期'], idx['大盘涨幅']))
print(f'大盘数据 {len(idx_map)} 天')
agg = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    if 'sh000001' in f: continue  # 跳过指数本身
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[0,5,9,10,13,14,26])
    df.columns = ['日期','涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['次日高幅','涨幅','日期'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['大盘涨幅'] = df['日期'].map(idx_map)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r'])) & (df['首升连']==1) & (df['涨幅']>=2)
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum()
    # 按大盘涨幅分组
    for b, g in sub.groupby(pd.cut(sub['大盘涨幅'], bins=[-100,-1,0,1,100], labels=['大盘跌>1%','大盘平-1~1%','大盘涨1-1%','大盘涨>1%'])):
        add(f'大盘{b}', g)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连+涨幅≥2% × 大盘环境')
print('='*70)
rows = []
for cls, (n, p3) in agg.items():
    if n >= 1000: rows.append((cls, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'大盘环境':<20}{'样本':>10}{'5天≥3%':>10}")
for cls, n, p3 in rows:
    print(f"{cls:<20}{n:>10}{p3:>10.2f}")
