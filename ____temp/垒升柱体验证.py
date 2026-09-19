# -*- coding: utf-8 -*-
"""
垒升柱体验证：升连按柱体大小(涨幅绝对值)分档，看后续获利
========================================
用户定义: 垒升=升连+柱体明显(非十字星/极小)，不要求触顶
  升连+柱体明显 = 垒升(获利)
  升连+十字星/极小 = 平移(不获利)

验证: 甲乙DXZA>0己，DXZC>0，升连柱按涨幅绝对值分档
数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 5=涨幅, 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅
"""
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
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['未来5天≥5%'] = (df['未来5天高幅'] >= 5).astype(int)
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    sub['涨幅abs'] = sub['涨幅'].abs()
    # 升连柱按涨幅绝对值分档
    shenglian = sub[sub['柱排类']=='升连']
    bins = [0, 0.5, 1, 2, 3, 5, 10, 100]
    labels = ['<0.5','0.5-1','1-2','2-3','3-5','5-10','>10']
    for b, grp in shenglian.groupby(pd.cut(shenglian['涨幅abs'], bins=bins, labels=labels)):
        a = agg[f'升连_涨幅{b}'][0] if False else None
        key = f'升连_涨幅{b}'
        a = agg[key]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    # 基线
    a = agg['基线(甲乙己ZC>0)']; a[0]+=len(sub); a[1]+=sub['未来5天≥3%'].sum(); a[2]+=sub['未来5天≥5%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('垒升柱体验证：升连按涨幅绝对值分档（甲乙DXZA>0己，DXZC>0）')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg.items():
    if n >= 500:
        rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<20}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<20}{n:>10}{p3:>10.2f}{p5:>10.2f}")
