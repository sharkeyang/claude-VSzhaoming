#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周线 WXAB 由正转负 前置状态验证（镜面对称四情形）

镜面对称 WXAB 由负转正四情形：
(1) 前周WTAB=1（转正）→ 前周WTAB=-1（转负）
(2) 己+前WTZB>0+升排（转甲）→ 丙/丁+前WTZB<0+跌排（转坏）
(3) 戊+前WTZA>0+升排+连阳（转正交）→ 甲乙+前WTZA<0+跌排+连阴（转负）
(4) 前WTZA<0今WTZA>0（转正交）→ 前WTZA>0今WTZA<0（转负）

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表周转负四情形.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/周转负四情形结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])  # [n, hit]

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
        df['prev_AB'] = df['AB周'].shift(1)
        df['prev_WXZA'] = df['WXZA'].shift(1)
        df['prev_WXZB'] = df['WXZB'].shift(1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['跌排'] = df['柱排str'].str.startswith('跌')
        df['连阴'] = df['柱排str'].str.startswith('跌') & df['柱排str'].str.contains('连')
        df['升排'] = df['柱排str'].str.startswith('升')

        # 正交护型（甲/乙/己）与非正交（丙/丁/戊）
        df['正交'] = df['hx'].isin(['甲', '乙', '己'])
        df['非正交'] = df['hx'].isin(['丙', '丁', '戊'])

        def mark(cond, name, target):
            """target: '转负'(正交→丙丁戊) / '转坏'(丙→丁/戊) / '维持负'(非正交→仍非正交)"""
            if target == '转负':
                sub = df[cond & df['正交']]
                hit = sub['next_hx'].isin(['丙', '丁', '戊'])
            elif target == '转坏':
                # 丙→丁/戊 才算转坏（丙转坏）；丁→丁 不算（丁本来就是死胡同）
                sub = df[cond & (df['hx'] == '丙')]
                hit = sub['next_hx'].isin(['丁', '戊'])
            else:  # 维持负
                sub = df[cond & df['非正交']]
                hit = sub['next_hx'].isin(['丙', '丁', '戊'])
            if sub.empty:
                return
            n = len(sub)
            s = stat[name]
            s[0] += n
            s[1] += int(hit.sum())

        # ===== 镜面对称四情形 =====
        # (1) 前周WTAB=-1（转负）：本周维持负
        mark(df['prev_AB'] == -1, '前周WTAB=-1_维持负', '维持负')
        # 前周WTAB=-1 + 本周跌排
        mark((df['prev_AB'] == -1) & (df['跌排']), '前周WTAB=-1+跌排_维持负', '维持负')
        # 对比：前周WTAB<-1
        mark(df['prev_AB'] < -1, '前周WTAB<-1_维持负', '维持负')

        # (2) 丙 + 前周WTZB<0 + WJA之下跌排：转坏（丙→丁/戊）
        mark((df['hx'] == '丙') & (df['prev_WXZB'] < 0) & (df['WXZA'] < 0) & (df['跌排']), '丙+前WTZB<0+跌排_转坏', '转坏')
        # 丙 + 前周WTZB<0（不管柱排）
        mark((df['hx'] == '丙') & (df['prev_WXZB'] < 0), '丙+前WTZB<0_转坏', '转坏')
        # 对比：丙 整体转坏
        mark(df['hx'] == '丙', '丙整体_转坏', '转坏')

        # (3) 乙 + 前周WTZA<0 + WJA之下跌排 + 连阴：转负（乙→丙丁戊）
        mark((df['hx'] == '乙') & (df['prev_WXZA'] < 0) & (df['WXZA'] < 0) & (df['跌排']) & (df['连阴']), '乙+前WTZA<0+跌排+连阴_转负', '转负')
        # 乙 + 前周WTZA<0 + 跌排
        mark((df['hx'] == '乙') & (df['prev_WXZA'] < 0) & (df['WXZA'] < 0) & (df['跌排']), '乙+前WTZA<0+跌排_转负', '转负')

        # (4) 前周WTZA>0，本周WTZA<0：转负
        mark((df['prev_WXZA'] > 0) & (df['WXZA'] < 0), '前WTZA>0今WTZA<0_转负', '转负')

    # 输出
    print(f'\n=== WXAB 由正转负前置状态（镜面对称）===')
    print(f'{"场景":<36} {"n":>8} {"命中":>7} {"命中%":>8}')
    print('-' * 64)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[1] / n * 100
        results.append((name, n, s[1], pct))
    results.sort(key=lambda x: -x[3])
    for name, n, hit, pct in results:
        print(f'{name:<36} {n:>8} {hit:>7} {pct:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '命中', '命中%'])
        for name, n, hit, pct in results:
            w.writerow([name, n, hit, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()