# -*- coding: utf-8 -*-
"""
柱排深化分析: 人排内部反直觉 + 升排×甲组合
========================================
课题1: 人排内部 (跌)人(61.46%) > (人)人(60.58%) > (升)人(57.97%) 反直觉
  验证: 人排内部按尾柱形态细分，看(跌)人为何触顶概率高
课题2: 升排×甲 74.13% 最强组合
  验证: 升排×甲 按尾柱形态/并符天数细分，找最强子组合

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
    v = str(v)
    if v.startswith('升'): return '升排'
    elif v.startswith('跌'): return '跌排'
    elif v.startswith('(升)人'): return '(升)人'
    elif v.startswith('(跌)人'): return '(跌)人'
    elif v.startswith('(人)人'): return '(人)人'
    else: return '首柱'

def classify_tail(v):
    v = str(v)
    if '尾连' in v: return '尾连'
    elif '尾吞' in v: return '尾吞'
    elif '尾反孕' in v: return '尾反孕'
    elif '连后吞' in v: return '连后吞'
    elif '吞吞' in v: return '吞吞'
    elif '孕孕' in v: return '孕孕'
    else: return '其他'

# 聚合容器
agg_ren_tail = defaultdict(lambda: [0,0,0])   # 人排内部×尾柱形态->[n,10天触顶,触顶后P3]
agg_shengjia_tail = defaultdict(lambda: [0,0,0]) # 升排×甲×尾柱形态->[n,10天触顶,触顶后P3]
agg_shengjia_dur = defaultdict(lambda: [0,0,0])  # 升排×甲×并符天数->[n,10天触顶,触顶后P3]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,14,26,30])
    df.columns = ['DXAB','柱排','日ZA','日ZC','次日高幅','上符串']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['柱排','次日高幅'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['触顶'] = df['上符串'].str.endswith('A').astype(int)
    df['未来10天触顶'] = df['触顶'].rolling(10, min_periods=1).max().shift(-9).fillna(0).astype(int)
    mask = (df['日ZC'] > 25) & (~df['上符串'].str.endswith('A'))
    sub = df[mask]
    if sub.empty: continue
    sub = sub.copy()
    sub['cls_first'] = sub['柱排'].apply(classify_first)
    sub['cls_tail'] = sub['柱排'].apply(classify_tail)
    sub['P3'] = (sub['次日高幅'] >= 3).astype(int)
    sub_touch = sub[sub['未来10天触顶']==1]
    # 人排内部×尾柱形态
    ren = sub[sub['cls_first'].isin(['(升)人','(跌)人','(人)人'])]
    for (c1, c2), grp in ren.groupby(['cls_first','cls_tail']):
        a = agg_ren_tail[(c1,c2)]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    ren_t = sub_touch[sub_touch['cls_first'].isin(['(升)人','(跌)人','(人)人'])]
    for (c1, c2), grp in ren_t.groupby(['cls_first','cls_tail']):
        agg_ren_tail[(c1,c2)][2] += grp['P3'].sum()
    # 升排×甲×尾柱形态
    sj = sub[(sub['cls_first']=='升排') & (sub['护型码']=='a')]
    for c2, grp in sj.groupby('cls_tail'):
        a = agg_shengjia_tail[c2]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    sj_t = sub_touch[(sub_touch['cls_first']=='升排') & (sub_touch['护型码']=='a')]
    for c2, grp in sj_t.groupby('cls_tail'):
        agg_shengjia_tail[c2][2] += grp['P3'].sum()
    # 升排×甲×并符天数(提取Q后的数字)
    for v, grp in sj.groupby('柱排'):
        import re
        m = re.search(r'Q(\d+)', str(v))
        if m:
            dur = int(m.group(1))
            a = agg_shengjia_dur[dur]; a[0]+=len(grp); a[1]+=grp['未来10天触顶'].sum()
    for v, grp in sj_t.groupby('柱排'):
        import re
        m = re.search(r'Q(\d+)', str(v))
        if m:
            dur = int(m.group(1))
            agg_shengjia_dur[dur][2] += grp['P3'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

def show(name, agg):
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
    print(f"{'类别':<16}{'样本':>10}{'10天触顶%':>10}{'触顶后P3%':>10}")
    for cls, n, t, p in rows:
        print(f"{str(cls):<16}{n:>10}{t:>10.2f}{p:>10.2f}")
    if rows:
        t_vals=[r[2] for r in rows]; p_vals=[r[3] for r in rows]
        print(f"  触顶区分度={max(t_vals)-min(t_vals):.1f}pp, 触顶后P3区分度={max(p_vals)-min(p_vals):.1f}pp")

show('课题1: 人排内部 × 尾柱形态 对 未来10天触顶率', agg_ren_tail)
show('课题2: 升排×甲 × 尾柱形态 对 未来10天触顶率', agg_shengjia_tail)
show('课题2: 升排×甲 × 并符天数 对 未来10天触顶率', agg_shengjia_dur)
