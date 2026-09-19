# -*- coding: utf-8 -*-
"""垒升阈值全量遍历：按股票波动水平分组，验证绝对阈值 vs 相对阈值适用性"""
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
# 聚合: 波动水平 -> 阈值类型 -> [n, 5天≥3%]
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
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['均涨幅20'] = df['涨幅'].abs().rolling(20, min_periods=5).mean()
    df['相对涨幅'] = df['涨幅'].abs() / df['均涨幅20'].replace(0, float('nan'))
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    shenglian = sub[sub['柱排类']=='升连']
    if shenglian.empty: continue
    # 按该股20日均涨幅(波动水平)分组
    for wl, grp in shenglian.groupby(pd.cut(shenglian['均涨幅20'], bins=[0,1,2,3,5,100], labels=['<1%','1-2%','2-3%','3-5%','>5%'])):
        # 绝对阈值2%
        g_abs = grp[grp['涨幅'].abs()>=2]
        a = agg[wl]['绝对≥2%']; a[0]+=len(g_abs); a[1]+=g_abs['未来5天≥3%'].sum()
        g_abs_lt = grp[grp['涨幅'].abs()<2]
        a = agg[wl]['绝对<2%']; a[0]+=len(g_abs_lt); a[1]+=g_abs_lt['未来5天≥3%'].sum()
        # 相对阈值2倍
        g_rel = grp[grp['相对涨幅']>=2]
        a = agg[wl]['相对≥2倍']; a[0]+=len(g_rel); a[1]+=g_rel['未来5天≥3%'].sum()
        g_rel_lt = grp[grp['相对涨幅']<2]
        a = agg[wl]['相对<2倍']; a[0]+=len(g_rel_lt); a[1]+=g_rel_lt['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('按股票波动水平(20日均涨幅)分组：绝对阈值 vs 相对阈值')
print('='*70)
for wl in ['<1%','1-2%','2-3%','3-5%','>5%']:
    if wl not in agg: continue
    print(f'\n--- 波动水平 {wl} ---')
    rows = []
    for t, (n, p3) in agg[wl].items():
        if n >= 500: rows.append((t, n, p3/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'阈值':<12}{'样本':>10}{'5天≥3%':>10}")
    for t, n, p3 in rows:
        print(f"{t:<12}{n:>10}{p3:>10.2f}")
    if len(rows) >= 2:
        abs_hi = [r for r in rows if '绝对≥' in r[0]]
        abs_lo = [r for r in rows if '绝对<' in r[0]]
        rel_hi = [r for r in rows if '相对≥' in r[0]]
        rel_lo = [r for r in rows if '相对<' in r[0]]
        if abs_hi and abs_lo:
            print(f"  绝对阈值区分度 = {abs_hi[0][2]-abs_lo[0][2]:.1f}pp")
        if rel_hi and rel_lo:
            print(f"  相对阈值区分度 = {rel_hi[0][2]-rel_lo[0][2]:.1f}pp")
