# -*- coding: utf-8 -*-
"""
验证周策分好/坏的生成逻辑：从周线数据计算 WXCD × 周护型 的转坏率/转好率
对比 vba表周策分坏.txt / vba表周策分好.txt 的值，确认计算方式
"""
import csv, os, json, io
from collections import defaultdict

高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
DATA_DIR = '昭明算展/谕组周'
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def hx_key(wxab, za):
    if len(wxab) < 2:
        return None
    hx = HX_MAP.get(wxab[0])
    if not hx:
        return None
    try:
        za_f = float(za)
    except:
        za_f = 0
    if hx == '乙':
        return '乙(ZA>0)' if za_f > 0 else '乙(ZA≤0)'
    if hx == '戊':
        return '戊(ZA>0)' if za_f > 0 else '戊(ZA≤0)'
    return hx

def wxcd_name(wxcd):
    """WXCD 首字符 → 金/银/唏/嘘/尿/屎"""
    if not wxcd:
        return None
    c = wxcd[0]
    if c in ('金', '银', '唏', '嘘', '尿', '屎'):
        return c
    return None

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(os.listdir(DATA_DIR))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

# (wxcd, cur, nxt) -> count
trans = defaultdict(int)
for i, fname in enumerate(files):
    if i % 1000 == 0:
        print(f'  [加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组周_', '').replace('.csv', '')
    if board_map.get(cidl, '') not in 高波池板块:
        continue
    with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        prev = None  # (hx, wxcd)
        for row in r:
            if len(row) < 15:
                continue
            cur = hx_key(row[4], row[14])  # WXAB, ZA周
            if not cur:
                prev = None
                continue
            wc = wxcd_name(row[13])  # WXCD
            if not wc:
                prev = None
                continue
            if prev:
                p_hx, p_wc = prev
                trans[(p_wc, p_hx, cur)] += 1
            prev = (cur, wc)

# 计算转坏率/转好率
# 转坏去向（旧版，§3.8.1.1）
BAD_OLD = {
    '甲': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA>0)': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA≤0)': ['丙', '丁'],
    '丙': ['丁'],
    '丁': ['戊(ZA>0)', '戊(ZA≤0)'],
    '戊(ZA>0)': ['戊(ZA≤0)'],
    '戊(ZA≤0)': ['戊(ZA≤0)'],  # 维持也算
    '己': ['戊(ZA>0)', '戊(ZA≤0)'],
}
# 转坏去向（修正版，用户确认）
BAD_NEW = {
    '甲': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA>0)': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA≤0)': ['乙(ZA≤0)', '丙', '丁'],  # 维持也算
    '丙': ['丙', '丁'],  # 维持也算
    '丁': ['丁', '戊(ZA>0)', '戊(ZA≤0)'],  # 维持也算
    '戊(ZA>0)': ['戊(ZA≤0)'],
    '戊(ZA≤0)': ['戊(ZA≤0)'],  # 维持也算
    '己': ['戊(ZA>0)', '戊(ZA≤0)'],
}
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']
WXCD_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

out = io.open('____temp/_verify_zhou.txt', 'w', encoding='utf-8')
def O(s=''):
    out.write(s + '\n')

# 对比旧版转坏率 vs vba表
O('=== 旧版转坏率 vs vba表周策分坏 ===')
for wc in WXCD_ORDER:
    row = []
    for hx in HX_ORDER:
        total = sum(v for (w, c, n), v in trans.items() if w == wc and c == hx)
        if total == 0:
            row.append('—')
            continue
        bad = sum(trans.get((wc, hx, nxt), 0) for nxt in BAD_OLD[hx]) / total * 100
        row.append(f'{bad:.0f}')
    O(f'{wc}: ' + ' | '.join(row))

# 修正版转坏率
O('')
O('=== 修正版转坏率 ===')
for wc in WXCD_ORDER:
    row = []
    for hx in HX_ORDER:
        total = sum(v for (w, c, n), v in trans.items() if w == wc and c == hx)
        if total == 0:
            row.append('—')
            continue
        bad = sum(trans.get((wc, hx, nxt), 0) for nxt in BAD_NEW[hx]) / total * 100
        row.append(f'{bad:.0f}')
    O(f'{wc}: ' + ' | '.join(row))

# 转好率
O('')
O('=== 转好率 ===')
for wc in WXCD_ORDER:
    row = []
    for hx in HX_ORDER:
        total = sum(v for (w, c, n), v in trans.items() if w == wc and c == hx)
        if total == 0:
            row.append('—')
            continue
        if hx in ('甲', '乙(ZA>0)'):
            good = trans.get((wc, hx, hx), 0) / total * 100  # 维持率
        else:
            good = (trans.get((wc, hx, '甲'), 0) + trans.get((wc, hx, '乙(ZA>0)'), 0)) / total * 100
        row.append(f'{good:.0f}')
    O(f'{wc}: ' + ' | '.join(row))
out.close()
print('Done')