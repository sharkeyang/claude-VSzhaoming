# -*- coding: utf-8 -*-
"""
MC3.3.3 每日筛选流程 高波池全量重跑.py
====================================
重跑 §2.1.5 每日筛选流程数据（含BSHA5+连阳）
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

agg = defaultdict(lambda: {'n':0, 'n_ge2':0})

def add(key, next_hr):
    agg[key]['n'] += 1
    if next_hr >= 2:
        agg[key]['n_ge2'] += 1

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
        bsha = df['BSHA'].astype(float).values
        lianyang = df['BT连阳'].astype(float).values
        next_hr = df['次日高幅'].astype(float).values
    except:
        continue

    for j in range(len(df) - 1):
        if next_hr[j] <= -99:
            continue
        cd = dxcd[j][0] if len(dxcd[j]) > 0 else '?'
        zhoumen = zc[j] > 0 and cd == '上'
        yuemen = ze[j] > 0
        b5 = bsha[j] >= 5
        ly = lianyang[j] > 0

        # 基准
        add('基准', next_hr[j])
        # 仅周门
        if zhoumen: add('仅周门', next_hr[j])
        # 仅月门
        if yuemen: add('仅月门', next_hr[j])
        # 周门+月门
        if zhoumen and yuemen: add('周门+月门', next_hr[j])
        # 周门+BSHA5+连阳
        if zhoumen and b5 and ly: add('周门+BSHA5+连阳', next_hr[j])
        # 月门+BSHA5+连阳
        if yuemen and b5 and ly: add('月门+BSHA5+连阳', next_hr[j])
        # 周门+月门+BSHA5+连阳
        if zhoumen and yuemen and b5 and ly: add('周门+月门+BSHA5+连阳', next_hr[j])
        # BSHA5+连阳(无门)
        if b5 and ly: add('BSHA5+连阳(无门)', next_hr[j])

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

print('\n' + '='*80)
print('§2.1.5 每日筛选流程')
print('='*80)
print(f'{"验证场景":<22s} {"样本":>12s} {"占比":>8s} {"下日≥2%":>10s}')
print('-'*55)
total = agg['基准']['n']
for key in ['基准','仅周门','仅月门','周门+月门','周门+BSHA5+连阳','月门+BSHA5+连阳','周门+月门+BSHA5+连阳','BSHA5+连阳(无门)']:
    a = agg[key]
    if a['n'] == 0: continue
    print(f'{key:<22s} {a["n"]:>12,d} {a["n"]/total*100:>7.1f}% {a["n_ge2"]/a["n"]*100:>9.1f}%')

with open('____temp/每日筛选_高波池.txt', 'w', encoding='utf-8') as f:
    f.write('场景,样本,占比,下日≥2%\n')
    for key in ['基准','仅周门','仅月门','周门+月门','周门+BSHA5+连阳','月门+BSHA5+连阳','周门+月门+BSHA5+连阳','BSHA5+连阳(无门)']:
        a = agg[key]
        if a['n'] == 0: continue
        f.write(f'{key},{a["n"]},{a["n"]/total*100:.1f}%,{a["n_ge2"]/a["n"]*100:.1f}%\n')
print('\n结果已保存: ____temp/每日筛选_高波池.txt')