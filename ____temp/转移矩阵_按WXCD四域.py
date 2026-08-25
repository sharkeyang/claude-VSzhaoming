# -*- coding: utf-8 -*-
"""
按WXCD四域拆分的护型转移矩阵
金/银/唏嘘/尿/屎 各跑一个转移矩阵
验证：主升时乙(ZA<0)是否更倾向于转乙(ZA>0)，主跌时相反
"""
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
import pandas as pd, numpy as np, glob, json, time, warnings, os
from collections import defaultdict
warnings.simplefilter('ignore')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
高波池 = {'Qic', 'Qim', 'Qit'}
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
files = sorted(glob.glob(DATA_DIR + '/谕组周_*.csv'))

def get_wxab_hu(s):
    if pd.isna(s) or len(str(s)) == 0: return '?'
    m = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
    return m.get(str(s)[0], '?')

def get_wxcd(s):
    """WXCD首字：金/银/唏/嘘/尿/屎"""
    if pd.isna(s) or len(str(s)) == 0: return '?'
    return str(s)[0]

# 按WXCD四域聚合
# 金 / 银 / 唏嘘 / 尿 / 屎
agg = defaultdict(lambda: defaultdict(int))
agg_total = defaultdict(int)

t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}/{len(files)}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 2: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池: continue
    try:
        wxab = df['WXAB'].astype(str).values
        wxcd = df['WXCD'].astype(str).values
        za = df['ZA周'].astype(float).values
    except: continue
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        cd = get_wxcd(wxcd[j])
        if cd == '?': continue
        # 合并唏嘘
        if cd in '唏嘘':
            cd = '唏嘘'
        za_cur = za[j] > 0
        za_nxt = za[j+1] > 0
        # 当前护型按ZA拆分
        if cur == '乙':
            cur_key = '乙(ZA>0)' if za_cur else '乙(ZA≤0)'
        elif cur == '戊':
            cur_key = '戊(ZA>0)' if za_cur else '戊(ZA≤0)'
        else:
            cur_key = cur
        # 转移去向按ZA拆分
        if nxt == '乙':
            nxt_key = '乙(ZA>0)' if za_nxt else '乙(ZA≤0)'
        elif nxt == '戊':
            nxt_key = '戊(ZA>0)' if za_nxt else '戊(ZA≤0)'
        else:
            nxt_key = nxt
        key = (cur_key, cd)
        agg[key][nxt_key] += 1
        agg_total[key] += 1

print(f'耗时: {time.time()-t0:.0f}s', flush=True)

headers = ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']

for cd in ['金','银','唏嘘','尿','屎']:
    print(f'\n{"="*80}')
    print(f'WXCD={cd} 时护型转移矩阵')
    print(f'{"="*80}')
    print(f'{"当前护型":<12s} {"样本":>8s}', end='')
    for h in headers:
        print(f'{h:>12s}', end='')
    print(f'{"维持率":>10s}')
    print('-'*120)
    for cur_key in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        key = (cur_key, cd)
        total = agg_total[key]
        if total < 100: continue
        trans = agg[key]
        # 维持率
        if cur_key.startswith('乙'):
            maintain = trans.get('乙(ZA>0)',0) + trans.get('乙(ZA≤0)',0)
        elif cur_key.startswith('戊'):
            maintain = trans.get('戊(ZA>0)',0) + trans.get('戊(ZA≤0)',0)
        else:
            maintain = trans.get(cur_key, 0)
        print(f'{cur_key:<12s} {total:>8,d}', end='')
        for nxt_key in headers:
            print(f'{trans.get(nxt_key,0)/total*100:>11.1f}%', end='')
        print(f'{maintain/total*100:>9.1f}%')

# 关键对比：乙(ZA≤0)在不同WXCD下的转移去向
print(f'\n{"="*80}')
print('乙(ZA≤0)在不同WXCD下的转移去向对比')
print(f'{"="*80}')
print(f'{"WXCD":<6s} {"样本":>8s} {"→乙(ZA>0)":>12s} {"→乙(ZA≤0)":>12s} {"→丙":>8s} {"→丁":>8s} {"维持率":>10s}')
print('-'*60)
for cd in ['金','银','唏嘘','尿','屎']:
    key = ('乙(ZA≤0)', cd)
    total = agg_total[key]
    if total < 100: continue
    trans = agg[key]
    maintain = trans.get('乙(ZA>0)',0) + trans.get('乙(ZA≤0)',0)
    print(f'{cd:<6s} {total:>8,d} {trans.get("乙(ZA>0)",0)/total*100:>11.1f}% {trans.get("乙(ZA≤0)",0)/total*100:>11.1f}% {trans.get("丙",0)/total*100:>7.1f}% {trans.get("丁",0)/total*100:>7.1f}% {maintain/total*100:>9.1f}%')

# 关键对比：乙(ZA>0)在不同WXCD下的转移去向
print(f'\n{"="*80}')
print('乙(ZA>0)在不同WXCD下的转移去向对比')
print(f'{"="*80}')
print(f'{"WXCD":<6s} {"样本":>8s} {"→乙(ZA>0)":>12s} {"→乙(ZA≤0)":>12s} {"→丙":>8s} {"→丁":>8s} {"维持率":>10s}')
print('-'*60)
for cd in ['金','银','唏嘘','尿','屎']:
    key = ('乙(ZA>0)', cd)
    total = agg_total[key]
    if total < 100: continue
    trans = agg[key]
    maintain = trans.get('乙(ZA>0)',0) + trans.get('乙(ZA≤0)',0)
    print(f'{cd:<6s} {total:>8,d} {trans.get("乙(ZA>0)",0)/total*100:>11.1f}% {trans.get("乙(ZA≤0)",0)/total*100:>11.1f}% {trans.get("丙",0)/total*100:>7.1f}% {trans.get("丁",0)/total*100:>7.1f}% {maintain/total*100:>9.1f}%')