# -*- coding: utf-8 -*-
"""问题4深入：转跌信号（阴阳阴）广义分析
用户提出的3种具体组合（跌吞+升孕+跌吞等）经前序验证样本≈0（因跌吞/升孕/升吞是稀有单柱形态）
本脚本验证广义阴阳阴（跌排-升排-跌排）的真实分布与转跌能力
"""
import pandas as pd, glob, sys
from collections import defaultdict, Counter
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def classify_zp(v):
    v = str(v)
    if '尾连' in v:
        if v.startswith('升'): return '升连'
        if v.startswith('跌'): return '跌连'
        return '人连'
    if '尾吞' in v:
        if v.startswith('升'): return '升吞'
        if v.startswith('跌'): return '跌吞'
        return '人吞'
    if '尾反孕' in v:
        if v.startswith('升'): return '升孕'
        if v.startswith('跌'): return '跌孕'
        return '人孕'
    if '连后吞' in v: return '连后吞'
    if '吞吞' in v: return '吞吞'
    if '孕孕' in v: return '孕孕'
    return '其他'

def yinyang(zp_cls):
    """柱排 -> 阴阳归类"""
    if zp_cls in ('跌吞','跌孕','跌连'): return '阴'
    if zp_cls in ('升吞','升孕','升连'): return '阳'
    return '其他'

# 3连序列 -> [n, 次日P3, 5天P3, 次日均高幅, 次日ZA<0, 3天ZA<0]
agg_seq = defaultdict(lambda: [0,0,0,0.0,0,0])
# 阴阳模式 -> [n, 次日P3, 次日均高幅, 次日ZA<0]
agg_mode = defaultdict(lambda: [0,0,0.0,0])
# 详细: 阴-阳-阴 子类型
agg_yyy_sub = defaultdict(lambda: [0,0,0.0,0,0])
# 对照: 全部3连
all_3 = [0,0,0.0,0]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[9,10,13,26])
    df.columns = ['DXAB','柱排','日ZA','次日高幅']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['阴阳'] = df['柱排类'].apply(yinyang)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)
    df['3天ZA负'] = df['ZA负'].rolling(3, min_periods=1).max().shift(-2).fillna(0).astype(int)

    zp = df['柱排类'].values
    yy = df['阴阳'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    zan = df['ZA负'].values
    za3 = df['3天ZA负'].values
    n = len(df)

    for j in range(n-2):
        seq = (zp[j], zp[j+1], zp[j+2])
        mode = (yy[j], yy[j+1], yy[j+2])
        # 3连序列明细
        a = agg_seq[seq]
        a[0] += 1; a[1] += p3[j+2]; a[2] += p5[j+2]; a[3] += hf[j+2]; a[4] += zan[j+2]; a[5] += za3[j+2]
        # 阴阳模式
        m = agg_mode[mode]
        m[0] += 1; m[1] += p3[j+2]; m[2] += hf[j+2]; m[3] += zan[j+2]
        # 阴-阳-阴 子类型（用户关注的）
        if mode == ('阴','阳','阴'):
            b = agg_yyy_sub[seq]
            b[0] += 1; b[1] += p3[j+2]; b[2] += hf[j+2]; b[3] += zan[j+2]; b[4] += za3[j+2]
        # 全部3连
        all_3[0] += 1; all_3[1] += p3[j+2]; all_3[2] += hf[j+2]; all_3[3] += zan[j+2]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q4: 阴阳模式分布（3连）')
print('='*70)
print(f"{'模式':<14}{'样本':>10}{'次日P3%':>10}{'次日均高幅':>10}{'次日ZA<0%':>10}")
for mode in [('阴','阳','阴'),('阴','阳','阳'),('阳','阳','阴'),('阳','阴','阴'),('阳','阴','阳'),
             ('阴','阴','阳'),('阴','阴','阴'),('阳','阳','阳'),('其他','阳','阴'),('阴','阳','其他')]:
    m = agg_mode[mode]
    if m[0] > 0:
        print(f"{''.join(mode):<14}{m[0]:>10}{m[1]/m[0]*100:>10.2f}{m[2]/m[0]:>10.2f}{m[3]/m[0]*100:>10.2f}")
print(f"\n全部3连: n={all_3[0]}, 次日P3={all_3[1]/all_3[0]*100:.2f}%, 次日均高幅={all_3[2]/all_3[0]:.2f}, 次日ZA<0={all_3[3]/all_3[0]*100:.2f}%")

print('\n' + '='*70)
print('Q4: 阴-阳-阴 子类型（用户关注的转跌信号）')
print('='*70)
print(f"{'序列':<28}{'样本':>8}{'次日P3%':>9}{'次日均高幅':>10}{'次日ZA<0%':>10}{'3天ZA<0%':>10}")
rows = sorted(agg_yyy_sub.items(), key=lambda x: -x[1][0])
for seq, b in rows:
    if b[0] >= 100:
        print(f"{' '.join(seq):<28}{b[0]:>8}{b[1]/b[0]*100:>9.2f}{b[2]/b[0]:>10.2f}{b[3]/b[0]*100:>10.2f}{b[4]/b[0]*100:>10.2f}")

# 用户3个具体组合确认
print('\n' + '='*70)
print('Q4: 用户提出的3个具体组合样本量确认')
print('='*70)
targets = [('跌吞','升孕','跌吞'), ('跌孕','升孕','跌吞'), ('跌孕','升吞','跌孕')]
for t in targets:
    b = agg_seq[t]
    print(f"  {'+'.join(t)}: n={b[0]}")
