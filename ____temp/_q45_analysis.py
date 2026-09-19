# -*- coding: utf-8 -*-
"""问题4-5分析
Q4: 转跌信号（阴阳阴类别）—— 3连柱排序列
Q5: DTZA>=4升连后过渡过程（升连->阴阳相间->跌连）
"""
import pandas as pd, glob, sys
from collections import defaultdict
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

# Q4: 阴阳阴3连序列 -> [n, 次日P3, 5天P3, 次日均高幅, 次日DXZA<0, 3天DXZA<0]
q4 = defaultdict(lambda: [0,0,0,0.0,0,0])
# Q4基线: 所有3连序列（中间为升排）
q4_base = [0,0,0,0.0,0,0]

# Q5: 升连链后过渡
q5 = defaultdict(lambda: [0,0,0,0])  # 过渡类型 -> [n, 立即跌连, 阴阳相间后跌连, 最终跌连]
q5_trans = defaultdict(lambda: [0,0,0,0])  # 链末DTZA区间 -> [n, 立即跌连, 阴阳后跌连, 最终跌连]

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[5,9,10,13,14,26])
    df.columns = ['涨幅','DXAB','柱排','日ZA','日ZC','次日高幅']
    for c in ['涨幅','日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DXAB'] = df['DXAB'].astype(str)
    df = df.dropna(subset=['次日高幅','涨幅','日ZA','日ZC'])
    if df.empty: continue
    df['护型码'] = df['DXAB'].str[0]
    df['柱排类'] = df['柱排'].apply(classify_zp)
    df['P3'] = (df['次日高幅']>=3).astype(int)
    df['未来5天高幅'] = df['次日高幅'].rolling(5, min_periods=1).max()
    df['5天P3'] = (df['未来5天高幅']>=3).astype(int)
    df['ZA负'] = (df['日ZA']<0).astype(int)
    df['3天ZA负'] = df['ZA负'].rolling(3, min_periods=1).max().shift(-2).fillna(0).astype(int)

    zp = df['柱排类'].values
    za = df['日ZA'].values
    p3 = df['P3'].values
    p5 = df['5天P3'].values
    hf = df['次日高幅'].values
    zan = df['ZA负'].values
    za3 = df['3天ZA负'].values
    n = len(df)

    # Q4: 3连序列（阴阳阴）
    for j in range(n-2):
        seq = (zp[j], zp[j+1], zp[j+2])
        first_neg = seq[0] in ('跌吞','跌孕','跌连')
        mid_pos = seq[1] in ('升吞','升孕','升连')
        last_neg = seq[2] in ('跌吞','跌孕','跌连')
        if first_neg and mid_pos and last_neg:
            key = f'{seq[0]}+{seq[1]}+{seq[2]}'
            a = q4[key]
            a[0] += 1
            a[1] += p3[j+2]
            a[2] += p5[j+2]
            a[3] += hf[j+2]
            a[4] += zan[j+2]
            a[5] += za3[j+2]
        if mid_pos:
            q4_base[0] += 1
            q4_base[1] += p3[j+2]
            q4_base[2] += p5[j+2]
            q4_base[3] += hf[j+2]
            q4_base[4] += zan[j+2]
            q4_base[5] += za3[j+2]

    # Q5: 升连链后过渡
    j = 0
    while j < n:
        if zp[j] == '升连':
            k = j
            while k < n and zp[k] == '升连':
                k += 1
            length = k - j
            chain_za = za[j:k]
            if length >= 1 and (chain_za >= 4).any():
                end = k - 1
                after = zp[k:k+10]
                if len(after) > 0:
                    immediate_die = after[0] == '跌连'
                    first_die_idx = None
                    for idx, v in enumerate(after):
                        if v == '跌连':
                            first_die_idx = idx
                            break
                    die_final = first_die_idx is not None
                    yinyang_then_die = die_final and first_die_idx >= 1
                    if immediate_die:
                        trans = '立即跌连'
                    elif yinyang_then_die:
                        trans = '阴阳相间后跌连'
                    elif die_final:
                        trans = '直接跌连(无阴阳)'
                    else:
                        trans = '10柱内无跌连'
                    a = q5[trans]
                    a[0] += 1
                    a[1] += int(immediate_die)
                    a[2] += int(yinyang_then_die)
                    a[3] += int(die_final)
                    end_za = za[end]
                    if end_za >= 4:
                        zone = 'DTZA>=4'
                    elif end_za >= 2:
                        zone = 'DTZA2-3'
                    else:
                        zone = 'DTZA<2'
                    b = q5_trans[zone]
                    b[0] += 1
                    b[1] += int(immediate_die)
                    b[2] += int(yinyang_then_die)
                    b[3] += int(die_final)
            j = k
        else:
            j += 1

    if (i+1) % 2000 == 0:
        print(f'  已处理 {i+1}/{len(files)}', flush=True)

print('\n' + '='*70)
print('Q4: 转跌信号（阴阳阴3连序列）')
print('='*70)
print(f"{'序列':<28}{'样本':>8}{'次日P3%':>9}{'5天P3%':>9}{'次日均高幅':>10}{'次日ZA<0%':>10}{'3天ZA<0%':>10}")
rows = sorted(q4.items(), key=lambda x: -x[1][0])
for key, a in rows:
    if a[0] >= 100:
        print(f"{key:<28}{a[0]:>8}{a[1]/a[0]*100:>9.2f}{a[2]/a[0]*100:>9.2f}{a[3]/a[0]:>10.2f}{a[4]/a[0]*100:>10.2f}{a[5]/a[0]*100:>10.2f}")
print(f"\n基线(所有3连序列,中间升排): n={q4_base[0]}, 次日P3={q4_base[1]/q4_base[0]*100:.2f}%, 次日ZA<0={q4_base[4]/q4_base[0]*100:.2f}%")

print('\n' + '='*70)
print('Q5: DTZA>=4升连链后过渡过程')
print('='*70)
print(f"{'过渡类型':<20}{'样本':>8}{'立即跌连%':>10}{'阴阳后跌连%':>12}{'最终跌连%':>10}")
for trans, a in q5.items():
    if a[0] > 0:
        print(f"{trans:<20}{a[0]:>8}{a[1]/a[0]*100:>10.2f}{a[2]/a[0]*100:>12.2f}{a[3]/a[0]*100:>10.2f}")
print(f"\n按链末DTZA区间:")
print(f"{'区间':<12}{'样本':>8}{'立即跌连%':>10}{'阴阳后跌连%':>12}{'最终跌连%':>10}")
for zone, b in q5_trans.items():
    if b[0] > 0:
        print(f"{zone:<12}{b[0]:>8}{b[1]/b[0]*100:>10.2f}{b[2]/b[0]*100:>12.2f}{b[3]/b[0]*100:>10.2f}")
