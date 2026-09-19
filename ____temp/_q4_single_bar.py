# -*- coding: utf-8 -*-
"""Q4修正：单柱阴阳（阴柱+阳柱+阴柱）验证
用户指出：阴阳阴是单柱（阴柱+阳柱+阴柱），不是柱排（跌排/升排）
单柱阴阳 = 柱排字符串前缀 (跌)=阴柱 / (升)=阳柱
验证用户提出的3种组合 + 广义单柱阴阳阴分布
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def single_bar_yinyang(v):
    """单柱阴阳：前缀 (跌)/跌=阴柱, (升)/升=阳柱, (人)/人=人柱"""
    v = str(v)
    if v.startswith('(跌)') or v.startswith('跌'): return '阴'
    if v.startswith('(升)') or v.startswith('升'): return '阳'
    if v.startswith('(人)') or v.startswith('人'): return '人'
    return '其他'

# 单柱阴阳3连模式 -> [n, 次日P3, 次日均高幅, 次日ZA<0]
agg_mode = defaultdict(lambda: [0,0,0.0,0])
# 用户3种组合（用单柱阴阳 + 柱排形态）
# 用户组合是柱排形态级：跌吞+升孕+跌吞 等
# 先看单柱阴阳阴的分布
all_3 = [0,0,0.0,0]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,13,26])
    df.columns = ['柱排','日ZA','次日高幅']
    for c in ['日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['次日高幅','日ZA'])
    if df.empty: continue
    df['单柱阴阳'] = df['柱排'].apply(single_bar_yinyang)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)

    yy = df['单柱阴阳'].values
    p3 = df['P3'].values
    hf = df['次日高幅'].values
    zan = df['ZA负'].values
    n = len(df)

    for j in range(n-2):
        mode = (yy[j], yy[j+1], yy[j+2])
        m = agg_mode[mode]
        m[0] += 1; m[1] += p3[j+2]; m[2] += hf[j+2]; m[3] += zan[j+2]
        all_3[0] += 1; all_3[1] += p3[j+2]; all_3[2] += hf[j+2]; all_3[3] += zan[j+2]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q4修正: 单柱阴阳3连模式分布')
print('='*70)
print(f"{'模式':<14}{'样本':>10}{'次日P3%':>10}{'次日均高幅':>10}{'次日ZA<0%':>10}")
for mode in [('阴','阳','阴'),('阴','阳','阳'),('阳','阳','阴'),('阳','阴','阴'),
             ('阳','阴','阳'),('阴','阴','阳'),('阴','阴','阴'),('阳','阳','阳')]:
    m = agg_mode[mode]
    if m[0] > 0:
        print(f"{''.join(mode):<14}{m[0]:>10}{m[1]/m[0]*100:>10.2f}{m[2]/m[0]:>10.2f}{m[3]/m[0]*100:>10.2f}")
print(f"\n全部3连: n={all_3[0]}, 次日P3={all_3[1]/all_3[0]*100:.2f}%, 次日均高幅={all_3[2]/all_3[0]:.2f}, 次日ZA<0={all_3[3]/all_3[0]*100:.2f}%")