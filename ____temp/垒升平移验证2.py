# -*- coding: utf-8 -*-
"""垒升 vs 平移 柱排分析验证2 - 精确匹配a龙"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')
agg = defaultdict(lambda: [0,0,0])
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
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,14,26,30,43])
    df.columns = ['DXAB','柱排','日ZA','日ZC','次日高幅','上符串','顶型']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['顶型'] = df['顶型'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['触顶'] = df['上符串'].str.endswith('A')
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['未来5天≥5%'] = (df['未来5天高幅'] >= 5).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    sub['prev_ZA'] = sub['日ZA'].shift(1)
    sub['首上破DJA'] = (sub['日ZA'] > 0) & (sub['prev_ZA'] <= 0)
    # 精确a龙: 顶型=='a龙' (触顶的龙)
    sub['a龙'] = sub['顶型']=='a龙'
    sub['跌孕'] = sub['柱排类']=='跌反孕'
    sub['a龙跌孕'] = sub['a龙'] & sub['跌孕']
    sub['阳阴阳'] = sub['柱排类'].isin(['连后吞','吞吞'])
    sub['连阳'] = sub['柱排类']=='升连'
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    for t in [True, False]:
        add(f'升连_触顶={t}', sub[(sub['柱排类']=='升连') & (sub['触顶']==t)])
    for c in ['跌反孕','跌吞','跌连']:
        add(c, sub[sub['柱排类']==c])
    add('升反孕', sub[sub['柱排类']=='升反孕'])
    for t in [True, False]:
        add(f'升吞_触顶={t}', sub[(sub['柱排类']=='升吞') & (sub['触顶']==t)])
    add('a龙跌孕', sub[sub['a龙跌孕']])
    add('阳阴阳', sub[sub['阳阴阳']])
    add('首上破DJA', sub[sub['首上破DJA']])
    add('连阳', sub[sub['连阳']])
    add('基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('垒升 vs 平移 柱排分析（甲乙DXZA>0己，DXZC>0，精确a龙）')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg.items():
    if n >= 1000:
        rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<18}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<18}{n:>10}{p3:>10.2f}{p5:>10.2f}")
