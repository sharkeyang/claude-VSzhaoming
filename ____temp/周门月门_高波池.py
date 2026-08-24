# -*- coding: utf-8 -*-
"""
MC3.3.3 周门月门 高波池全量重跑.py
================================
重跑 §2.1 门过滤体系（周门+月门）数据
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

# 周门 = ZC>0 且 DXCD=上
# 月门 = ZE>0
# 聚合器
agg = defaultdict(lambda: {'n':0, 'n_ge2':0, 'n_ge3':0})

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
        ze = df['日ZE'].astype(float).values
        zc = df['日ZC'].astype(float).values
        dxcd = df['DXCD'].astype(str).values
        next_hr = df['次日高幅'].astype(float).values
    except:
        continue

    for j in range(len(df) - 1):
        if next_hr[j] <= -99:
            continue
        cd = dxcd[j][0] if len(dxcd[j]) > 0 else '?'
        zhoumen = zc[j] > 0 and cd == '上'
        yuemen = ze[j] > 0

        # 组合
        if zhoumen and yuemen:
            key = '周门+月门'
        elif zhoumen and not yuemen:
            key = '周门+非月门'
        elif not zhoumen and yuemen:
            key = '非周门+月门'
        else:
            key = '非周门+非月门'

        agg[key]['n'] += 1
        if next_hr[j] >= 2: agg[key]['n_ge2'] += 1
        if next_hr[j] >= 3: agg[key]['n_ge3'] += 1

        # 单独周门
        if zhoumen:
            agg['仅周门']['n'] += 1
            if next_hr[j] >= 2: agg['仅周门']['n_ge2'] += 1
            if next_hr[j] >= 3: agg['仅周门']['n_ge3'] += 1
        # 单独月门
        if yuemen:
            agg['仅月门']['n'] += 1
            if next_hr[j] >= 2: agg['仅月门']['n_ge2'] += 1
            if next_hr[j] >= 3: agg['仅月门']['n_ge3'] += 1

        # 基准
        agg['基准']['n'] += 1
        if next_hr[j] >= 2: agg['基准']['n_ge2'] += 1
        if next_hr[j] >= 3: agg['基准']['n_ge3'] += 1

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

# 输出
print('\n' + '='*80)
print('§2.1.4 周门 vs 月门：每日筛选对比')
print('='*80)
print(f'{"组合":<16s} {"样本":>12s} {"占比":>8s} {"下日≥2%":>10s} {"下日≥3%":>10s}')
print('-'*60)
total = agg['基准']['n']
for key in ['基准','周门+月门','周门+非月门','非周门+月门','非周门+非月门','仅周门','仅月门']:
    a = agg[key]
    if a['n'] == 0: continue
    print(f'{key:<16s} {a["n"]:>12,d} {a["n"]/total*100:>7.1f}% {a["n_ge2"]/a["n"]*100:>9.1f}% {a["n_ge3"]/a["n"]*100:>9.1f}%')

# 保存
with open('____temp/周门月门_高波池.txt', 'w', encoding='utf-8') as f:
    f.write('组合,样本,占比,下日≥2%,下日≥3%\n')
    for key in ['基准','周门+月门','周门+非月门','非周门+月门','非周门+非月门','仅周门','仅月门']:
        a = agg[key]
        if a['n'] == 0: continue
        f.write(f'{key},{a["n"]},{a["n"]/total*100:.1f}%,{a["n_ge2"]/a["n"]*100:.1f}%,{a["n_ge3"]/a["n"]*100:.1f}%\n')
print('\n结果已保存: ____temp/周门月门_高波池.txt')