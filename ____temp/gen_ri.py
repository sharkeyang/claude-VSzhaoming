# -*- coding: utf-8 -*-
"""
生成 vba表日策分坏.txt / vba表日策分好.txt
基于 DXCD × 日护型 转移矩阵，用修正版转坏去向计算转坏率，转好率=转为甲或乙(ZA>0)
"""
import csv, os, json, io
from collections import defaultdict

高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
DATA_DIR = '昭明算展/谕组日'
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']
DXCD_ORDER = ['上', '中', '下', '忐', '忠', '忑']

def hx_key(dxab, za):
    if len(dxab) < 2:
        return None
    hx = HX_MAP.get(dxab[0])
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
files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

trans = defaultdict(int)
for i, fname in enumerate(files):
    if i % 1000 == 0:
        print(f'  [加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_', '').replace('.csv', '')
    if board_map.get(cidl, '') not in 高波池板块:
        continue
    with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        prev = None  # (hx, dxcd)
        for row in r:
            if len(row) < 51:
                continue
            cur = hx_key(row[9], row[13])
            if not cur:
                prev = None
                continue
            cd = row[8].strip()
            if cd not in DXCD_ORDER:
                prev = None
                continue
            if prev:
                p_hx, p_cd = prev
                trans[(p_cd, p_hx, cur)] += 1
            prev = (cur, cd)

# 生成 vba表日策分坏.txt
out_bad = io.open('_产出物/_工具/vba表日策分坏.txt', 'w', encoding='gbk')
out_bad.write('名称\t编码\n')
for cd in DXCD_ORDER:
    for hx in HX_ORDER:
        total = sum(v for (c, h, n), v in trans.items() if c == cd and h == hx)
        if total == 0:
            continue
        bad = sum(trans.get((cd, hx, nxt), 0) for nxt in BAD_NEW[hx]) / total * 100
        bad_int = int(round(bad))
        if bad_int >= 30:
            code = f'W{bad_int}'
        else:
            code = f'_{bad_int}'
        out_bad.write(f'{cd}|{hx}\t{code}\n')
out_bad.close()

# 生成 vba表日策分好.txt
out_good = io.open('_产出物/_工具/vba表日策分好.txt', 'w', encoding='gbk')
out_good.write('名称\t编码\n')
for cd in DXCD_ORDER:
    for hx in HX_ORDER:
        total = sum(v for (c, h, n), v in trans.items() if c == cd and h == hx)
        if total == 0:
            continue
        if hx in ('甲', '乙(ZA>0)'):
            good = trans.get((cd, hx, hx), 0) / total * 100  # 维持率
        else:
            good = (trans.get((cd, hx, '甲'), 0) + trans.get((cd, hx, '乙(ZA>0)'), 0)) / total * 100
        good_int = int(round(good))
        if good_int >= 30:
            code = f'G{good_int}'
        else:
            code = f'_{good_int}'
        out_good.write(f'{cd}|{hx}\t{code}\n')
out_good.close()
print('Done: vba表日策分坏.txt / vba表日策分好.txt 已生成')