# -*- coding: utf-8 -*-
"""
戊己簇完整结局分析 — 负交→正交转变过程成功率
============================================
对称于乙簇分析（2.3.4.1），追踪戊/己的完整生命周期。
"""
import numpy as np, pandas as pd, os, glob, json, warnings
from collections import defaultdict
warnings.simplefilter('ignore')

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 200

高波池板块 = {'Qic', 'Qim', 'Qit'}
护型序 = {'甲':0,'乙':1,'丙':2,'丁':3,'戊':4,'己':5}

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    if len(dxab_str) >= 2 and dxab_str[1] in 护型序:
        return dxab_str[1]
    return ''

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

# ── 收集所有股票的护型序列 ──
# 每只股票: [(date, hx, za, zc, pr, hr), ...]
stock_data = defaultdict(list)

for i, f in enumerate(files):
    if i % 500 == 0:
        print(f'  [{i}/{len(files)}]...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5: continue
    except: continue

    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池板块: continue

    dates = df.iloc[:, 0].astype(str).values
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    zas = df['日ZA'].astype(float).values
    zcs = df['日ZC'].astype(float).values
    prs = df['涨幅'].astype(float).values
    hrs = df['次日高幅'].astype(float).values

    for j in range(len(df)):
        if hxs[j]:
            stock_data[cidl].append((dates[j], hxs[j], zas[j], zcs[j], prs[j], hrs[j]))

print(f'股票数: {len(stock_data)}', flush=True)

# ── 提取戊簇和己簇 ──
# 簇定义：连续出现戊（或己）的日子，且起始日DXZA<0（与乙簇对称）
# 结局：退出到哪个护型

def extract_clusters(stock_data, target_hx):
    """提取目标护型的连续簇，起始日ZA<0"""
    clusters = []  # [(start_idx, end_idx, length, [hx_seq], [za_seq], exit_hx)]
    for cidl, rows in stock_data.items():
        i = 0
        while i < len(rows):
            if rows[i][1] == target_hx and rows[i][3] < 0:  # ZA<0
                start = i
                while i < len(rows) and rows[i][1] == target_hx:
                    i += 1
                end = i - 1
                length = end - start + 1
                # 确定退出护型
                exit_hx = ''
                if i < len(rows):
                    exit_hx = rows[i][1]
                clusters.append({
                    'cidl': cidl, 'start': start, 'end': end,
                    'length': length, 'exit_hx': exit_hx,
                    'start_za': rows[start][3],
                    'end_za': rows[end][3],
                    'has_za_pos': any(rows[k][3] > 0 for k in range(start, end+1)),
                    'has_za_neg': any(rows[k][3] < 0 for k in range(start, end+1)),
                })
            else:
                i += 1
    return clusters

print('提取戊簇...', flush=True)
戊簇 = extract_clusters(stock_data, '戊')
print(f'戊簇数: {len(戊簇)}', flush=True)

print('提取己簇...', flush=True)
己簇 = extract_clusters(stock_data, '己')
print(f'己簇数: {len(己簇)}', flush=True)

# ── 分析结局分布 ──
def analyze_outcomes(clusters, name):
    print(f'\n{"="*60}')
    print(f'{name} 结局分析')
    print(f'{"="*60}')

    total = len(clusters)
    if total == 0: return

    # 无条件结局
    outcomes = defaultdict(int)
    for c in clusters:
        outcomes[c['exit_hx']] += 1

    print(f'\n无条件结局（{name}起始ZA<0，共{total}个簇）：')
    print(f'| 结局 | 数量 | 占比 | 含义 |')
    print(f'|:----|:----:|:----:|:-----|')
    正交结局 = {'甲', '乙'}
    负交结局 = {'丙', '丁', '戊', '己'}
    for hx in ['甲','乙','丙','丁','戊','己','']:
        n = outcomes.get(hx, 0)
        if n > 0:
            if hx == '':
                print(f'| 文件末尾未结束 | {n} | {n/total*100:.2f}% | - |')
            elif hx in 正交结局:
                print(f'| ->{hx}(转正交) | {n} | {n/total*100:.2f}% | 成功转正交 |')
            else:
                print(f'| ->{hx}(维持负交) | {n} | {n/total*100:.2f}% | 仍在负交体系 |')

    # 按簇长度分组
    print(f'\n按簇长度分组（{name}）：')
    print(f'| 长度 | 簇数 | 转正交 | 维持负交 | 未结束 |')
    print(f'|:----|:----:|:------:|:--------:|:-----:|')
    for length in [1, 2, 3, 4, 5]:
        subset = [c for c in clusters if c['length'] == length]
        if not subset: continue
        n_ok = sum(1 for c in subset if c['exit_hx'] in 正交结局)
        n_bad = sum(1 for c in subset if c['exit_hx'] in 负交结局)
        n_end = sum(1 for c in subset if c['exit_hx'] == '')
        print(f'| {length}天 | {len(subset)} | {n_ok/len(subset)*100:.1f}% | {n_bad/len(subset)*100:.1f}% | {n_end/len(subset)*100:.1f}% |')

    # 按簇内ZA恢复情况分组
    print(f'\n按簇内ZA恢复情况分组（{name}）：')
    print(f'| 条件 | 簇数 | 转正交 | 维持负交 | 含义 |')
    print(f'|:----|:----:|:------:|:--------:|:-----|')
    for cond, key in [('簇内ZA曾>0', True), ('簇内ZA始终≤0', False)]:
        subset = [c for c in clusters if c['has_za_pos'] == key]
        if not subset: continue
        n_ok = sum(1 for c in subset if c['exit_hx'] in 正交结局)
        n_bad = sum(1 for c in subset if c['exit_hx'] in 负交结局)
        n_end = sum(1 for c in subset if c['exit_hx'] == '')
        print(f'| {cond} | {len(subset)} | {n_ok/len(subset)*100:.1f}% | {n_bad/len(subset)*100:.1f}% | {"ZA恢复后转正交概率高" if n_ok/len(subset) > 0.3 else "ZA恢复后仍难转正交"} |')

analyze_outcomes(戊簇, '戊簇')
analyze_outcomes(己簇, '己簇')

# ── 额外：戊→己→甲 完整路径分析 ──
print(f'\n{"="*60}')
print('戊→己→甲 完整路径分析')
print(f'{"="*60}')

# 统计戊→己的转移概率
戊转己_count = 0
戊转己_成功转甲 = 0
for c in 戊簇:
    if c['exit_hx'] == '己':
        戊转己_count += 1
        # 找到这个己簇
        for c2 in 己簇:
            if c2['cidl'] == c['cidl'] and c2['start'] == c['end'] + 1:
                if c2['exit_hx'] == '甲':
                    戊转己_成功转甲 += 1
                break

if 戊转己_count > 0:
    print(f'戊→己转移数: {戊转己_count}')
    print(f'戊→己→甲成功数: {戊转己_成功转甲}')
    print(f'戊→己→甲成功率: {戊转己_成功转甲/戊转己_count*100:.1f}%')

# ── 输出汇总表 ──
print(f'\n{"="*60}')
print('汇总：负交→正交转变成功率')
print(f'{"="*60}')
print()
print('| 起始护型 | 簇数 | 转正交 | 转甲 | 转乙 | 维持负交 | 未结束 |')
print('|:--------|:----:|:------:|:----:|:----:|:--------:|:-----:|')

for name, clusters in [('戊簇', 戊簇), ('己簇', 己簇)]:
    total = len(clusters)
    if total == 0: continue
    outcomes = defaultdict(int)
    for c in clusters:
        outcomes[c['exit_hx']] += 1
    n_ok = sum(outcomes.get(h, 0) for h in 正交结局)
    n_甲 = outcomes.get('甲', 0)
    n_乙 = outcomes.get('乙', 0)
    n_bad = sum(outcomes.get(h, 0) for h in 负交结局)
    n_end = outcomes.get('', 0)
    print(f'| {name} | {total} | {n_ok/total*100:.1f}% | {n_甲/total*100:.1f}% | {n_乙/total*100:.1f}% | {n_bad/total*100:.1f}% | {n_end/total*100:.1f}% |')

print(f'\n对比：乙簇（正交→负交方向）')
print(f'| 起始护型 | 簇数 | 恢复正交 | 恶化到丙 | 恶化到丁 | 未结束 |')
print(f'|:--------|:----:|:--------:|:--------:|:--------:|:-----:|')
print(f'| 乙簇(ZA<0) | 601,616 | 58.1% | 37.3% | 4.5% | 0.2% |')