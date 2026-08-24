# -*- coding: utf-8 -*-
"""
周级别 WXZC+WXAB 全维度分析 v2.py
==================================
修正WXCD和柱排周的提取逻辑
"""
import pandas as pd, numpy as np, glob, json, time, warnings, os, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

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

def get_zhupai(s):
    """柱排周首字：升/跌/人"""
    if pd.isna(s) or len(str(s)) == 0: return '?'
    s = str(s)
    if s.startswith('(升)') or s.startswith('(人)'):
        return '人'
    return s[0]

t0 = time.time()

# ── 1. 护型排序 ──
print('='*80)
print('1. 护型排序（WXZC>0 和 WXZC≤0）')
print('='*80)

agg_1 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0, 'rets':[]})

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
        zc = df['ZC周'].astype(float).values
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        key = (hu, 'ZC>0' if zc[j] > 0 else 'ZC≤0')
        agg_1[key]['n'] += 1
        agg_1[key]['sum_pr'] += pr[j]
        agg_1[key]['rets'].append(pr[j])
        if pr[j] > 0: agg_1[key]['n_win'] += 1

print(f'{"护型":<6s} {"ZC>0样本":>10s} {"ZC>0均涨幅":>10s} {"ZC>0涨率":>10s} {"ZC≤0样本":>10s} {"ZC≤0均涨幅":>10s} {"ZC≤0涨率":>10s}')
print('-'*75)
for hu in ['甲','乙','丙','丁','戊','己']:
    a1 = agg_1[(hu, 'ZC>0')]
    a2 = agg_1[(hu, 'ZC≤0')]
    if a1['n'] == 0: continue
    print(f'{hu:<6s} {a1["n"]:>10,d} {a1["sum_pr"]/a1["n"]:>9.2f}% {a1["n_win"]/a1["n"]*100:>9.1f}% {a2["n"]:>10,d} {a2["sum_pr"]/a2["n"]:>9.2f}% {a2["n_win"]/a2["n"]*100:>9.1f}%')

# ── 2. 护型转移概率 ──
print('\n' + '='*80)
print('2. 护型转移概率')
print('='*80)

agg_trans = defaultdict(lambda: defaultdict(int))
agg_trans_total = defaultdict(int)

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 2: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池: continue
    try:
        wxab = df['WXAB'].astype(str).values
    except: continue
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        agg_trans[cur][nxt] += 1
        agg_trans_total[cur] += 1

for cur_hu in ['甲','乙','丙','丁','戊','己']:
    total = agg_trans_total[cur_hu]
    if total < 100: continue
    trans = agg_trans[cur_hu]
    maintain = trans.get(cur_hu, 0)
    print(f'\n--- 当前护型: {cur_hu}（样本{total:,}）---')
    print(f'{"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*60)
    for nxt in ['甲','乙','丙','丁','戊','己']:
        print(f'{trans.get(nxt,0)/total*100:>7.1f}%', end=' ')
    print(f'{maintain/total*100:>7.1f}%')

# ── 3. 护型×WXCD协同 ──
print('\n' + '='*80)
print('3. 护型×WXCD协同')
print('='*80)

agg_3 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
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
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        cd = get_wxcd(wxcd[j])
        if hu == '?' or cd == '?': continue
        key = (hu, cd)
        agg_3[key]['n'] += 1
        agg_3[key]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_3[key]['n_win'] += 1

print(f'{"护型":<6s} {"金":>12s} {"银":>12s} {"唏":>12s} {"嘘":>12s} {"尿":>12s} {"屎":>12s}')
print('-'*80)
for hu in ['甲','乙','丙','丁','戊','己']:
    parts = []
    for cd in ['金','银','唏','嘘','尿','屎']:
        a = agg_3[(hu, cd)]
        if a['n'] > 0:
            parts.append(f'{a["sum_pr"]/a["n"]:.2f}%/{a["n_win"]/a["n"]*100:.0f}%')
        else:
            parts.append('—')
    print(f'{hu:<6s} {parts[0]:>12s} {parts[1]:>12s} {parts[2]:>12s} {parts[3]:>12s} {parts[4]:>12s} {parts[5]:>12s}')

# ── 4. 护型持续天数 ──
print('\n' + '='*80)
print('4. 护型持续天数')
print('='*80)

agg_dur = defaultdict(lambda: {'durations':[]})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 2: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池: continue
    try:
        wxab = df['WXAB'].astype(str).values
    except: continue
    cur_hu = None; dur = 0
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        if hu == cur_hu: dur += 1
        else:
            if cur_hu and dur >= 1: agg_dur[cur_hu]['durations'].append(dur)
            cur_hu = hu; dur = 1
    if cur_hu and dur >= 1: agg_dur[cur_hu]['durations'].append(dur)

print(f'{"护型":<6s} {"均值":>8s} {"中位数":>8s} {"最大":>8s} {"样本":>8s}')
print('-'*40)
for hu in ['甲','乙','丙','丁','戊','己']:
    d = agg_dur[hu]['durations']
    if d:
        print(f'{hu:<6s} {np.mean(d):>7.1f}周 {np.median(d):>7.1f}周 {max(d):>7d}周 {len(d):>8,d}')

# ── 5. 护型×柱排 ──
print('\n' + '='*80)
print('5. 护型×柱排')
print('='*80)

agg_5 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  {i}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 2: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池: continue
    try:
        wxab = df['WXAB'].astype(str).values
        zhupai = df['柱排周'].astype(str).values
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        zp = get_zhupai(zhupai[j])
        if hu == '?': continue
        key = (hu, zp)
        agg_5[key]['n'] += 1
        agg_5[key]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_5[key]['n_win'] += 1

for hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {hu} ---')
    print(f'{"柱排":<6s} {"样本":>8s} {"均涨幅":>8s} {"涨率":>8s}')
    print('-'*35)
    for zp in ['升','跌','人']:
        a = agg_5[(hu, zp)]
        if a['n'] > 0:
            print(f'{zp:<6s} {a["n"]:>8,d} {a["sum_pr"]/a["n"]:>7.2f}% {a["n_win"]/a["n"]*100:>7.1f}%')

print(f'\n总耗时: {time.time()-t0:.0f}s')