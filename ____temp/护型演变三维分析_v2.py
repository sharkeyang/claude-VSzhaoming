# -*- coding: utf-8 -*-
"""
护型演变 × 日等型 × 日柱排 三维分析（修复版）
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

def get_dengji(dtza, moshi):
    if dtza == 1: return '等1'
    elif dtza == -1: return '等5'
    elif dtza >= 2:
        if moshi in 'EF': return '等7'
        elif moshi in 'CD': return '等2'
        elif moshi in 'AB': return '等3'
        else: return '等2'
    elif dtza <= -2:
        if moshi in 'ABCD': return '等6'
        elif moshi in 'EF': return '等7'
        else: return '等6'
    return '等0'

def get_huxing(s):
    if pd.isna(s) or len(str(s)) == 0: return '?'
    first = str(s)[0]
    mapping = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
    return mapping.get(first, '?')

def get_zhupai(s):
    """从柱排完整字符串中提取升/人/跌"""
    if pd.isna(s) or len(str(s)) == 0: return '?'
    s = str(s)
    if s.startswith('升'): return '升排'
    elif s.startswith('跌'): return '跌排'
    elif s.startswith('('):
        # (升)人 或 (跌)人 或 (人)人
        if '升' in s[:5]: return '升排'
        elif '跌' in s[:5]: return '跌排'
        else: return '人排'
    else:
        return '?'

agg_trans = defaultdict(lambda: defaultdict(int))
agg_trans_total = defaultdict(int)

t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池板块: continue
    try:
        dxab = df['DXAB'].astype(str).values
        zhupa = df['柱排'].astype(str).values
        dtza = df['日ZA'].astype(int).values
        moshi = df['中符串'].astype(str).values
    except: continue

    for j in range(len(df) - 1):
        cur_hu = get_huxing(dxab[j])
        next_hu = get_huxing(dxab[j+1])
        if cur_hu == '?' or next_hu == '?': continue
        last_char = moshi[j][-1] if len(moshi[j]) > 0 else '?'
        dj = get_dengji(dtza[j], last_char)
        zp = get_zhupai(zhupa[j])
        if zp == '?': continue
        key = (cur_hu, dj, zp)
        agg_trans[key][next_hu] += 1
        agg_trans_total[key] += 1

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

# 输出
# 1. 护型转移 × 日等型
print('\n' + '='*80)
print('一、护型转移 × 日等型（二维）')
print('='*80)
for cur_hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"等型":<6s} {"样本":>8s} {"→甲":>7s} {"→乙":>7s} {"→丙":>7s} {"→丁":>7s} {"→戊":>7s} {"→己":>7s} {"维持":>6s}')
    print('-'*68)
    for dj in ['等1','等2','等3','等5','等6','等7']:
        total = 0; trans = defaultdict(int)
        for k, v in agg_trans.items():
            if k[0] == cur_hu and k[1] == dj:
                total += agg_trans_total[k]
                for nxt, cnt in v.items(): trans[nxt] += cnt
        if total < 100: continue
        mr = trans.get(cur_hu, 0)/total*100
        print(f'{dj:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>6.1f}% {trans.get("乙",0)/total*100:>6.1f}% {trans.get("丙",0)/total*100:>6.1f}% {trans.get("丁",0)/total*100:>6.1f}% {trans.get("戊",0)/total*100:>6.1f}% {trans.get("己",0)/total*100:>6.1f}% {mr:>5.1f}%')

# 2. 护型转移 × 柱排
print('\n' + '='*80)
print('二、护型转移 × 柱排（二维）')
print('='*80)
for cur_hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"柱排":<6s} {"样本":>8s} {"→甲":>7s} {"→乙":>7s} {"→丙":>7s} {"→丁":>7s} {"→戊":>7s} {"→己":>7s} {"维持":>6s}')
    print('-'*68)
    for zp in ['升排','人排','跌排']:
        total = 0; trans = defaultdict(int)
        for k, v in agg_trans.items():
            if k[0] == cur_hu and k[2] == zp:
                total += agg_trans_total[k]
                for nxt, cnt in v.items(): trans[nxt] += cnt
        if total < 100: continue
        mr = trans.get(cur_hu, 0)/total*100
        print(f'{zp:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>6.1f}% {trans.get("乙",0)/total*100:>6.1f}% {trans.get("丙",0)/total*100:>6.1f}% {trans.get("丁",0)/total*100:>6.1f}% {trans.get("戊",0)/total*100:>6.1f}% {trans.get("己",0)/total*100:>6.1f}% {mr:>5.1f}%')

# 3. 三维交叉：己和乙
print('\n' + '='*80)
print('三、三维交叉：护型 × 等型 × 柱排')
print('='*80)
for cur_hu in ['己','乙']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"等型":<6s} {"柱排":<6s} {"样本":>8s} {"→甲":>7s} {"→乙":>7s} {"→丙":>7s} {"→丁":>7s} {"→戊":>7s} {"→己":>7s} {"维持":>6s}')
    print('-'*75)
    for dj in ['等1','等2','等3','等5','等6','等7']:
        for zp in ['升排','人排','跌排']:
            key = (cur_hu, dj, zp)
            total = agg_trans_total.get(key, 0)
            if total < 100: continue
            trans = agg_trans[key]
            mr = trans.get(cur_hu, 0)/total*100
            print(f'{dj:<6s} {zp:<6s} {total:>8,d} {trans.get("甲",0)/total*100:>6.1f}% {trans.get("乙",0)/total*100:>6.1f}% {trans.get("丙",0)/total*100:>6.1f}% {trans.get("丁",0)/total*100:>6.1f}% {trans.get("戊",0)/total*100:>6.1f}% {trans.get("己",0)/total*100:>6.1f}% {mr:>5.1f}%')

print('\n完成！')