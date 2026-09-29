#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：上升过程与 WXZC>0、WXAB>0 强相关，及介入条件

用户假设（2026-09-29）：
1. 上升过程与两个特征强相关：WXZC>0（价格在WJC之上）和 WXAB>0（正交）
2. 对于 WXZC<0：强制要求 WXAB>0 才能介入
3. 对于 WXZC>0：可接受 WXAB>0 且 WXZB>0，但 WXZB<0（丙丁戊）千万小心

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [3] HR（临高幅=下周高幅）  [4] WXAB护型  [15] ZB周=WXZB  [16] ZC周=WXZC  [20] AB周=WXAB交叉

验证指标：P(HR≥3%) = 下周冲高概率（周冲≥3%）

用法：
    python _产出物/_工具/vba表WXZC_WXAB介入验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXZC_WXAB介入验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：场景 -> [n, hit3, HR和]
    stat = defaultdict(lambda: [0, 0, 0.0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[3, 4, 15, 16, 20])
            df.columns = ['HR', 'WXAB护型', 'WXZB', 'WXZC', 'WXAB']
        except Exception:
            continue
        for c in ['HR', 'WXZB', 'WXZC', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['HR', 'WXZB', 'WXZC', 'WXAB'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        df['hit3'] = (df['HR'] >= 3).astype(int)

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += int(sub['hit3'].sum())
            s[2] += float(sub['HR'].sum())

        # ===== 1. 上升过程与 WXZC>0、WXAB>0 相关性 =====
        mark(df['WXZC'] > 0, 'WXZC>0')
        mark(df['WXZC'] <= 0, 'WXZC<=0')
        mark(df['WXAB'] > 0, 'WXAB>0')
        mark(df['WXAB'] <= 0, 'WXAB<=0')
        # 组合
        mark((df['WXZC'] > 0) & (df['WXAB'] > 0), 'WXZC>0+WXAB>0')
        mark((df['WXZC'] > 0) & (df['WXAB'] <= 0), 'WXZC>0+WXAB<=0')
        mark((df['WXZC'] <= 0) & (df['WXAB'] > 0), 'WXZC<=0+WXAB>0')
        mark((df['WXZC'] <= 0) & (df['WXAB'] <= 0), 'WXZC<=0+WXAB<=0')

        # ===== 2. WXZC<0 时 WXAB>0 的介入价值 =====
        mark((df['WXZC'] < 0) & (df['WXAB'] > 0), 'WXZC<0+WXAB>0')
        mark((df['WXZC'] < 0) & (df['WXAB'] <= 0), 'WXZC<0+WXAB<=0')

        # ===== 3. WXZC>0 时 WXZB 正负区分 =====
        mark((df['WXZC'] > 0) & (df['WXAB'] > 0) & (df['WXZB'] > 0), 'WXZC>0+WXAB>0+WXZB>0')
        mark((df['WXZC'] > 0) & (df['WXAB'] > 0) & (df['WXZB'] <= 0), 'WXZC>0+WXAB>0+WXZB<=0')
        # WXZB<0 时护型分布（丙丁戊）
        mark((df['WXZC'] > 0) & (df['WXZB'] < 0) & (df['hx'].isin(['丙', '丁', '戊'])), 'WXZC>0+WXZB<0+丙丁戊')
        mark((df['WXZC'] > 0) & (df['WXZB'] < 0) & (df['hx'].isin(['甲', '乙', '己'])), 'WXZC>0+WXZB<0+甲乙己')

    # 输出
    print(f'\n=== 上升过程与 WXZC>0、WXAB>0 相关性（P(HR≥3%)）===')
    print(f'{"场景":<28} {"n":>10} {"P(≥3%)":>8} {"均HR":>7}')
    print('-' * 60)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        p3 = s[1] / n * 100
        avg = s[2] / n
        results.append((name, n, p3, avg))
    results.sort(key=lambda x: -x[2])
    for name, n, p3, avg in results:
        print(f'{name:<28} {n:>10} {p3:>7.2f}% {avg:>6.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', 'P(≥3%)', '均HR'])
        for name, n, p3, avg in results:
            w.writerow([name, n, f'{p3:.2f}', f'{avg:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()