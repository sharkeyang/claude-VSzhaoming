# -*- coding: utf-8 -*-
"""Q4修正2：单柱阴阳用涨幅列判断（涨幅>0=阳柱, <0=阴柱）
用户指出：阴阳阴是单柱（阴柱+阳柱+阴柱），用涨幅正负判断
验证：单柱阴阳3连模式分布 + 用户3种柱排形态组合
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def bar_yinyang(zf):
    """单柱阴阳：涨幅>0=阳柱, <0=阴柱, =0=平"""
    if zf > 0: return '阳'
    if zf < 0: return '阴'
    return '平'

# 单柱阴阳3连模式 -> [n, 次日P3, 次日均高幅, 次日ZA<0]
agg_mode = defaultdict(lambda: [0,0,0.0,0])
all_3 = [0,0,0.0,0]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,13,26])
    df.columns = ['涨幅','日ZA','次日高幅']
    for c in ['涨幅','日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['涨幅','次日高幅','日ZA'])
    if df.empty: continue
    df['单柱阴阳'] = df['涨幅'].apply(bar_yinyang)
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
print('Q4修正2: 单柱阴阳(涨幅)3连模式分布')
print('='*70)
print(f"{'模式':<14}{'样本':>10}{'次日P3%':>10}{'次日均高幅':>10}{'次日ZA<0%':>10}")
for mode in [('阴','阳','阴'),('阴','阳','阳'),('阳','阳','阴'),('阳','阴','阴'),
             ('阳','阴','阳'),('阴','阴','阳'),('阴','阴','阴'),('阳','阳','阳')]:
    m = agg_mode[mode]
    if m[0] > 0:
        print(f"{''.join(mode):<14}{m[0]:>10}{m[1]/m[0]*100:>10.2f}{m[2]/m[0]:>10.2f}{m[3]/m[0]*100:>10.2f}")
print(f"\n全部3连: n={all_3[0]}, 次日P3={all_3[1]/all_3[0]*100:.2f}%, 次日均高幅={all_3[2]/all_3[0]:.2f}, 次日ZA<0={all_3[3]/all_3[0]*100:.2f}%")