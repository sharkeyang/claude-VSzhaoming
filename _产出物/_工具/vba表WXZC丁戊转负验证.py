#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：WXZC>0 时若出现 WXAB 丁/戊，是否必然会导致 WXZC<0？

用户假设（2026-09-29）：WXZC>0（价格在 WJC 之上）时，如果出现 WXAB 丁/戊
（非正交护型，丁=死水终点，戊=下跌护型），是否必然导致 WXZC<0（跌破 WJC）？

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型  [16] ZC周 = WXZC（价格 vs WJC 交叉）

验证：WXZC>0 且 WXAB=丁/戊 时，后续 N 周内 WXZC 转负（<0）的概率。
对比：WXZC>0 且 WXAB=甲/乙/丙/己 时，后续 N 周内 WXZC 转负的概率。

用法：
    python _产出物/_工具/vba表WXZC丁戊转负验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXZC丁戊转负验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：护型 -> [n, 1周转负, 3周转负, 5周转负, 10周转负]
    stat = defaultdict(lambda: [0, 0, 0, 0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 16])
            df.columns = ['WXAB护型', 'WXZC']
        except Exception:
            continue
        df['WXZC'] = pd.to_numeric(df['WXZC'], errors='coerce')
        df = df.dropna(subset=['WXZC'])
        if df.empty:
            continue

        hx = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        zc = df['WXZC'].values
        n = len(df)

        # WXZC>0 时，看后续 N 周内是否转负
        for idx in range(n):
            if zc[idx] > 0:
                h = hx.iloc[idx]
                if h is None:
                    continue
                s = stat[h]
                s[0] += 1
                # 1周内转负
                if idx + 1 < n and zc[idx + 1] < 0:
                    s[1] += 1
                # 3周内转负
                if any(zc[idx + k] < 0 for k in range(1, min(4, n - idx))):
                    s[2] += 1
                # 5周内转负
                if any(zc[idx + k] < 0 for k in range(1, min(6, n - idx))):
                    s[3] += 1
                # 10周内转负
                if any(zc[idx + k] < 0 for k in range(1, min(11, n - idx))):
                    s[4] += 1

    # 输出
    print(f'\n=== WXZC>0 时，各护型后续 N 周内 WXZC 转负概率 ===')
    print(f'{"护型":<8} {"n":>8} {"1周":>6} {"3周":>6} {"5周":>6} {"10周":>6}')
    print('-' * 50)
    results = []
    for h in ['甲', '乙', '丙', '丁', '戊', '己']:
        s = stat[h]
        if s[0] == 0:
            continue
        n = s[0]
        results.append((h, n, s[1] / n * 100, s[2] / n * 100, s[3] / n * 100, s[4] / n * 100))
    # 按10周转负率排序
    results.sort(key=lambda x: -x[5])
    for h, n, p1, p3, p5, p10 in results:
        print(f'{h:<8} {n:>8} {p1:>5.1f}% {p3:>5.1f}% {p5:>5.1f}% {p10:>5.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['护型', 'n', '1周转负%', '3周转负%', '5周转负%', '10周转负%'])
        for h, n, p1, p3, p5, p10 in results:
            w.writerow([h, n, f'{p1:.1f}', f'{p3:.1f}', f'{p5:.1f}', f'{p10:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()