# -*- coding: utf-8 -*-
"""
周级别 WXZC+WXAB 全维度分析 v3.py
==================================
在周级别上重跑日类第二章的所有分析：
2.0 核心准则
2.1 核心验证结果（护型排序、假设验证、按市板、个体差异、低波池、跨周期）
2.2 特征统计数据（护型×等型、次日冲高、柱排、持续天数、ZA时长）
2.3 护型转移研究（转移矩阵、ZA依赖、各护型专题）
2.4 ZC分段（ZC数值分级、拐点分析）
2.5 WXCD协同效应
"""
import pandas as pd, numpy as np, glob, json, time, warnings, os, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
高波池 = {'Qic', 'Qim', 'Qit'}
低波池 = {'Qd', 'Qe', 'Qif', 'Qin', 'Qst', 'Qbj'}

with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(glob.glob(DATA_DIR + '/谕组周_*.csv'))

def get_wxab_hu(s):
    if pd.isna(s) or len(str(s)) == 0: return '?'
    m = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
    return m.get(str(s)[0], '?')

def get_wxcd(s):
    if pd.isna(s) or len(str(s)) == 0: return '?'
    return str(s)[0]

def get_zhupai(s):
    if pd.isna(s) or len(str(s)) == 0: return '?'
    s = str(s)
    if s.startswith('(升)') or s.startswith('(人)'): return '人'
    return s[0]

t0 = time.time()

# ── 2.1 核心验证结果 ──
print('='*80)
print('2.1 核心验证结果')
print('='*80)

# 2.1.1 护型排序（按WXZC符号）
agg_211 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0, 'rets':[]})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.1.1 {i}/{len(files)}...', flush=True)
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
        agg_211[key]['n'] += 1
        agg_211[key]['sum_pr'] += pr[j]
        agg_211[key]['rets'].append(pr[j])
        if pr[j] > 0: agg_211[key]['n_win'] += 1

print('\nWXZC>0 排序：')
print(f'{"护型":<6s} {"样本":>10s} {"均涨幅":>8s} {"标准差":>8s} {"涨率":>8s} {"夏普":>8s}')
print('-'*55)
for hu in ['己','甲','戊','乙','丁','丙']:
    a = agg_211[(hu, 'ZC>0')]
    if a['n'] == 0: continue
    std = np.std(a['rets']) if len(a['rets']) > 1 else 0
    sharpe = (a['sum_pr']/a['n'])/std*100 if std > 0 else 0
    print(f'{hu:<6s} {a["n"]:>10,d} {a["sum_pr"]/a["n"]:>7.2f}% {std:>7.2f} {a["n_win"]/a["n"]*100:>7.1f}% {sharpe:>7.2f}')

print('\nWXZC≤0 排序：')
print(f'{"护型":<6s} {"样本":>10s} {"均涨幅":>8s} {"标准差":>8s} {"涨率":>8s} {"夏普":>8s}')
print('-'*55)
for hu in ['己','甲','戊','乙','丁','丙']:
    a = agg_211[(hu, 'ZC≤0')]
    if a['n'] == 0: continue
    std = np.std(a['rets']) if len(a['rets']) > 1 else 0
    sharpe = (a['sum_pr']/a['n'])/std*100 if std > 0 else 0
    print(f'{hu:<6s} {a["n"]:>10,d} {a["sum_pr"]/a["n"]:>7.2f}% {std:>7.2f} {a["n_win"]/a["n"]*100:>7.1f}% {sharpe:>7.2f}')

# 2.1.3 按市板验证
print('\n' + '='*80)
print('2.1.3 按市板验证')
print('='*80)

agg_213 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.1.3 {i}/{len(files)}...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 2: continue
    except: continue
    cidl = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if not board: continue
    try:
        wxab = df['WXAB'].astype(str).values
        zc = df['ZC周'].astype(float).values
        pr = df['PR'].astype(float).values
    except: continue
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        key = (board, hu, 'ZC>0' if zc[j] > 0 else 'ZC≤0')
        agg_213[key]['n'] += 1
        agg_213[key]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_213[key]['n_win'] += 1

for board in ['Qic','Qim','Qit','Qif','Qd','Qe']:
    print(f'\n--- {board} ---')
    print(f'{"护型":<6s} {"ZC>0均涨幅":>10s} {"ZC>0涨率":>10s} {"ZC≤0均涨幅":>10s} {"ZC≤0涨率":>10s}')
    for hu in ['甲','乙','丙','丁','戊','己']:
        a1 = agg_213[(board, hu, 'ZC>0')]
        a2 = agg_213[(board, hu, 'ZC≤0')]
        if a1['n'] == 0: continue
        print(f'{hu:<6s} {a1["sum_pr"]/a1["n"]:>9.2f}% {a1["n_win"]/a1["n"]*100:>9.1f}% {a2["sum_pr"]/a2["n"]:>9.2f}% {a2["n_win"]/a2["n"]*100:>9.1f}%')

# ── 2.2 特征统计数据 ──
print('\n' + '='*80)
print('2.2 特征统计数据')
print('='*80)

# 2.2.1 护型×WXCD协同
print('\n2.2.1 护型×WXCD协同')
print(f'{"护型":<6s} {"金":>12s} {"银":>12s} {"唏":>12s} {"嘘":>12s} {"尿":>12s} {"屎":>12s}')
print('-'*80)

agg_221 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.2.1 {i}/{len(files)}...', flush=True)
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
        agg_221[(hu, cd)]['n'] += 1
        agg_221[(hu, cd)]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_221[(hu, cd)]['n_win'] += 1

for hu in ['甲','乙','丙','丁','戊','己']:
    parts = []
    for cd in ['金','银','唏','嘘','尿','屎']:
        a = agg_221[(hu, cd)]
        if a['n'] > 0:
            parts.append(f'{a["sum_pr"]/a["n"]:.2f}%/{a["n_win"]/a["n"]*100:.0f}%')
        else:
            parts.append('—')
    print(f'{hu:<6s} {parts[0]:>12s} {parts[1]:>12s} {parts[2]:>12s} {parts[3]:>12s} {parts[4]:>12s} {parts[5]:>12s}')

# 2.2.2 护型×柱排
print('\n2.2.2 护型×柱排')
agg_222 = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.2.2 {i}/{len(files)}...', flush=True)
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
        agg_222[(hu, zp)]['n'] += 1
        agg_222[(hu, zp)]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_222[(hu, zp)]['n_win'] += 1

print(f'{"护型":<6s} {"升排均涨幅":>10s} {"升排涨率":>10s} {"跌排均涨幅":>10s} {"跌排涨率":>10s} {"人排均涨幅":>10s} {"人排涨率":>10s}')
print('-'*75)
for hu in ['甲','乙','丙','丁','戊','己']:
    parts = []
    for zp in ['升','跌','人']:
        a = agg_222[(hu, zp)]
        if a['n'] > 0:
            parts.append(f'{a["sum_pr"]/a["n"]:.2f}%')
            parts.append(f'{a["n_win"]/a["n"]*100:.1f}%')
        else:
            parts.append('—')
            parts.append('—')
    print(f'{hu:<6s} {parts[0]:>10s} {parts[1]:>10s} {parts[2]:>10s} {parts[3]:>10s} {parts[4]:>10s} {parts[5]:>10s}')

# 2.2.3 护型持续天数
print('\n2.2.3 护型持续天数')
agg_dur = defaultdict(lambda: {'durations':[], 'durations_zc0':[], 'durations_zc1':[]})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.2.3 {i}/{len(files)}...', flush=True)
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
    cur_hu = None; dur = 0; dur_zc = None
    for j in range(len(df)):
        hu = get_wxab_hu(wxab[j])
        if hu == '?': continue
        if hu == cur_hu:
            dur += 1
        else:
            if cur_hu and dur >= 1:
                agg_dur[cur_hu]['durations'].append(dur)
                if dur_zc is not None:
                    if dur_zc > 0: agg_dur[cur_hu]['durations_zc1'].append(dur)
                    else: agg_dur[cur_hu]['durations_zc0'].append(dur)
            cur_hu = hu; dur = 1; dur_zc = zc[j]
    if cur_hu and dur >= 1:
        agg_dur[cur_hu]['durations'].append(dur)
        if dur_zc is not None:
            if dur_zc > 0: agg_dur[cur_hu]['durations_zc1'].append(dur)
            else: agg_dur[cur_hu]['durations_zc0'].append(dur)

print(f'{"护型":<6s} {"均值":>8s} {"中位数":>8s} {"最大":>8s} {"ZC>0均值":>10s} {"ZC≤0均值":>10s}')
print('-'*55)
for hu in ['甲','乙','丙','丁','戊','己']:
    d = agg_dur[hu]['durations']
    d1 = agg_dur[hu]['durations_zc1']
    d0 = agg_dur[hu]['durations_zc0']
    if d:
        print(f'{hu:<6s} {np.mean(d):>7.1f}周 {np.median(d):>7.1f}周 {max(d):>7d}周 {np.mean(d1):>9.1f}周 {np.mean(d0):>9.1f}周')

# ── 2.3 护型转移研究 ──
print('\n' + '='*80)
print('2.3 护型转移研究')
print('='*80)

# 2.3.1 整体转移矩阵
print('\n2.3.1 护型转移概率（整体）')
agg_trans = defaultdict(lambda: defaultdict(int))
agg_trans_total = defaultdict(int)

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.3.1 {i}/{len(files)}...', flush=True)
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

print(f'{"当前护型":<8s} {"样本":>10s} {"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
print('-'*75)
for cur_hu in ['甲','乙','丙','丁','戊','己']:
    total = agg_trans_total[cur_hu]
    if total < 100: continue
    trans = agg_trans[cur_hu]
    maintain = trans.get(cur_hu, 0)
    print(f'{cur_hu:<8s} {total:>10,d}', end='')
    for nxt in ['甲','乙','丙','丁','戊','己']:
        print(f'{trans.get(nxt,0)/total*100:>7.1f}%', end='')
    print(f'{maintain/total*100:>7.1f}%')

# 2.3.2 乙/戊按ZA拆分
print('\n2.3.2 乙/戊按WXZA拆分')
agg_trans_za = defaultdict(lambda: defaultdict(int))
agg_trans_za_total = defaultdict(int)

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.3.2 {i}/{len(files)}...', flush=True)
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
    except: continue
    for j in range(len(df) - 1):
        cur = get_wxab_hu(wxab[j])
        nxt = get_wxab_hu(wxab[j+1])
        if cur == '?' or nxt == '?': continue
        za_gt0 = za[j] > 0
        if cur == '乙':
            key = '乙(ZA>0)' if za_gt0 else '乙(ZA≤0)'
        elif cur == '戊':
            key = '戊(ZA>0)' if za_gt0 else '戊(ZA≤0)'
        else:
            key = cur
        agg_trans_za[key][nxt] += 1
        agg_trans_za_total[key] += 1

for cur_key in ['乙(ZA>0)','乙(ZA≤0)','戊(ZA>0)','戊(ZA≤0)']:
    total = agg_trans_za_total[cur_key]
    if total < 100: continue
    trans = agg_trans_za[cur_key]
    maintain = trans.get(cur_key[0], 0)
    print(f'\n--- {cur_key}（样本{total:,}）---')
    print(f'{"→甲":>8s} {"→乙":>8s} {"→丙":>8s} {"→丁":>8s} {"→戊":>8s} {"→己":>8s} {"维持率":>8s}')
    print('-'*60)
    for nxt in ['甲','乙','丙','丁','戊','己']:
        print(f'{trans.get(nxt,0)/total*100:>7.1f}%', end='')
    print(f'{maintain/total*100:>7.1f}%')

# ── 2.4 ZC分段 ──
print('\n' + '='*80)
print('2.4 ZC分段')
print('='*80)

print('\n2.4.1 ZC数值分级')
agg_zc = defaultdict(lambda: {'n':0, 'sum_pr':0.0, 'n_win':0})

for i, f in enumerate(files):
    if i % 1000 == 0: print(f'  2.4.1 {i}/{len(files)}...', flush=True)
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
        zc_val = zc[j]
        if zc_val <= -10: seg = 'ZC≤-10'
        elif zc_val <= -5: seg = '-10<ZC≤-5'
        elif zc_val <= -2: seg = '-5<ZC≤-2'
        elif zc_val < 0: seg = '-2<ZC<0'
        elif zc_val < 1: seg = '0≤ZC<1'
        elif zc_val < 2: seg = '1≤ZC<2'
        elif zc_val < 5: seg = '2≤ZC<5'
        elif zc_val < 10: seg = '5≤ZC<10'
        else: seg = 'ZC≥10'
        agg_zc[(hu, seg)]['n'] += 1
        agg_zc[(hu, seg)]['sum_pr'] += pr[j]
        if pr[j] > 0: agg_zc[(hu, seg)]['n_win'] += 1

for seg in ['ZC≤-10','-10<ZC≤-5','-5<ZC≤-2','-2<ZC<0','0≤ZC<1','1≤ZC<2','2≤ZC<5','5≤ZC<10','ZC≥10']:
    print(f'\n{seg}：')
    print(f'{"护型":<6s} {"样本":>8s} {"均涨幅":>8s} {"涨率":>8s}')
    for hu in ['己','甲','戊','乙','丁','丙']:
        a = agg_zc[(hu, seg)]
        if a['n'] > 0:
            print(f'{hu:<6s} {a["n"]:>8,d} {a["sum_pr"]/a["n"]:>7.2f}% {a["n_win"]/a["n"]*100:>7.1f}%')

print(f'\n总耗时: {time.time()-t0:.0f}s')