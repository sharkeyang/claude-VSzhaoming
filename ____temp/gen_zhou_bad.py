# -*- coding: utf-8 -*-
"""
重新生成 vba表周策分坏.txt（修正转坏去向）
修正：乙(ZA≤0)、丙、丁 的"维持自身"也算转坏
转好率不变（vba表周策分好.txt 无需改）
"""
import csv, os, json, io
from collections import defaultdict

高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
DATA_DIR = '昭明算展/谕组周'
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']
WXCD_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

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
    if not wxcd:
        return None
    c = wxcd[0]
    if c in ('金', '银', '唏', '嘘', '尿', '屎'):
        return c
    return None

# 修正版转坏去向（用户确认）
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

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(os.listdir(DATA_DIR))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

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
        prev = None
        for row in r:
            if len(row) < 15:
                continue
            cur = hx_key(row[4], row[14])
            if not cur:
                prev = None
                continue
            wc = wxcd_name(row[13])
            if not wc:
                prev = None
                continue
            if prev:
                p_hx, p_wc = prev
                trans[(p_wc, p_hx, cur)] += 1
            prev = (cur, wc)

# 生成 vba表周策分坏.txt（修正版）
out = io.open('_产出物/_工具/vba表周策分坏.txt', 'w', encoding='gbk')
out.write('名称\t编码\n')
for wc in WXCD_ORDER:
    for hx in HX_ORDER:
        total = sum(v for (w, c, n), v in trans.items() if w == wc and c == hx)
        if total == 0:
            continue
        bad = sum(trans.get((wc, hx, nxt), 0) for nxt in BAD_NEW[hx]) / total * 100
        bad_int = int(round(bad))
        if bad_int >= 30:
            code = f'W{bad_int}'
        else:
            code = f'_{bad_int}'
        out.write(f'{wc}|{hx}\t{code}\n')
out.close()
print('Done: vba表周策分坏.txt 已生成（修正版）')