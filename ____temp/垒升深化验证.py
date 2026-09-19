# -*- coding: utf-8 -*-
"""
垒升深化验证（DXZC>0，甲乙DXZA>0己）
========================================
用户理论框架:
  垒升(可介入): 升连(触顶)、连阳、龙a跌孕(不打破升排)、龙a+跌孕+阳柱(帐篷)、阳阴阳、首上破DJA
  平移(不介入): 跌孕/跌吞/跌连、升孕、升吞/首个升连不触顶、跌孕升吞、鼎
  操作: 不要信跌连后升吞/首个升连，可信跌连后阳阴阳/启动结构；帐篷谨慎

验证指标: 未来5天冲高≥3% (垒升=获利高)
数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅, 27=柱型, 30=上符串, 42=BT鼎, 43=顶型
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
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,14,26,27,30,42,43])
    df.columns = ['DXAB','柱排','日ZA','日ZC','次日高幅','柱型','上符串','BT鼎','顶型']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['BT鼎'] = pd.to_numeric(df['BT鼎'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['顶型'] = df['顶型'].astype(str)
    df['柱型'] = df['柱型'].astype(str)
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
    sub['a龙'] = sub['顶型']=='a龙'
    sub['跌孕'] = sub['柱排类']=='跌反孕'
    sub['a龙跌孕'] = sub['a龙'] & sub['跌孕']
    sub['阳阴阳'] = sub['柱排类'].isin(['连后吞','吞吞'])
    sub['连阳'] = sub['柱排类']=='升连'
    sub['鼎'] = sub['BT鼎'] > 0
    sub['启动'] = sub['柱型'].str.contains('启', na=False)
    sub['跌孕升吞'] = sub['柱排类']=='跌反孕'  # 跌孕升吞近似
    # 帐篷: 龙a+跌孕+阳柱(次日阳柱)
    sub['次日阳'] = sub['次日高幅'] > 0
    sub['帐篷'] = sub['a龙跌孕'] & sub['次日阳']
    def add(cls, grp):
        a = agg[cls]; a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    # 升连(触顶 vs 不触顶)
    for t in [True, False]:
        add(f'升连_触顶={t}', sub[(sub['柱排类']=='升连') & (sub['触顶']==t)])
    # 连阳
    add('连阳', sub[sub['连阳']])
    # 龙a跌孕(不打破升排=前柱升排)
    sub['prev_zp'] = sub['柱排类'].shift(1)
    sub['龙a跌孕_前升排'] = sub['a龙跌孕'] & (sub['prev_zp']=='升连')
    sub['龙a跌孕_前非升排'] = sub['a龙跌孕'] & (sub['prev_zp']!='升连')
    add('龙a跌孕_前升排', sub[sub['龙a跌孕_前升排']])
    add('龙a跌孕_前非升排', sub[sub['龙a跌孕_前非升排']])
    # 帐篷
    add('帐篷(龙a跌孕+阳柱)', sub[sub['帐篷']])
    # 阳阴阳
    add('阳阴阳', sub[sub['阳阴阳']])
    # 首上破DJA
    add('首上破DJA', sub[sub['首上破DJA']])
    # 跌孕/跌吞/跌连
    for c in ['跌反孕','跌吞','跌连']:
        add(c, sub[sub['柱排类']==c])
    # 升孕
    add('升反孕', sub[sub['柱排类']=='升反孕'])
    # 升吞(触顶 vs 不触顶)
    for t in [True, False]:
        add(f'升吞_触顶={t}', sub[(sub['柱排类']=='升吞') & (sub['触顶']==t)])
    # 鼎
    add('鼎(BT鼎>0)', sub[sub['鼎']])
    # 跌连后升吞/首个升连
    sub['跌连后'] = (sub['prev_zp']=='跌连')
    add('跌连后升吞', sub[sub['跌连后'] & (sub['柱排类']=='升吞')])
    add('跌连后升连', sub[sub['跌连后'] & (sub['柱排类']=='升连')])
    add('跌连后阳阴阳', sub[sub['跌连后'] & sub['阳阴阳']])
    add('跌连后启动', sub[sub['跌连后'] & sub['启动']])
    # 基线
    add('基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)
print('\n' + '='*70)
print('垒升深化验证（甲乙DXZA>0己，DXZC>0）')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg.items():
    if n >= 500:
        rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<22}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<22}{n:>10}{p3:>10.2f}{p5:>10.2f}")
