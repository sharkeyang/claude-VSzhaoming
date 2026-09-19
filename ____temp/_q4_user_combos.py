# -*- coding: utf-8 -*-
"""Q4修正3：验证用户提出的3种阴阳阴形态组合
用户组合（单柱形态序列，并符字母）：
1. 跌吞+升孕+跌吞 = V o V  （代表向下，类似跌连）
2. 跌孕+升孕+跌吞 = v o V  （代表顶部转向下）
3. 跌孕+升吞+跌孕 = v O v  （更多代表向上）
并符字母：Q=升连 O=升吞 o=升孕 W=跌连 V=跌吞 v=跌孕
柱排字符串形态部分 = 并符字母序列，如 '跌.尾反孕oVo' 形态='oVo'
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def form_letters(v):
    """提取柱排字符串的形态字母序列（. 后面的部分，去掉前缀）"""
    v = str(v)
    if '.' in v:
        return v.split('.')[1]
    return v

# 用户3种组合 -> [n, 次日P3, 次日均高幅, 次日ZA<0, 3天ZA<0]
targets = {
    '跌吞+升孕+跌吞(VoV)': 'VoV',
    '跌孕+升孕+跌吞(voV)': 'voV',
    '跌孕+升吞+跌孕(vOv)': 'vOv',
}
agg = {k: [0,0,0.0,0,0] for k in targets}
# 对照：全部阴阳阴（单柱） + 全部3连
agg_yyy = [0,0,0.0,0]
all_3 = [0,0,0.0,0]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,10,13,26])
    df.columns = ['涨幅','柱排','日ZA','次日高幅']
    for c in ['涨幅','日ZA','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['涨幅','次日高幅','日ZA'])
    if df.empty: continue
    df['形态'] = df['柱排'].apply(form_letters)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)
    df['3天ZA负'] = df['ZA负'].rolling(3, min_periods=1).max().shift(-2).fillna(0).astype(int)

    zf = df['涨幅'].values
    form = df['形态'].values
    p3 = df['P3'].values
    hf = df['次日高幅'].values
    zan = df['ZA负'].values
    za3 = df['3天ZA负'].values
    n = len(df)

    for j in range(n-2):
        # 单柱阴阳（涨幅）
        y0 = '阳' if zf[j]>0 else ('阴' if zf[j]<0 else '平')
        y1 = '阳' if zf[j+1]>0 else ('阴' if zf[j+1]<0 else '平')
        y2 = '阳' if zf[j+2]>0 else ('阴' if zf[j+2]<0 else '平')
        # 3连形态字母（取每根单柱的形态）
        f0, f1, f2 = form[j], form[j+1], form[j+2]
        # 用户组合匹配：形态字母序列
        for k, pat in targets.items():
            if f0 == pat[0] and f1 == pat[1] and f2 == pat[2]:
                a = agg[k]
                a[0] += 1; a[1] += p3[j+2]; a[2] += hf[j+2]; a[3] += zan[j+2]; a[4] += za3[j+2]
        # 全部阴阳阴（单柱）
        if y0=='阴' and y1=='阳' and y2=='阴':
            agg_yyy[0] += 1; agg_yyy[1] += p3[j+2]; agg_yyy[2] += hf[j+2]; agg_yyy[3] += zan[j+2]
        all_3[0] += 1; all_3[1] += p3[j+2]; all_3[2] += hf[j+2]; all_3[3] += zan[j+2]

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q4修正3: 用户3种阴阳阴形态组合')
print('='*70)
print(f"{'组合':<24}{'样本':>8}{'次日P3%':>9}{'次日均高幅':>10}{'次日ZA<0%':>10}{'3天ZA<0%':>10}")
for k in targets:
    a = agg[k]
    if a[0] > 0:
        print(f"{k:<24}{a[0]:>8}{a[1]/a[0]*100:>9.2f}{a[2]/a[0]:>10.2f}{a[3]/a[0]*100:>10.2f}{a[4]/a[0]*100:>10.2f}")
    else:
        print(f"{k:<24}{a[0]:>8}  (样本为0)")

print(f"\n全部阴阳阴(单柱): n={agg_yyy[0]}, 次日P3={agg_yyy[1]/agg_yyy[0]*100:.2f}%, 次日均高幅={agg_yyy[2]/agg_yyy[0]:.2f}, 次日ZA<0={agg_yyy[3]/agg_yyy[0]*100:.2f}%")
print(f"全部3连: n={all_3[0]}, 次日P3={all_3[1]/all_3[0]*100:.2f}%, 次日均高幅={all_3[2]/all_3[0]:.2f}, 次日ZA<0={all_3[3]/all_3[0]*100:.2f}%")