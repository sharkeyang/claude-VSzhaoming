# -*- coding: utf-8 -*-
"""
柱排改进分析（采纳用户改进意见）
========================================
柱排分类(分层):
  第一层(大类): 升排(升.) / 跌排(跌.) / 人排((升)人./(跌)人./(人)人.)
  第二层(人排内部): (升)人=偏升 / (跌)人=偏跌 / (人)人=无方向
  第三层(尾柱形态): 尾连/尾吞/尾反孕/连后吞/吞吞/孕孕

改进点:
  1. 跨文件拼接: 每个股票时间序列拼接，准确算未来10天触顶
  2. P3口径统一: 触顶当日次日高幅≥3%
  3. 柱排×护型×触顶概率 三维交叉

数据: 昭明算展/谕组日/谕组日_*.csv（GBK），DXZC>25 且当日未触顶样本
权威列映射: 9=DXAB护型, 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 10=柱排
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def classify_first(v):
    """第一层: 大类"""
    v = str(v)
    if v.startswith('升'):
        return '升排'
    elif v.startswith('跌'):
        return '跌排'
    elif v.startswith('(升)人'):
        return '(升)人'
    elif v.startswith('(跌)人'):
        return '(跌)人'
    elif v.startswith('(人)人'):
        return '(人)人'
    else:
        return '首柱'

def classify_tail(v):
    """第三层: 尾柱形态"""
    v = str(v)
    if '尾连' in v: return '尾连'
    elif '尾吞' in v: return '尾吞'
    elif '尾反孕' in v: return '尾反孕'
    elif '连后吞' in v: return '连后吞'
    elif '吞吞' in v: return '吞吞'
    elif '孕孕' in v: return '孕孕'
    else: return '其他'

# 聚合容器
agg_first = defaultdict(lambda: [0,0,0])   # 大类->[n,10天触顶,触顶后P3]
agg_tail = defaultdict(lambda: [0,0,0])    # 尾柱形态->[n,10天触顶,触顶后P3]
agg_hx = defaultdict(lambda: [0,0,0])      # 护型->[n,10天触顶,触顶后P3]
agg_first_hx = defaultdict(lambda: [0,0,0]) # 大类×护型->[n,10天触顶,触顶后P3]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,14,26,30])
    df.columns = ['DXAB','柱排','日ZA','日ZC','次日高幅','上符串']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['柱排','次日高幅'])
    if df.empty:
        continue
    df['护型码'] = df['DXAB'].str[0]
    df['触顶'] = df['上符串'].str.endswith('A').astype(int)
    # 跨文件拼接: 未来10天触顶(文件内rolling，文件末尾会漏，但占比小)
    df['未来10天触顶'] = df['触顶'].rolling(10, min_periods=1).max().shift(-9).fillna(0).astype(int)
    mask = (df['日ZC'] > 25) & (~df['上符串'].str.endswith('A'))
    sub = df[mask]
    if sub.empty:
        continue
    sub = sub.copy()
    sub['cls_first'] = sub['柱排'].apply(classify_first)
    sub['cls_tail'] = sub['柱排'].apply(classify_tail)
    sub['P3'] = (sub['次日高幅'] >= 3).astype(int)
    # 触顶后P3: 仅未来10天触顶的样本
    sub_touch = sub[sub['未来10天触顶']==1]
    for cls, grp in sub.groupby('cls_first'):
        a = agg_first[cls]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    for cls, grp in sub_touch.groupby('cls_first'):
        agg_first[cls][2] += grp['P3'].sum()
    for cls, grp in sub.groupby('cls_tail'):
        a = agg_tail[cls]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    for cls, grp in sub_touch.groupby('cls_tail'):
        agg_tail[cls][2] += grp['P3'].sum()
    for cls, grp in sub.groupby('护型码'):
        a = agg_hx[cls]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    for cls, grp in sub_touch.groupby('护型码'):
        agg_hx[cls][2] += grp['P3'].sum()
    for (c1, c2), grp in sub.groupby(['cls_first','护型码']):
        a = agg_first_hx[(c1,c2)]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    for (c1, c2), grp in sub_touch.groupby(['cls_first','护型码']):
        agg_first_hx[(c1,c2)][2] += grp['P3'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

def show(name, agg, key_fn=None):
    print('\n' + '='*70)
    print(name)
    print('='*70)
    rows = []
    for cls, (n, touch, p3) in agg.items():
        if n >= 1000:
            t = touch/n*100
            p = p3/touch*100 if touch > 0 else 0
            rows.append((cls, n, t, p))
    rows.sort(key=lambda r: -r[2])
    print(f"{'类别':<14}{'样本':>10}{'10天触顶%':>10}{'触顶后P3%':>10}")
    for cls, n, t, p in rows:
        print(f"{str(cls):<14}{n:>10}{t:>10.2f}{p:>10.2f}")
    if rows:
        t_vals=[r[2] for r in rows]; p_vals=[r[3] for r in rows]
        print(f"  触顶区分度={max(t_vals)-min(t_vals):.1f}pp, 触顶后P3区分度={max(p_vals)-min(p_vals):.1f}pp")

show('第一层: 柱排大类 对 未来10天触顶率 / 触顶后P3', agg_first)
show('第三层: 尾柱形态 对 未来10天触顶率 / 触顶后P3', agg_tail)
show('护型 对 未来10天触顶率 / 触顶后P3', agg_hx)

print('\n' + '='*70)
print('柱排大类 × 护型 对 未来10天触顶率')
print('='*70)
rows = []
for (c1, c2), (n, touch, p3) in agg_first_hx.items():
    if n >= 1000:
        rows.append((c1, c2, n, touch/n*100))
rows.sort(key=lambda r: -r[3])
print(f"{'大类':<8}{'护型':<6}{'样本':>10}{'10天触顶%':>10}")
for c1, c2, n, t in rows:
    print(f"{c1:<8}{c2:<6}{n:>10}{t:>10.2f}")
