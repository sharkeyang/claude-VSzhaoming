#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
判断升势：用均线多头结构（价格站上均线数量），而非单一 P(≥3%)

用户反馈（2026-09-29）：不要用 P(≥3%) 单一条件判断升势，应观察图形——
图形上判断升势的核心是均线系统的多头结构：价格站上几根均线、均线是否多头排列。

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR（临高幅=下周高幅）
    [14] ZA周=WXZA（价格vs WJA=EMA5）  [15] ZB周=WXZB（vs WJB=EMA12）
    [16] ZC周=WXZC（vs WJC=EMA26）  [17] ZD周=WXZD（vs WJD=EMA60）
    [18] ZE周=WXZE（vs WJE=EMA120）

升势度量：价格站上均线数量（WXZA>0 + WXZB>0 + WXZC>0 + WXZD>0 + WXZE>0 的个数，0-5）
验证：站上不同数量均线时，后续周涨/HR 如何（多头排列程度 vs 升势）

用法：
    python _产出物/_工具/vba表升势均线结构验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/升势均线结构验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：站上均线数量 -> [n, 周涨和, HR和, 正周涨数, 正HR数]
    stat = defaultdict(lambda: [0, 0.0, 0.0, 0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 3, 14, 15, 16, 17, 18])
            df.columns = ['周涨', 'HR', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE']
        except Exception:
            continue
        for c in ['周涨', 'HR', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'HR', 'WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE'])
        if df.empty:
            continue

        # 价格站上均线数量（0-5）
        n_above = (df[['WXZA', 'WXZB', 'WXZC', 'WXZD', 'WXZE']] > 0).sum(axis=1)
        for k in range(6):
            sub = df[n_above == k]
            if sub.empty:
                continue
            s = stat[k]
            s[0] += len(sub)
            s[1] += float(sub['周涨'].sum())
            s[2] += float(sub['HR'].sum())
            s[3] += int((sub['周涨'] > 0).sum())
            s[4] += int((sub['HR'] > 0).sum())

    # 输出
    print(f'\n=== 升势判断：价格站上均线数量（多头排列程度）===')
    print(f'{"站上均线数":<10} {"n":>10} {"平均周涨":>9} {"正周涨%":>8} {"平均HR":>8} {"正HR%":>7}')
    print('-' * 60)
    results = []
    for k in range(6):
        s = stat[k]
        if s[0] == 0:
            continue
        n = s[0]
        avg_zhou = s[1] / n
        avg_hr = s[2] / n
        p_zhou = s[3] / n * 100
        p_hr = s[4] / n * 100
        results.append((k, n, avg_zhou, p_zhou, avg_hr, p_hr))
    for k, n, avg_zhou, p_zhou, avg_hr, p_hr in results:
        print(f'{k:<10} {n:>10} {avg_zhou:>9.3f}% {p_zhou:>7.1f}% {avg_hr:>8.2f}% {p_hr:>6.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['站上均线数', 'n', '平均周涨%', '正周涨%', '平均HR%', '正HR%'])
        for k, n, avg_zhou, p_zhou, avg_hr, p_hr in results:
            w.writerow([k, n, f'{avg_zhou:.3f}', f'{p_zhou:.1f}', f'{avg_hr:.2f}', f'{p_hr:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()