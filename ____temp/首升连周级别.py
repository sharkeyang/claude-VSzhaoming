# -*- coding: utf-8 -*-
"""首升连×周级别：周升连是否适用首升连介入策略"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组周/'
files = sorted(glob.glob(DATA_DIR + '谕组周_*.csv'))
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
# 聚合: 条件 -> [n, 未来5周冲高≥3%]
agg = defaultdict(lambda: [0,0])
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[1,3,4,6,8,14,16])
    df.columns = ['周涨','HR','WXAB','柱排','层界','ZA','ZC']
    for c in ['周涨','HR','ZA','ZC']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['WXAB'] = df['WXAB'].astype(str)
    df['柱排'] = df['柱排'].astype(str)
    df['层界'] = df['层界'].astype(str)
    df = df.dropna(subset=['周涨','HR'])
    if df.empty: continue
    df['护型码'] = df['WXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['是升连'] = (df['柱排类']=='升连').astype(int)
    df['prev升连'] = df['是升连'].shift(1).fillna(0)
    df['首升连'] = (df['是升连']==1) & (df['prev升连']==0)
    df['触顶'] = df['层界'].str.endswith('A')
    # 未来5周HR≥3% (用HR列)
    df['未来5周HR'] = df['HR'].rolling(5, min_periods=1).max()
    df['未来5周≥3%'] = (df['未来5周HR'] >= 3).astype(int)
    # 周级别护型
    mask = (df['ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['未来5周≥3%'].sum()
    # 周首升连
    add('周首升连(无限制)', sub[sub['首升连']==1])
    add('周首升连+周涨≥2%', sub[(sub['首升连']==1) & (sub['周涨']>=2)])
    add('周首升连+周涨≥3%', sub[(sub['首升连']==1) & (sub['周涨']>=3)])
    add('周首升连+周涨<2%', sub[(sub['首升连']==1) & (sub['周涨']<2)])
    add('周升连(所有)', sub[sub['是升连']==1])
    add('周基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('首升连×周级别')
print('='*70)
rows = []
for cls, (n, p3) in agg.items():
    if n >= 100: rows.append((cls, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'条件':<24}{'样本':>10}{'未来5周≥3%':>12}")
for cls, n, p3 in rows:
    print(f"{cls:<24}{n:>10}{p3:>12.2f}")
