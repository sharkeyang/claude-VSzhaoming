#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：WXAB>0 且 WXZB>0 是否可认为主升特征（用户观点）

用户观点（2026-09-29）：不同意"只有完全多头排列才是升势"。
用户认为：WXAB>0（短期均线正交 JA>JB）且 WXZB>0（价格在 WJB=EMA12 之上），
按照"行乞的心态"（谨慎/保守），可以认为主升的特征。

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR（临高幅=下周高幅）
    [15] ZB周=WXZB（价格vs WJB=EMA12）  [16] ZC周=WXZC（vs WJC=EMA26）
    [20] AB周=WXAB（JA vs JB 交叉）

验证：WXAB>0 且 WXZB>0 时，平均周涨/正周涨/HR 如何，对比其他条件。

用法：
    python _产出物/_工具/vba表WXAB_WXZB主升验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB_WXZB主升验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：场景 -> [n, 周涨和, 正周涨数, HR和]
    stat = defaultdict(lambda: [0, 0.0, 0, 0.0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 3, 15, 16, 20])
            df.columns = ['周涨', 'HR', 'WXZB', 'WXZC', 'WXAB']
        except Exception:
            continue
        for c in ['周涨', 'HR', 'WXZB', 'WXZC', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'HR', 'WXZB', 'WXZC', 'WXAB'])
        if df.empty:
            continue

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += float(sub['周涨'].sum())
            s[2] += int((sub['周涨'] > 0).sum())
            s[3] += float(sub['HR'].sum())

        # 用户观点：WXAB>0 且 WXZB>0
        mark((df['WXAB'] > 0) & (df['WXZB'] > 0), 'WXAB>0+WXZB>0')
        # 对比
        mark(df['WXZB'] > 0, 'WXZB>0')
        mark(df['WXZC'] > 0, 'WXZC>0')
        mark(df['WXAB'] > 0, 'WXAB>0')
        mark((df['WXAB'] > 0) & (df['WXZC'] > 0), 'WXAB>0+WXZC>0')
        mark((df['WXZB'] > 0) & (df['WXZC'] > 0), 'WXZB>0+WXZC>0')
        mark((df['WXAB'] > 0) & (df['WXZB'] > 0) & (df['WXZC'] > 0), 'WXAB>0+WXZB>0+WXZC>0')
        # 完全多头（站上5根均线）
        mark((df['WXZC'] > 0), 'WXZC>0')

    # 输出
    print(f'\n=== WXAB>0 且 WXZB>0 主升特征验证 ===')
    print(f'{"场景":<26} {"n":>10} {"平均周涨":>9} {"正周涨%":>8} {"平均HR":>8}')
    print('-' * 65)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        avg_zhou = s[1] / n
        p_zhou = s[2] / n * 100
        avg_hr = s[3] / n
        results.append((name, n, avg_zhou, p_zhou, avg_hr))
    results.sort(key=lambda x: -x[2])
    for name, n, avg_zhou, p_zhou, avg_hr in results:
        print(f'{name:<26} {n:>10} {avg_zhou:>9.3f}% {p_zhou:>7.1f}% {avg_hr:>8.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '平均周涨%', '正周涨%', '平均HR%'])
        for name, n, avg_zhou, p_zhou, avg_hr in results:
            w.writerow([name, n, f'{avg_zhou:.3f}', f'{p_zhou:.1f}', f'{avg_hr:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()