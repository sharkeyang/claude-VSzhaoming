# -*- coding: utf-8 -*-
"""
MC3.3.3 日等型 高波池全量重跑.py
================================
重跑 MC3.3.3_研究日等型.md 的核心数据（§1.2 下日冲高概率）
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

# 日等型分类（VBA末位逻辑）
def get_dengji(dtza, last_char):
    if dtza == 1:
        return '等1'
    elif dtza == -1:
        return '等5'
    elif dtza >= 2:
        if last_char in 'AB':
            return '等3'
        else:  # CDEF
            return '等2'
    elif dtza <= -2:
        if last_char in 'EF':
            return '等7'
        else:  # ABCD
            return '等6'
    return '等0'

# 聚合器
# agg[等型] = {'n':0, 'n_ge0':0, 'n_ge1':0, 'n_ge2':0, 'n_ge3':0, 'n_ge5':0, 'sum_hr':0, 'sum_lr':0, 'n_ge2_days':0}
agg = defaultdict(lambda: {'n':0, 'n_ge0':0, 'n_ge1':0, 'n_ge2':0, 'n_ge3':0, 'n_ge5':0, 'sum_hr':0.0, 'sum_lr':0.0, 'n_ge2_days':0})
agg['基准'] = agg['基准'].copy()

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
        lr = df['低幅'].astype(float).values if '低幅' in df.columns else np.zeros(len(df))
        next_hr = df['次日高幅'].astype(float).values
    except:
        continue

    for j in range(len(df) - 1):
        if next_hr[j] <= -99:
            continue
        last_char = moshi[j][-1] if len(moshi[j]) > 0 else '?'
        dj = get_dengji(dtza[j], last_char)

        # 基准
        agg['基准']['n'] += 1
        if next_hr[j] >= 0: agg['基准']['n_ge0'] += 1
        if next_hr[j] >= 1: agg['基准']['n_ge1'] += 1
        if next_hr[j] >= 2: agg['基准']['n_ge2'] += 1
        if next_hr[j] >= 3: agg['基准']['n_ge3'] += 1
        if next_hr[j] >= 5: agg['基准']['n_ge5'] += 1
        agg['基准']['sum_hr'] += next_hr[j]

        # 各等型
        agg[dj]['n'] += 1
        if next_hr[j] >= 0: agg[dj]['n_ge0'] += 1
        if next_hr[j] >= 1: agg[dj]['n_ge1'] += 1
        if next_hr[j] >= 2: agg[dj]['n_ge2'] += 1
        if next_hr[j] >= 3: agg[dj]['n_ge3'] += 1
        if next_hr[j] >= 5: agg[dj]['n_ge5'] += 1
        agg[dj]['sum_hr'] += next_hr[j]

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

# 输出
print('\n' + '='*80)
print('§1.2.1 分类分布（6等）')
print('='*80)
print(f'{"分类":<6s} {"样本":>12s} {"占比":>8s}')
print('-'*30)
total = agg['基准']['n']
for dj in ['等1','等2','等3','等5','等6','等7']:
    a = agg[dj]
    print(f'{dj:<6s} {a["n"]:>12,d} {a["n"]/total*100:>7.1f}%')

print('\n' + '='*80)
print('§1.2.2 下日冲高≥0%~≥5% 逐层对比')
print('='*80)
print(f'{"分类":<6s} {"样本":>12s} {"≥0%":>8s} {"≥1%":>8s} {"≥2%":>8s} {"≥3%":>8s} {"≥5%":>8s}')
print('-'*60)
for dj in ['等1','等2','等3','等5','等6','等7']:
    a = agg[dj]
    if a['n'] == 0: continue
    print(f'{dj:<6s} {a["n"]:>12,d} {a["n_ge0"]/a["n"]*100:>7.1f}% {a["n_ge1"]/a["n"]*100:>7.1f}% {a["n_ge2"]/a["n"]*100:>7.1f}% {a["n_ge3"]/a["n"]*100:>7.1f}% {a["n_ge5"]/a["n"]*100:>7.1f}%')
b = agg['基准']
print(f'{"基准":<6s} {b["n"]:>12,d} {b["n_ge0"]/b["n"]*100:>7.1f}% {b["n_ge1"]/b["n"]*100:>7.1f}% {b["n_ge2"]/b["n"]*100:>7.1f}% {b["n_ge3"]/b["n"]*100:>7.1f}% {b["n_ge5"]/b["n"]*100:>7.1f}%')

# 保存
with open('____temp/日等型_高波池_基础.txt', 'w', encoding='utf-8') as f:
    f.write('§1.2.1 分类分布\n')
    for dj in ['等1','等2','等3','等5','等6','等7']:
        a = agg[dj]
        f.write(f'{dj},{a["n"]},{a["n"]/total*100:.1f}%\n')
    f.write('\n§1.2.2 下日冲高\n')
    for dj in ['等1','等2','等3','等5','等6','等7','基准']:
        a = agg[dj]
        f.write(f'{dj},{a["n"]},{a["n_ge0"]/a["n"]*100:.1f}%,{a["n_ge1"]/a["n"]*100:.1f}%,{a["n_ge2"]/a["n"]*100:.1f}%,{a["n_ge3"]/a["n"]*100:.1f}%,{a["n_ge5"]/a["n"]*100:.1f}%\n')
print('\n结果已保存: ____temp/日等型_高波池_基础.txt')