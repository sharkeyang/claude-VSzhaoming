# -*- coding: utf-8 -*-
"""
柱排定义是否需要调整？分析不同柱排分类方式的区分度
========================================
背景: §6.5.1.7 发现柱排对"触顶概率"区分度19.5pp(升排70.6% vs 其他51.1%)，
     但对"触顶后P3"几乎无影响(1.1pp)。⑦.14 显示尾柱形态(尾连/尾吞/尾反孕)有区分。
用户问题: 柱排的定义(首柱类型升/跌/人)是否需要调整？

对比不同柱排分类方式对"未来10天触顶概率"和"触顶后P3"的区分度:
  A. 首柱类型(升/跌/人) - 当前粗分类
  B. 尾柱形态(尾连/尾吞/尾反孕/连后吞/吞吞/孕孕)
  C. 首柱×尾柱组合

数据: 昭明算展/谕组日/谕组日_*.csv（GBK），DXZC>25 且当日未触顶样本
权威列映射: 13=日ZA, 14=日ZC, 26=次日高幅, 30=上符串, 10=柱排
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

agg = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))  # 分类方式->类别->[n,未来10天触顶,触顶后P3]

def classify_zp(v, mode):
    v = str(v)
    if v in ('柱排', '首柱') or v.startswith('首柱'):
        return '首柱'
    if v.startswith('升.'):
        first = '升'
    elif v.startswith('跌.'):
        first = '跌'
    elif v.startswith('(升)人'):
        first = '(升)人'
    elif v.startswith('(跌)人'):
        first = '(跌)人'
    elif v.startswith('(人)人'):
        first = '(人)人'
    else:
        first = '其他'
    if '尾连' in v:
        tail = '尾连'
    elif '尾吞' in v:
        tail = '尾吞'
    elif '尾反孕' in v:
        tail = '尾反孕'
    elif '连后吞' in v:
        tail = '连后吞'
    elif '吞吞' in v:
        tail = '吞吞'
    elif '孕孕' in v:
        tail = '孕孕'
    else:
        tail = '其他'
    if mode == 'first':
        return first
    elif mode == 'tail':
        return tail
    elif mode == 'combo':
        return f'{first}.{tail}'
    return v

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,13,14,26,30])
    df.columns = ['柱排','日ZA','日ZC','次日高幅','上符串']
    df['日ZC'] = pd.to_numeric(df['日ZC'], errors='coerce')
    df['次日高幅'] = pd.to_numeric(df['次日高幅'], errors='coerce')
    df['上符串'] = df['上符串'].astype(str)
    df = df.dropna(subset=['柱排','次日高幅'])
    if df.empty:
        continue
    # 未来10天触顶: 用滚动窗口(文件内)，上符串末位A
    df['触顶'] = df['上符串'].str.endswith('A').astype(int)
    # 未来10天(含当日)是否有触顶
    df['未来10天触顶'] = df['触顶'].rolling(10, min_periods=1).max().shift(-9).fillna(0).astype(int)
    # DXZC>25 且当日未触顶
    mask = (df['日ZC'] > 25) & (~df['上符串'].str.endswith('A'))
    sub = df[mask]
    if sub.empty:
        continue
    for mode in ['first', 'tail', 'combo']:
        sub['cls'] = sub['柱排'].apply(lambda v: classify_zp(v, mode))
        for cls, grp in sub.groupby('cls'):
            a = agg[mode][cls]
            a[0] += len(grp)
            a[1] += grp['未来10天触顶'].sum()
            # 触顶后P3: 仅未来10天触顶的样本，用次日高幅
            a[2] += grp['次日高幅'].apply(lambda x: 1 if x >= 3 else 0).sum()
    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

for mode, name in [('first','A. 首柱类型(升/跌/人)'), ('tail','B. 尾柱形态'), ('combo','C. 首柱×尾柱')]:
    print('\n' + '='*70)
    print(f'{name} 对 未来10天触顶率 / 次日P3 的区分度')
    print('='*70)
    rows = []
    for cls, (n, touch, p3) in agg[mode].items():
        if n >= 1000:
            rows.append((cls, n, touch/n*100, p3/n*100))
    rows.sort(key=lambda r: -r[2])
    print(f"{'类别':<16}{'样本':>10}{'10天触顶%':>10}{'次日P3%':>10}")
    for cls, n, t, p in rows:
        print(f"{cls:<16}{n:>10}{t:>10.2f}{p:>10.2f}")
    if rows:
        t_vals = [r[2] for r in rows]
        p_vals = [r[3] for r in rows]
        print(f"  触顶区分度 = {max(t_vals)-min(t_vals):.1f}pp, P3区分度 = {max(p_vals)-min(p_vals):.1f}pp")
