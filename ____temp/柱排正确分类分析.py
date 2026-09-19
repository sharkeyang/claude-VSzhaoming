# -*- coding: utf-8 -*-
"""
用正确的柱排分类(并符组合)重新分析 §6.5.1.7 数据
========================================
用户澄清: 柱排分类看并符组合，不看首柱:
  升排 = 不含跌连W、跌吞V (可含跌孕v)
  跌排 = 不含升连Q、升吞O (可含升孕o)
  人排 = 排除升排和跌排后剩下的 (同时含升连/升吞 和 跌连/跌吞，或只有孕)

对比: 旧分类(柱排首) vs 新分类(并符组合) 对 未来10天触顶率 / 次日P3 的区分度
数据: 昭明算展/谕组日/谕组日_*.csv（GBK），DXZC>25 且当日未触顶样本
权威列映射: 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 10=柱排
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 并符字符
W, V, Q, O = 'W', 'V', 'Q', 'O'  # 跌连,跌吞,升连,升吞

def classify_new(v):
    """新分类: 看并符组合是否含跌连W/跌吞V 或 升连Q/升吞O"""
    v = str(v)
    if v in ('柱排', '首柱') or v.startswith('首柱'):
        return '首柱'
    has_W = 'W' in v  # 跌连
    has_V = 'V' in v  # 跌吞
    has_Q = 'Q' in v  # 升连
    has_O = 'O' in v  # 升吞
    if not has_W and not has_V:
        return '升排'
    elif not has_Q and not has_O:
        return '跌排'
    else:
        return '人排'

def classify_old(v):
    """旧分类: 柱排首字符"""
    v = str(v)
    if v.startswith('升'):
        return '升排'
    elif v.startswith('跌'):
        return '跌排'
    else:
        return '人排'

agg_new = defaultdict(lambda: [0, 0, 0])  # 新分类->[n,10天触顶,次日P3]
agg_old = defaultdict(lambda: [0, 0, 0])  # 旧分类->[n,10天触顶,次日P3]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,13,14,26,30])
    df.columns = ['柱排','日ZA','日ZC','次日高幅','上符串']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['柱排','次日高幅'])
    if df.empty:
        continue
    df['触顶'] = df['上符串'].str.endswith('A').astype(int)
    df['未来10天触顶'] = df['触顶'].rolling(10, min_periods=1).max().shift(-9).fillna(0).astype(int)
    mask = (df['日ZC'] > 25) & (~df['上符串'].str.endswith('A'))
    sub = df[mask]
    if sub.empty:
        continue
    sub = sub.copy()
    sub['cls_new'] = sub['柱排'].apply(classify_new)
    sub['cls_old'] = sub['柱排'].apply(classify_old)
    sub['P3'] = (sub['次日高幅'] >= 3).astype(int)
    for cls, grp in sub.groupby('cls_new'):
        a = agg_new[cls]
        a[0] += len(grp); a[1] += grp['未来10天触顶'].sum(); a[2] += grp['P3'].sum()
    for cls, grp in sub.groupby('cls_old'):
        a = agg_old[cls]
        a[0] += len(grp); a[1] += grp['未来10天触顶'].sum(); a[2] += grp['P3'].sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

for name, agg in [('旧分类(柱排首)', agg_old), ('新分类(并符组合)', agg_new)]:
    print('\n' + '='*70)
    print(f'{name} 对 未来10天触顶率 / 次日P3 的区分度')
    print('='*70)
    rows = []
    for cls, (n, touch, p3) in agg.items():
        if n >= 1000:
            rows.append((cls, n, touch/n*100, p3/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'类别':<8}{'样本':>10}{'10天触顶%':>10}{'次日P3%':>10}")
    for cls, n, t, p in rows:
        print(f"{cls:<8}{n:>10}{t:>10.2f}{p:>10.2f}")
    if rows:
        t_vals = [r[2] for r in rows]
        p_vals = [r[3] for r in rows]
        print(f"  触顶区分度 = {max(t_vals)-min(t_vals):.1f}pp, P3区分度 = {max(p_vals)-min(p_vals):.1f}pp")
