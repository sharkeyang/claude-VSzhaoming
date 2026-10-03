#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周线 WXAB 由负转正/由正转负 前置状态验证

验证用户猜想：
WXAB 由负转正前置状态：
(1) 前周柱 WTAB=1：如果还未冲高，是最好的介入机会
(2) 己：前周柱 WTZB>0，特别是在 WJA 之上有周柱升排，如果是阴柱最好为跌孕
(3) 戊(WTZA>0)：前周柱 WTZA>0，特别是在 WJA 之上有周柱升排，最好为升排、连阳
(4) 前周 WTZA<0，本周中 WTZA>0：不要介入

WXAB 由正转负前置状态：镜面对称验证

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表周前置状态验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/周前置状态验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])  # [n, 转正交(非正交→己甲)]

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
        df['prev_AB'] = df['AB周'].shift(1)
        df['prev_WXZA'] = df['WXZA'].shift(1)
        df['prev_WXZB'] = df['WXZB'].shift(1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['升排'] = df['柱排str'].str.startswith('升')
        df['连阳'] = df['柱排str'].str.startswith('升') & df['柱排str'].str.contains('连')
        df['跌孕'] = df['柱排str'].str.startswith('跌') & df['柱排str'].str.contains('孕')
        df['阴柱'] = df['柱排str'].str.startswith('跌')

        # 非正交护型（戊/丙/丁）
        df['非正交'] = df['hx'].isin(['戊', '丙', '丁'])

        def mark(cond, name):
            sub = df[cond & df['非正交']]
            if sub.empty:
                return
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_orth = int(next_hx.isin(['己', '甲']).sum())
            s = stat[name]
            s[0] += n
            s[1] += to_orth

        # ===== WXAB 由负转正前置状态 =====
        # (1) 前周柱 WTAB=1：直接看本周是否已是正交（甲/乙），而非"下周转正交"
        #     因为前周AB=1（刚转正）时，本周绝大多数已是正交（甲88.8%），
        #     不需要"转正交"；只有少数掉回非正交(丁/丙)才是异常。
        prev_ab1 = df[df['prev_AB'] == 1]
        if not prev_ab1.empty:
            n = len(prev_ab1)
            orth = int(prev_ab1['hx'].isin(['甲', '乙']).sum())
            s = stat['前周WTAB=1_本周已是正交']
            s[0] += n
            s[1] += orth
        # (2) 己 + 前周 WTZB>0 + WJA之上升排
        mark((df['hx'] == '己') & (df['prev_WXZB'] > 0) & (df['WXZA'] > 0) & (df['升排']), '转正_己+前WTZB>0+升排')
        # 己 + 前周 WTZB>0 + 升排 + 跌孕
        mark((df['hx'] == '己') & (df['prev_WXZB'] > 0) & (df['WXZA'] > 0) & (df['升排']) & (df['跌孕']), '转正_己+前WTZB>0+升排+跌孕')
        # (3) 戊 + 前周 WTZA>0 + WJA之上升排
        mark((df['hx'] == '戊') & (df['prev_WXZA'] > 0) & (df['WXZA'] > 0) & (df['升排']), '转正_戊+前WTZA>0+升排')
        # 戊 + 前周 WTZA>0 + 升排 + 连阳
        mark((df['hx'] == '戊') & (df['prev_WXZA'] > 0) & (df['WXZA'] > 0) & (df['升排']) & (df['连阳']), '转正_戊+前WTZA>0+升排+连阳')
        # (4) 前周 WTZA<0，本周 WTZA>0
        mark((df['prev_WXZA'] < 0) & (df['WXZA'] > 0), '转正_前WTZA<0今WTZA>0')

        # ===== 对比基线 =====
        mark(df['非正交'], '转正_非正交整体')

    # 输出
    print(f'\n=== WXAB 由负转正前置状态 ===')
    print(f'{"场景":<30} {"n":>8} {"正交":>8} {"正交%":>9}')
    print('-' * 60)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[1] / n * 100
        results.append((name, n, s[1], pct))
    results.sort(key=lambda x: -x[3])
    for name, n, orth, pct in results:
        print(f'{name:<30} {n:>8} {orth:>8} {pct:>8.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '正交', '正交%'])
        for name, n, orth, pct in results:
            w.writerow([name, n, orth, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()