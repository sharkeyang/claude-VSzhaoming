# -*- coding: utf-8 -*-
"""
戊己簇完整结局分析 v2 — 负交->正交转变过程成功率
=============================================
对称于乙簇分析（2.3.4.1），追踪戊/己的完整生命周期。
在数据加载阶段直接聚合，避免事后遍历。
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

# 直接聚合簇结局
# 对每只股票，扫描护型序列，记录簇的起始和退出
戊簇_结局 = defaultdict(int)  # exit_hx -> count
己簇_结局 = defaultdict(int)
戊簇_长度分组 = defaultdict(lambda: defaultdict(int))  # length -> exit_hx -> count
己簇_长度分组 = defaultdict(lambda: defaultdict(int))
戊簇_ZA恢复 = defaultdict(lambda: defaultdict(int))  # has_za_pos -> exit_hx -> count
己簇_ZA恢复 = defaultdict(lambda: defaultdict(int))

戊簇_总 = 0
己簇_总 = 0

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

    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    zas = df['日ZA'].astype(float).values
    n = len(df)

    # 扫描戊簇
    j = 0
    while j < n:
        if hxs[j] == '戊' and zas[j] < 0:
            start = j
            while j < n and hxs[j] == '戊':
                j += 1
            end = j - 1
            length = end - start + 1
            exit_hx = hxs[j] if j < n else ''
            has_za_pos = any(zas[k] > 0 for k in range(start, end+1))

            戊簇_结局[exit_hx] += 1
            戊簇_长度分组[length][exit_hx] += 1
            戊簇_ZA恢复[has_za_pos][exit_hx] += 1
            戊簇_总 += 1
        else:
            j += 1

    # 扫描己簇
    j = 0
    while j < n:
        if hxs[j] == '己':
            start = j
            while j < n and hxs[j] == '己':
                j += 1
            end = j - 1
            length = end - start + 1
            exit_hx = hxs[j] if j < n else ''
            has_za_pos = any(zas[k] > 0 for k in range(start, end+1))

            己簇_结局[exit_hx] += 1
            己簇_长度分组[length][exit_hx] += 1
            己簇_ZA恢复[has_za_pos][exit_hx] += 1
            己簇_总 += 1
        else:
            j += 1

print(f'戊簇总数: {戊簇_总}', flush=True)
print(f'己簇总数: {己簇_总}', flush=True)

# ── 输出结果 ──
def print_outcomes(name, total, outcomes, length_groups, za_groups):
    print(f'\n{"="*60}')
    print(f'{name} 结局分析（起始ZA<0，共{total}个簇）')
    print(f'{"="*60}')
    if total == 0: return

    print(f'\n无条件结局：')
    print(f'| 结局 | 数量 | 占比 | 含义 |')
    print(f'|:----|:----:|:----:|:-----|')
    正交 = {'甲','乙'}
    负交 = {'丙','丁','戊','己'}
    for hx in ['甲','乙','丙','丁','戊','己','']:
        n = outcomes.get(hx, 0)
        if n > 0:
            if hx == '':
                print(f'| 文件末尾未结束 | {n} | {n/total*100:.2f}% | - |')
            elif hx in 正交:
                print(f'| ->{hx}(转正交) | {n} | {n/total*100:.2f}% | 成功转正交 |')
            else:
                print(f'| ->{hx}(维持负交) | {n} | {n/total*100:.2f}% | 仍在负交体系 |')

    print(f'\n按簇长度分组：')
    print(f'| 长度 | 簇数 | 转正交 | 维持负交 | 未结束 |')
    print(f'|:----|:----:|:------:|:--------:|:-----:|')
    for length in [1, 2, 3, 4, 5]:
        grp = length_groups.get(length, {})
        if not grp: continue
        n_total = sum(grp.values())
        n_ok = sum(grp.get(h, 0) for h in 正交)
        n_bad = sum(grp.get(h, 0) for h in 负交)
        n_end = grp.get('', 0)
        print(f'| {length}天 | {n_total} | {n_ok/n_total*100:.1f}% | {n_bad/n_total*100:.1f}% | {n_end/n_total*100:.1f}% |')

    print(f'\n按簇内ZA恢复情况分组：')
    print(f'| 条件 | 簇数 | 转正交 | 维持负交 | 含义 |')
    print(f'|:----|:----:|:------:|:--------:|:-----|')
    for cond, key in [('簇内ZA曾>0', True), ('簇内ZA始终<=0', False)]:
        grp = za_groups.get(key, {})
        if not grp: continue
        n_total = sum(grp.values())
        n_ok = sum(grp.get(h, 0) for h in 正交)
        n_bad = sum(grp.get(h, 0) for h in 负交)
        label = 'ZA恢复后转正交概率高' if n_ok/n_total > 0.3 else 'ZA恢复后仍难转正交'
        print(f'| {cond} | {n_total} | {n_ok/n_total*100:.1f}% | {n_bad/n_total*100:.1f}% | {label} |')

print_outcomes('戊簇', 戊簇_总, 戊簇_结局, 戊簇_长度分组, 戊簇_ZA恢复)
print_outcomes('己簇', 己簇_总, 己簇_结局, 己簇_长度分组, 己簇_ZA恢复)

# ── 汇总对比表 ──
print(f'\n{"="*60}')
print('汇总：负交->正交转变成功率 vs 正交->负交')
print(f'{"="*60}')
print()
print('| 方向 | 起始护型 | 簇数 | 转正交 | 转甲 | 转乙 | 维持负交 | 未结束 |')
print(f'|:----|:--------|:----:|:------:|:----:|:----:|:--------:|:-----:|')

for label, name, total, outcomes in [('负交->正交', '戊簇', 戊簇_总, 戊簇_结局),
                               ('负交->正交', '己簇', 己簇_总, 己簇_结局)]:
    if total == 0:
        print(f'| {label} | {name} | 0 | - | - | - | - | - |')
        continue
    n_ok = sum(outcomes.get(h, 0) for h in ['甲','乙'])
    n_甲 = outcomes.get('甲', 0)
    n_乙 = outcomes.get('乙', 0)
    n_bad = sum(outcomes.get(h, 0) for h in ['丙','丁','戊','己'])
    n_end = outcomes.get('', 0)
    print(f'| {label} | {name} | {total} | {n_ok/total*100:.1f}% | {n_甲/total*100:.1f}% | {n_乙/total*100:.1f}% | {n_bad/total*100:.1f}% | {n_end/total*100:.1f}% |')

print(f'\n对比：乙簇（正交->负交方向，数据来自2.3.4.1）')
print(f'| 方向 | 起始护型 | 簇数 | 恢复正交 | 恶化到丙 | 恶化到丁 | 未结束 |')
print(f'|:----|:--------|:----:|:--------:|:--------:|:--------:|:-----:|')
print(f'| 正交->负交 | 乙簇(ZA<0) | 601,616 | 58.1% | 37.3% | 4.5% | 0.2% |')