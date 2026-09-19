# -*- coding: utf-8 -*-
"""验证忠护级(DXCD状态)是否应纳入执念范围 - 不绑定护型"""
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
agg_zhong = defaultdict(lambda: [0,0])   # 忠×护型
agg_trans = defaultdict(lambda: [0,0])   # 忠次日转移
agg_zhong_zp = defaultdict(lambda: [0,0]) # 忠×柱排
agg_zhong_za = defaultdict(lambda: [0,0]) # 忠×DXZA
agg_zhong_bsha = defaultdict(lambda: [0,0]) # 忠×BSHA
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,14,19,26])
    df.columns = ['DXAB','柱排','日ZA','日ZC','BSHA','次日高幅']
    for c in ['日ZA','日ZC','BSHA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['护级'] = df['DXAB'].str[3]
    df['次日护级'] = df['护级'].shift(-1)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['柱排类'] = df['柱排'].apply(classify_zp)
    zhong = df[df['护级']=='忠']
    if zhong.empty: continue
    for hx, g in zhong.groupby('护型码'):
        a = agg_zhong[hx]; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    for nh, g in zhong.groupby(zhong['次日护级']):
        a = agg_trans[nh]; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    for zp, g in zhong.groupby('柱排类'):
        a = agg_zhong_zp[zp]; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    for za, g in zhong.groupby(zhong['日ZA']>0):
        za_label = 'DXZA>0' if za else 'DXZA<0'
        a = agg_zhong_za[za_label]; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    for b, g in zhong.groupby(pd.cut(zhong['BSHA'], bins=[-100,0,2,5,8,100], labels=['<0','0-2','2-5','5-8','>8'])):
        a = agg_zhong_bsha[f'BSHA{b}']; a[0]+=len(g); a[1]+=g['未来5天≥3%'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('1. 忠 × 护型')
print('='*70)
rows = []
for hx, (n, p3) in agg_zhong.items():
    if n >= 1000: rows.append((hx, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'护型':<6}{'样本':>10}{'5天≥3%':>10}")
for hx, n, p3 in rows:
    print(f"{hx:<6}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('2. 忠 次日转移')
print('='*70)
rows = []
total = sum(n for _, (n, _) in agg_trans.items())
for nh, (n, p3) in agg_trans.items():
    if n >= 1000: rows.append((nh, n, n/total*100, p3/n*100))
rows.sort(key=lambda r: -r[1])
print(f"{'次日护级':<6}{'样本':>10}{'占比%':>10}{'5天≥3%':>10}")
for nh, n, pct, p3 in rows:
    print(f"{nh:<6}{n:>10}{pct:>10.2f}{p3:>10.2f}")
print('\n' + '='*70)
print('3. 忠 × 柱排')
print('='*70)
rows = []
for zp, (n, p3) in agg_zhong_zp.items():
    if n >= 1000: rows.append((zp, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'柱排':<10}{'样本':>10}{'5天≥3%':>10}")
for zp, n, p3 in rows:
    print(f"{zp:<10}{n:>10}{p3:>10.2f}")
print('\n' + '='*70)
print('4. 忠 × DXZA')
print('='*70)
for za, (n, p3) in agg_zhong_za.items():
    if n >= 1000:
        print(f"{za}: n={n}, 5天≥3%={p3/n*100:.2f}%")
print('\n' + '='*70)
print('5. 忠 × BSHA')
print('='*70)
rows = []
for b, (n, p3) in agg_zhong_bsha.items():
    if n >= 1000: rows.append((b, n, p3/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'BSHA':<10}{'样本':>10}{'5天≥3%':>10}")
for b, n, p3 in rows:
    print(f"{b:<10}{n:>10}{p3:>10.2f}")
