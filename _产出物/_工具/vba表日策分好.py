#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表日策分好.txt
基于 DXCD × 日护型 转移矩阵，计算转好率
转好率定义：当前护型转为 甲 或 乙(ZA>0) 的概率；甲/乙(ZA>0) 已最优，转好率=维持率
编码格式：G(转好率≥30%值得关注)/_(<30%安全) + 转好率取整（如 G83、_20）
数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），与VBA中 IQQQ跨码工具_查日策分好 对应

用法：
    python _产出物/_工具/vba表日策分好.py
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

# 转好去向：只算→甲 或 →乙(ZA>0)
# 甲/乙(ZA>0) 已是最优，转好率=维持率（转自身）
GOOD_PATHS = {
    '甲': ['甲'],
    '乙(ZA>0)': ['乙(ZA>0)'],
    '乙(ZA≤0)': ['乙(ZA>0)', '甲'],
    '丙': ['甲', '乙(ZA>0)'],
    '丁': ['甲', '乙(ZA>0)'],
    '戊(ZA>0)': ['甲', '乙(ZA>0)'],
    '戊(ZA≤0)': ['甲', '乙(ZA>0)'],
    '己': ['甲', '乙(ZA>0)'],
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

# 生成 vba表日策分好.txt
out_good = io.open('_产出物/_工具/vba表日策分好.txt', 'w', encoding='gbk')
out_good.write('名称\t编码\n')
for cd in DXCD_ORDER:
    for hx in HX_ORDER:
        total = sum(v for (c, h, n), v in trans.items() if c == cd and h == hx)
        if total == 0:
            continue
        good = sum(trans.get((cd, hx, nxt), 0) for nxt in GOOD_PATHS[hx]) / total * 100
        good_int = int(round(good))
        if good_int >= 30:
            code = f'G{good_int}'
        else:
            code = f'_{good_int}'
        out_good.write(f'{cd}|{hx}\t{code}\n')
out_good.close()
print('Done: vba表日策分好.txt 已生成')
