# -*- coding: utf-8 -*-
"""
周级别 2.3 护型转移研究 补全.py
================================
补做日类2.3中未完成的子专题
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

t0 = time.time()

# ── 2.3.1.1 WXZC>0时护型转移矩阵 ──
print('='*80)
print('2.3.1.1 WXZC>0时护型转移矩阵')
print('='*80)

agg_trans_zc = defaultdict(lambda: defaultdict(int))
agg_trans_zc_total = defaultdict(int)

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
    except: continue
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        zc_gt0 = zc[j] > 0
        key = (cur, 'ZC>0' if zc_gt0 else 'ZC≤0')
        agg_trans_zc[key][nxt] += 1
        agg_trans_zc_total[key] += 1

for zc_label in ['ZC>0', 'ZC≤0']:
    print(f'\n--- {zc_label} ---')
    print(f'{"当前护型":<8s} {"样本":>10s} {"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*75)
    for cur_hu in ['甲','乙','丙','丁','戊','己']:
        key = (cur_hu, zc_label)
        total = agg_trans_zc_total[key]
        if total < 100: continue
        trans = agg_trans_zc[key]
        maintain = trans.get(cur_hu, 0)
        print(f'{cur_hu:<8s} {total:>10,d}', end='')
        for nxt in ['甲','乙','丙','丁','戊','己']:
            print(f'{trans.get(nxt,0)/total*100:>7.1f}%', end='')
        print(f'{maintain/total*100:>7.1f}%')

# ── 2.3.1.2 转移后的下周涨幅 ──
print('\n' + '='*80)
print('2.3.1.2 转移后的下周涨幅')
print('='*80)

agg_trans_pr = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

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
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        key = (cur, nxt)
        agg_trans_pr[key]['n'] += 1
        agg_trans_pr[key]['sum_pr'] += pr[j+1]
        if pr[j+1] > 0: agg_trans_pr[key]['n_win'] += 1

for cur_hu in ['甲','乙','丙','丁','戊','己']:
    print(f'\n--- 当前护型: {cur_hu} ---')
    print(f'{"→护型":<8s} {"样本":>8s} {"下周均涨幅":>10s} {"下周涨率":>10s}')
    print('-'*40)
    for nxt in ['甲','乙','丙','丁','戊','己']:
        a = agg_trans_pr[(cur_hu, nxt)]
        if a['n'] > 0:
            print(f'→{nxt:<6s} {a["n"]:>8,d} {a["sum_pr"]/a["n"]:>9.2f}% {a["n_win"]/a["n"]*100:>9.1f}%')

# ── 2.3.2 WXAB与WXZA的持有状态与依赖关系 ──
print('\n' + '='*80)
print('2.3.2 WXAB与WXZA的持有状态与依赖关系')
print('='*80)

agg_za = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0, 'za_vals':[]})

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
        za = df['ZA周'].astype(float).values
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        za_gt0 = za[j] > 0
        key = (hu, 'ZA>0' if za_gt0 else 'ZA≤0')
        agg_za[key]['n'] += 1
        agg_za[key]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_za[key]['n_win'] += 1
        agg_za[key]['za_vals'].append(za[j])

print(f'{"护型":<8s} {"ZA>0样本":>10s} {"ZA>0均涨幅":>10s} {"ZA>0涨率":>10s} {"ZA≤0样本":>10s} {"ZA≤0均涨幅":>10s} {"ZA≤0涨率":>10s}')
print('-'*75)
for hu in ['甲','乙','丙','丁','戊','己']:
    a1 = agg_za[(hu, 'ZA>0')]
    a2 = agg_za[(hu, 'ZA≤0')]
    if a1['n'] == 0: continue
    print(f'{hu:<8s} {a1["n"]:>10,d} {a1["sum_pr"]/a1["n"]:>9.2f}% {a1["n_win"]/a1["n"]*100:>9.1f}% {a2["n"]:>10,d} {a2["sum_pr"]/a2["n"]:>9.2f}% {a2["n_win"]/a2["n"]*100:>9.1f}%')

# ── 各护型专题 ──
print('\n' + '='*80)
print('2.3.3~2.3.8 各护型专题')
print('='*80)

# 收集各护型的转移去向和涨幅
agg_hu = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0, 'za_vals':[], 'durations':[], 'trans_to':defaultdict(int), 'trans_from':defaultdict(int)})

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
        za = df['ZA周'].astype(float).values
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        agg_hu[hu]['n'] += 1
        agg_hu[hu]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_hu[hu]['n_win'] += 1
        agg_hu[hu]['za_vals'].append(za[j])
    # 持续天数
    cur_hu = None; dur = 0
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        if hu == cur_hu: dur += 1
        else:
            if cur_hu: agg_hu[cur_hu]['durations'].append(dur)
            cur_hu = hu; dur = 1
    if cur_hu: agg_hu[cur_hu]['durations'].append(dur)
    # 转移
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        agg_hu[cur]['trans_to'][nxt] += 1
        agg_hu[nxt]['trans_from'][cur] += 1

# 甲护型专题
print('\n--- 甲护型专题：诱多信号修正 ---')
a = agg_hu['甲']
za_vals = a['za_vals']
za_gt0 = sum(1 for v in za_vals if v > 0)
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'ZA>0占比: {za_gt0/len(za_vals)*100:.1f}%, ZA中位数: {np.median(za_vals):.1f}')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周')
print(f'转移去向: →甲{a["trans_to"]["甲"]/a["n"]*100:.1f}%, →乙{a["trans_to"]["乙"]/a["n"]*100:.1f}%, →丙{a["trans_to"]["丙"]/a["n"]*100:.1f}%, →丁{a["trans_to"]["丁"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自己{a["trans_from"]["己"]/a["n"]*100:.1f}%')

# 乙护型专题
print('\n--- 乙护型专题 ---')
a = agg_hu['乙']
za_vals = a['za_vals']
za_gt0 = sum(1 for v in za_vals if v > 0)
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'ZA>0占比: {za_gt0/len(za_vals)*100:.1f}%, ZA中位数: {np.median(za_vals):.1f}')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周')
print(f'转移去向: →甲{a["trans_to"]["甲"]/a["n"]*100:.1f}%, →乙{a["trans_to"]["乙"]/a["n"]*100:.1f}%, →丙{a["trans_to"]["丙"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自甲{a["trans_from"]["甲"]/a["n"]*100:.1f}%')

# 丙护型专题
print('\n--- 丙护型专题：死亡螺旋预警 ---')
a = agg_hu['丙']
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周, 最大{max(a["durations"]):d}周')
print(f'转移去向: →乙{a["trans_to"]["乙"]/a["n"]*100:.1f}%, →丙{a["trans_to"]["丙"]/a["n"]*100:.1f}%, →丁{a["trans_to"]["丁"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自乙{a["trans_from"]["乙"]/a["n"]*100:.1f}%')

# 丁护型专题
print('\n--- 丁护型专题：筑底完成信号 ---')
a = agg_hu['丁']
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周')
print(f'转移去向: →丁{a["trans_to"]["丁"]/a["n"]*100:.1f}%, →戊{a["trans_to"]["戊"]/a["n"]*100:.1f}%, →己{a["trans_to"]["己"]/a["n"]*100:.1f}%, →甲{a["trans_to"]["甲"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自丙{a["trans_from"]["丙"]/a["n"]*100:.1f}%')

# 戊护型专题
print('\n--- 戊护型专题 ---')
a = agg_hu['戊']
za_vals = a['za_vals']
za_gt0 = sum(1 for v in za_vals if v > 0)
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'ZA>0占比: {za_gt0/len(za_vals)*100:.1f}%, ZA中位数: {np.median(za_vals):.1f}')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周')
print(f'转移去向: →戊{a["trans_to"]["戊"]/a["n"]*100:.1f}%, →己{a["trans_to"]["己"]/a["n"]*100:.1f}%, →甲{a["trans_to"]["甲"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自丁{a["trans_from"]["丁"]/a["n"]*100:.1f}%')

# 己护型专题
print('\n--- 己护型专题：持续天数与趋势确认 ---')
a = agg_hu['己']
za_vals = a['za_vals']
za_gt0 = sum(1 for v in za_vals if v > 0)
print(f'样本: {a["n"]:,}, 均涨幅: {a["sum_pr"]/a["n"]:.2f}%, 涨率: {a["n_win"]/a["n"]*100:.1f}%')
print(f'ZA>0占比: {za_gt0/len(za_vals)*100:.1f}%, ZA中位数: {np.median(za_vals):.1f}')
print(f'持续天数: 均值{np.mean(a["durations"]):.1f}周, 中位数{np.median(a["durations"]):.1f}周, 最大{max(a["durations"]):d}周')
print(f'转移去向: →甲{a["trans_to"]["甲"]/a["n"]*100:.1f}%, →己{a["trans_to"]["己"]/a["n"]*100:.1f}%, →戊{a["trans_to"]["戊"]/a["n"]*100:.1f}%')
print(f'转移来源: 来自戊{a["trans_from"]["戊"]/a["n"]*100:.1f}%')

print(f'\n总耗时: {time.time()-t0:.0f}s')