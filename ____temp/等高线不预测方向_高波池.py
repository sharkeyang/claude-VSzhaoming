# -*- coding: utf-8 -*-
"""
MC3.3.3 §1.2.4 等高线不预测方向 高波池全量重跑.py
================================================
重跑 §1.2.4 等高线不预测方向数据（下柱高幅/低幅）
口径：高波池（Qic+Qim+Qit），全量文件
"""
import pandas as pd, numpy as np, glob, json, time, warnings, os, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
高波池 = {'Qic', 'Qim', 'Qit'}

with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(glob.glob(DATA_DIR + '/谕组日_*.csv'))

def get_dengji(dtza, last_char):
    if dtza == 1: return '等1'
    elif dtza == -1: return '等5'
    elif dtza >= 2:
        return '等3' if last_char in 'AB' else '等2'
    elif dtza <= -2:
        return '等7' if last_char in 'EF' else '等6'
    return '等0'

agg = defaultdict(lambda: {'n':0, 'n_ge2':0, 'sum_hr':0.0, 'sum_lr':0.0})

t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  {i}/{len(files)}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5:
            continue
    except:
        continue
    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池:
        continue

    try:
        dtza = df['日ZA'].astype(int).values
        moshi = df['中符串'].astype(str).values
        hr = df['高幅'].astype(float).values
        low = df['低'].astype(float).values
        close = df['收'].astype(float).values
        next_hr = df['次日高幅'].astype(float).values
    except:
        continue

    for j in range(len(df) - 1):
        if next_hr[j] <= -99:
            continue
        last_char = moshi[j][-1] if len(moshi[j]) > 0 else '?'
        dj = get_dengji(dtza[j], last_char)

        # 低幅 = (低/前收 - 1)*100
        if j > 0 and close[j-1] > 0 and low[j] > 0:
            lr_val = (low[j]/close[j-1] - 1) * 100
        else:
            lr_val = 0

        agg[dj]['n'] += 1
        if next_hr[j] >= 2: agg[dj]['n_ge2'] += 1
        agg[dj]['sum_hr'] += next_hr[j]
        agg[dj]['sum_lr'] += lr_val

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

print('\n' + '='*80)
print('§1.2.4 等高线不预测方向')
print('='*80)
print(f'{"分类":<6s} {"样本":>10s} {"下柱≥2%":>8s} {"下柱高幅均值":>10s} {"下柱低幅均值":>10s} {"幅度比":>6s} {"期望收益/天":>10s}')
print('-'*70)
for dj in ['等1','等2','等3','等5','等6','等7']:
    a = agg[dj]
    if a['n'] == 0: continue
    ge2 = a['n_ge2']/a['n']*100
    avg_hr = a['sum_hr']/a['n']
    avg_lr = a['sum_lr']/a['n']
    ratio = avg_hr/avg_lr if avg_lr != 0 else 0
    exp = avg_hr - avg_lr
    print(f'{dj:<6s} {a["n"]:>10,d} {ge2:>7.1f}% {avg_hr:>9.2f}% {avg_lr:>9.2f}% {ratio:>5.2f} {exp:>+9.3f}%')

with open('____temp/等高线不预测方向_高波池.txt', 'w', encoding='utf-8') as f:
    f.write('分类,样本,下柱≥2%,下柱高幅均值,下柱低幅均值,幅度比,期望收益/天\n')
    for dj in ['等1','等2','等3','等5','等6','等7']:
        a = agg[dj]
        if a['n'] == 0: continue
        ge2 = a['n_ge2']/a['n']*100
        avg_hr = a['sum_hr']/a['n']
        avg_lr = a['sum_lr']/a['n']
        ratio = avg_hr/avg_lr if avg_lr != 0 else 0
        exp = avg_hr - avg_lr
        f.write(f'{dj},{a["n"]},{ge2:.1f}%,{avg_hr:.2f}%,{avg_lr:.2f}%,{ratio:.2f},{exp:+.3f}%\n')
print('\n结果已保存: ____temp/等高线不预测方向_高波池.txt')