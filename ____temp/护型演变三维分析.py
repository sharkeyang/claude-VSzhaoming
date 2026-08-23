# -*- coding: utf-8 -*-
"""
护型演变 × 日等型 × 日柱排 三维分析
=====================================
研究目标：
1. 护型转移概率 × 日等型（当前位置）
2. 护型转移概率 × 日柱排（当前动能）
3. 三维交叉：护型 × 等型 × 柱排 → 下一个护型预测
"""
import pandas as pd, numpy as np, glob, json, time, warnings, os, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}

with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(glob.glob(DATA_DIR + '/谕组日_*.csv'))

# 日等型映射
def get_dengji(dtza, moshi):
    """根据DTZA和末符计算日等型"""
    if dtza == 1:
        return '等1'
    elif dtza == -1:
        return '等5'
    elif dtza >= 2:
        if moshi in 'EF':
            return '等7'
        elif moshi in 'CD':
            return '等2'
        elif moshi in 'AB':
            return '等3'
        else:
            return '等2'
    elif dtza <= -2:
        if moshi in 'AB':
            return '等6'
        elif moshi in 'CD':
            return '等6'
        elif moshi in 'EF':
            return '等7'
        else:
            return '等6'
    else:
        return '等0'

# 聚合器
# agg_trans[('当前护型','日等型','柱排')] = {'->甲':n, '->乙':n, ...}
agg_trans = defaultdict(lambda: defaultdict(int))
agg_trans_total = defaultdict(int)  # 总样本数

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
    if board not in 高波池板块:
        continue

    try:
        dxab = df['DXAB'].astype(str).values
        zhupa = df['柱排'].astype(str).values
        dtza = df['日ZA'].astype(int).values
        moshi = df['中符串'].astype(str).values
    except:
        continue

    # 提取DXAB首字（护型）
    def get_huxing(s):
        if pd.isna(s) or len(s) == 0:
            return '?'
        first = s[0]
        mapping = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
        return mapping.get(first, '?')

    for j in range(len(df) - 1):
        cur_hu = get_huxing(dxab[j])
        next_hu = get_huxing(dxab[j+1])
        if cur_hu == '?' or next_hu == '?':
            continue

        # 日等型
        last_char = moshi[j][-1] if len(moshi[j]) > 0 else '?'
        dj = get_dengji(dtza[j], last_char)

        # 柱排
        zp = zhupa[j] if not pd.isna(zhupa[j]) else '?'

        key = (cur_hu, dj, zp)
        agg_trans[key][next_hu] += 1
        agg_trans_total[key] += 1

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

# ── 输出结果 ──
# 1. 护型转移 × 日等型（二维）
print('\n' + '='*80)
print('一、护型转移 × 日等型（二维）')
print('='*80)

for cur_hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"日等型":<6s} {"样本":>8s} {"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*70)
    for dj in ['等1','等2','等3','等5','等6','等7']:
        key = (cur_hu, dj, '?')
        # 汇总所有柱排
        total = 0
        trans = defaultdict(int)
        for k, v in agg_trans.items():
            if k[0] == cur_hu and k[1] == dj:
                total += agg_trans_total[k]
                for nxt, cnt in v.items():
                    trans[nxt] += cnt
        if total < 100:
            continue
        maintain = trans.get(cur_hu, 0)
        maintain_rate = maintain/total*100
        print(f'{dj:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>7.1f}% {trans.get("乙",0)/total*100:>7.1f}% {trans.get("丙",0)/total*100:>7.1f}% {trans.get("丁",0)/total*100:>7.1f}% {trans.get("戊",0)/total*100:>7.1f}% {trans.get("己",0)/total*100:>7.1f}% {maintain_rate:>7.1f}%')

# 2. 护型转移 × 日柱排（二维）
print('\n' + '='*80)
print('二、护型转移 × 日柱排（二维）')
print('='*80)

for cur_hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"柱排":<6s} {"样本":>8s} {"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*70)
    for zp in ['升排','人排','跌排']:
        total = 0
        trans = defaultdict(int)
        for k, v in agg_trans.items():
            if k[0] == cur_hu and k[2] == zp:
                total += agg_trans_total[k]
                for nxt, cnt in v.items():
                    trans[nxt] += cnt
        if total < 100:
            continue
        maintain = trans.get(cur_hu, 0)
        maintain_rate = maintain/total*100
        print(f'{zp:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>7.1f}% {trans.get("乙",0)/total*100:>7.1f}% {trans.get("丙",0)/total*100:>7.1f}% {trans.get("丁",0)/total*100:>7.1f}% {trans.get("戊",0)/total*100:>7.1f}% {trans.get("己",0)/total*100:>7.1f}% {maintain_rate:>7.1f}%')

# 3. 三维交叉：护型 × 等型 × 柱排 → 关键护型的演变
print('\n' + '='*80)
print('三、三维交叉：护型 × 等型 × 柱排（关键护型）')
print('='*80)

for cur_hu in ['己','乙']:  # 关键护型
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"等型":<6s} {"柱排":<6s} {"样本":>8s} {"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*75)
    for dj in ['等1','等2','等3','等5','等6','等7']:
        for zp in ['升排','人排','跌排']:
            key = (cur_hu, dj, zp)
            total = agg_trans_total.get(key, 0)
            if total < 100:
                continue
            trans = agg_trans[key]
            maintain = trans.get(cur_hu, 0)
            maintain_rate = maintain/total*100
            print(f'{dj:<6s} {zp:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>7.1f}% {trans.get("乙",0)/total*100:>7.1f}% {trans.get("丙",0)/total*100:>7.1f}% {trans.get("丁",0)/total*100:>7.1f}% {trans.get("戊",0)/total*100:>7.1f}% {trans.get("己",0)/total*100:>7.1f}% {maintain_rate:>7.1f}%')

print('\n完成！')