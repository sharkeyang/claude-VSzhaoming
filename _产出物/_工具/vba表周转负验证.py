#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周线 WXAB 由正转负 前置状态验证（镜面对称）

镜面对称 WXAB 由负转正前置状态：
由负转正：戊 + 前WTZA>0 + WJA之上升排 + 连阳 → 转正交
由正转负（镜面）：甲/乙 + 前WTZA<0 + WJA之下跌排 + 连阴 → 转负（转丙丁戊）

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表周转负验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/周转负验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])  # [n, 转负(正交→丙丁戊)]

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 6, 14, 15, 16, 20])
            df.columns = ['WXAB护型', '柱排周', 'WXZA', 'WXZB', 'WXZC', 'AB周']
        except Exception:
            continue
        for c in ['WXZA', 'WXZB', 'WXZC', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['WXZA'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        df['next_hx'] = df['hx'].shift(-1)
        df['prev_hx'] = df['hx'].shift(1)
        df['prev_WXZA'] = df['WXZA'].shift(1)
        df['prev_WXZB'] = df['WXZB'].shift(1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['跌排'] = df['柱排str'].str.startswith('跌')
        df['连阴'] = df['柱排str'].str.startswith('跌') & df['柱排str'].str.contains('连')
        df['升孕'] = df['柱排str'].str.startswith('升') & df['柱排str'].str.contains('孕')

        # 正交护型（甲/乙/己）
        df['正交'] = df['hx'].isin(['甲', '乙', '己'])

        def mark(cond, name):
            sub = df[cond & df['正交']]
            if sub.empty:
                return
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_bad = int(next_hx.isin(['丙', '丁', '戊']).sum())
            s = stat[name]
            s[0] += n
            s[1] += to_bad

        # ===== WXAB 由正转负前置状态（镜面对称）=====
        # 甲/乙 + 前WTZA<0 + WJA之下跌排
        mark((df['hx'].isin(['甲', '乙'])) & (df['prev_WXZA'] < 0) & (df['WXZA'] < 0) & (df['跌排']), '转负_甲乙+前WTZA<0+跌排')
        # 甲/乙 + 前WTZA<0 + 跌排 + 连阴
        mark((df['hx'].isin(['甲', '乙'])) & (df['prev_WXZA'] < 0) & (df['WXZA'] < 0) & (df['跌排']) & (df['连阴']), '转负_甲乙+前WTZA<0+跌排+连阴')
        # 甲/乙 + 前WTZA<0（不管柱排）
        mark((df['hx'].isin(['甲', '乙'])) & (df['prev_WXZA'] < 0), '转负_甲乙+前WTZA<0')
        # 甲/乙 + 前WTZA>0（对比）
        mark((df['hx'].isin(['甲', '乙'])) & (df['prev_WXZA'] > 0), '转负_甲乙+前WTZA>0')

        # ===== 对比基线 =====
        mark(df['正交'], '转负_正交整体')

    # 输出
    print(f'\n=== WXAB 由正转负前置状态（镜面对称）===')
    print(f'{"场景":<30} {"n":>8} {"转负":>7} {"转负%":>8}')
    print('-' * 60)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[1] / n * 100
        results.append((name, n, s[1], pct))
    results.sort(key=lambda x: -x[3])
    for name, n, bad, pct in results:
        print(f'{name:<30} {n:>8} {bad:>7} {pct:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '转负', '转负%'])
        for name, n, bad, pct in results:
            w.writerow([name, n, bad, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()