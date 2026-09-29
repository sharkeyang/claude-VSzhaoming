#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深度验证：WXAB>0 且 WXZB>0 能否作为主升判定标准，能否抓住所有主升？

用户问题（2026-09-29）：WXAB>0 且 WXZB>0 能否作为主升的判定标准，能否抓住所有主升？

验证两个维度：
1. 精确率（precision）：WXAB>0 且 WXZB>0 时，有多大比例处于主升？
   - 主升定义A：完全多头排列（站上全部5根均线 WXZA/WXZB/WXZC/WXZD/WXZE>0）
   - 主升定义B：本周周涨为正
2. 召回率（recall）：所有主升中，有多大比例满足 WXAB>0 且 WXZB>0？
   - 即"能否抓住所有主升"

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [14] ZA周=WXZA  [15] ZB周=WXZB  [16] ZC周=WXZC
    [17] ZD周=WXZD  [18] ZE周=WXZE  [20] AB周=WXAB

用法：
    python _产出物/_工具/vba表WXAB_WXZB主升判定验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB_WXZB主升判定验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计
    # 总样本
    n_total = 0
    # 主升定义A（完全多头）：站上5根均线
    n_A = 0
    # 主升定义B（周涨>0）
    n_B = 0
    # 条件 C = WXAB>0 且 WXZB>0
    n_C = 0
    # C 且 A（条件命中且完全多头）
    n_C_and_A = 0
    # C 且 B（条件命中且周涨>0）
    n_C_and_B = 0
    # A 且 C（完全多头且条件命中）
    n_A_and_C = 0
    # B 且 C（周涨>0且条件命中）
    n_B_and_C = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 14, 15, 16, 17, 18, 20])
            df.columns = ['周涨', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE', 'WXAB']
        except Exception:
            continue
        for c in ['周涨', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE', 'WXAB'])
        if df.empty:
            continue

        # 完全多头（站上5根均线）
        A = (df[['WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE']] > 0).all(axis=1)
        # 周涨>0
        B = df['周涨'] > 0
        # 条件 C = WXAB>0 且 WXZB>0
        C = (df['WXAB'] > 0) & (df['WXZB'] > 0)

        n_total += len(df)
        n_A += int(A.sum())
        n_B += int(B.sum())
        n_C += int(C.sum())
        n_C_and_A += int((C & A).sum())
        n_C_and_B += int((C & B).sum())
        n_A_and_C += int((A & C).sum())
        n_B_and_C += int((B & C).sum())

    # 输出
    print(f'\n=== WXAB>0 且 WXZB>0 主升判定验证 ===')
    print(f'总样本: {n_total}')
    print(f'\n主升定义A（完全多头，站上5根均线）: {n_A} ({n_A/n_total*100:.1f}%)')
    print(f'主升定义B（周涨>0）: {n_B} ({n_B/n_total*100:.1f}%)')
    print(f'条件C（WXAB>0且WXZB>0）: {n_C} ({n_C/n_total*100:.1f}%)')
    print(f'\n--- 精确率（条件命中时处于主升的比例）---')
    print(f'C 且 A: {n_C_and_A}/{n_C} = {n_C_and_A/n_C*100:.1f}%  （条件命中时完全多头的比例）')
    print(f'C 且 B: {n_C_and_B}/{n_C} = {n_C_and_B/n_C*100:.1f}%  （条件命中时周涨>0的比例）')
    print(f'\n--- 召回率（主升中满足条件的比例，能否抓住所有主升）---')
    print(f'A 且 C: {n_A_and_C}/{n_A} = {n_A_and_C/n_A*100:.1f}%  （完全多头中满足条件的比例）')
    print(f'B 且 C: {n_B_and_C}/{n_B} = {n_B_and_C/n_B*100:.1f}%  （周涨>0中满足条件的比例）')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['指标', '值'])
        w.writerow(['总样本', n_total])
        w.writerow(['主升A(完全多头)', f'{n_A} ({n_A/n_total*100:.1f}%)'])
        w.writerow(['主升B(周涨>0)', f'{n_B} ({n_B/n_total*100:.1f}%)'])
        w.writerow(['条件C(WXAB>0且WXZB>0)', f'{n_C} ({n_C/n_total*100:.1f}%)'])
        w.writerow(['精确率A(C且A/C)', f'{n_C_and_A/n_C*100:.1f}%'])
        w.writerow(['精确率B(C且B/C)', f'{n_C_and_B/n_C*100:.1f}%'])
        w.writerow(['召回率A(A且C/A)', f'{n_A_and_C/n_A*100:.1f}%'])
        w.writerow(['召回率B(B且C/B)', f'{n_B_and_C/n_B*100:.1f}%'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()