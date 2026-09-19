# -*- coding: utf-8 -*-
"""
垒升 vs 平移 柱排分析验证（甲乙DXZA>0己，DXZC>0）
========================================
用户理论框架:
  垒升(获利柱排): 升连(触顶时)、连阳、龙a跌孕、阳阴阳、首上破DJA
  平移(不获利柱排): 跌孕/跌吞/跌连、升孕、升吞/首个升连不触顶
  操作含义: 出现阴柱(跌吞/跌连)没必要介入，后续可能是平移

验证指标:
  垒升 = 未来5天冲高≥3% (获利)
  平移 = 未来5天冲高<3% (不获利)

数据: 昭明算展/谕组日/谕组日_*.csv（GBK）
权威列映射: 9=DXAB护型, 10=柱排, 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 43=顶型
"""
import pandas as pd, glob, sys, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 聚合容器: 类别 -> [n, 未来5天冲高≥3%, 未来5天冲高≥5%]
agg = defaultdict(lambda: [0,0,0])

def classify_zp(v):
    """柱排分类"""
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
    # 未来5天最大高幅(文件内rolling，跨文件会漏但占比小)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['未来5天≥3%'] = (df['未来5天高幅'] >= 3).astype(int)
    df['未来5天≥5%'] = (df['未来5天高幅'] >= 5).astype(int)
    # 甲乙DXZA>0己 且 DXZC>0
    mask = (df['日ZC'] > 0) & (df['护型码'].isin(['a','b','r']))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['柱排类'] = sub['柱排'].apply(classify_zp)
    # 首上破DJA: 日ZA从≤0变为>0 (文件内shift)
    sub['prev_ZA'] = sub['日ZA'].shift(1)
    sub['首上破DJA'] = (sub['日ZA'] > 0) & (sub['prev_ZA'] <= 0)
    # 龙a跌孕: 顶型含'龙'且柱排类=跌反孕(跌孕)
    sub['龙a'] = sub['顶型'].str.contains('龙', na=False)
    sub['跌孕'] = sub['柱排类']=='跌反孕'
    sub['龙a跌孕'] = sub['龙a'] & sub['跌孕']
    # 阳阴阳: 柱排类=连后吞 或 吞吞
    sub['阳阴阳'] = sub['柱排类'].isin(['连后吞','吞吞'])
    # 连阳: 柱排类=升连
    sub['连阳'] = sub['柱排类']=='升连'
    # 分类统计
    def add(cls, grp):
        a = agg[cls]
        a[0]+=len(grp); a[1]+=grp['未来5天≥3%'].sum(); a[2]+=grp['未来5天≥5%'].sum()
    # 升连(触顶 vs 不触顶)
    for t in [True, False]:
        g = sub[(sub['柱排类']=='升连') & (sub['触顶']==t)]
        add(f'升连_触顶={t}', g)
    # 跌孕/跌吞/跌连
    for c in ['跌反孕','跌吞','跌连']:
        add(f'{c}', sub[sub['柱排类']==c])
    # 升孕
    add('升反孕', sub[sub['柱排类']=='升反孕'])
    # 升吞(触顶 vs 不触顶)
    for t in [True, False]:
        g = sub[(sub['柱排类']=='升吞') & (sub['触顶']==t)]
        add(f'升吞_触顶={t}', g)
    # 龙a跌孕
    add('龙a跌孕', sub[sub['龙a跌孕']])
    # 阳阴阳
    add('阳阴阳', sub[sub['阳阴阳']])
    # 首上破DJA
    add('首上破DJA', sub[sub['首上破DJA']])
    # 连阳
    add('连阳', sub[sub['连阳']])
    # 基线
    add('基线(甲乙己ZC>0)', sub)
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('垒升 vs 平移 柱排分析（甲乙DXZA>0己，DXZC>0）')
print('='*70)
rows = []
for cls, (n, p3, p5) in agg.items():
    if n >= 1000:
        rows.append((cls, n, p3/n*100, p5/n*100))
rows.sort(key=lambda r: -r[2])
print(f"{'类别':<18}{'样本':>10}{'5天≥3%':>10}{'5天≥5%':>10}")
for cls, n, p3, p5 in rows:
    print(f"{cls:<18}{n:>10}{p3:>10.2f}{p5:>10.2f}")
