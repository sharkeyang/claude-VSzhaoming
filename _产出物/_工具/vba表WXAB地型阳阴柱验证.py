#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研究：WXAB>0（主升）区域内，按地型划分，阳柱/阴柱后的表现

用户问题（2026-09-30）：WXAB 之前结论阳柱后表现优于阴柱后，是否按地型划分能得到更好的预测效果？

地型定义（MC3.1_C7 §2.2.1）：基于 WTZA 正负二元 + 前四柱具并符串（Q/O/V/W）分类
8类：0橅/1柜/2栅/3桮（WTZA>0）+ 6娝/7姗/8姖/9妩（WTZA<0）
地型 = 波型列（[5]）前2字符

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [2] PR（临涨幅=下周涨幅）  [5] 波型（地型）  [20] AB周

验证：WXAB>0 区域内，按地型划分，阳柱后/阴柱后的下周收益（PR）

用法：
    python _产出物/_工具/vba表WXAB地型阳阴柱验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB地型阳阴柱验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：地型 -> [n, 阳柱后PR和, 阳柱数, 阴柱后PR和, 阴柱数, 阳柱后HR>3数, 阴柱后HR>3数]
    stat = defaultdict(lambda: [0, 0.0, 0, 0.0, 0, 0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 2, 3, 5, 20])
            df.columns = ['周涨', 'PR', 'HR', '波型', 'AB周']
        except Exception:
            continue
        for c in ['周涨', 'PR', 'HR', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'PR', 'HR', 'AB周'])
        if df.empty:
            continue

        # 地型 = 波型前2字符
        df['地型'] = df['波型'].astype(str).str[:2]
        # WXAB>0 区域
        sub = df[df['AB周'] > 0]
        if sub.empty:
            continue

        for d, g in sub.groupby('地型'):
            s = stat[d]
            s[0] += len(g)
            # 阳柱后 PR
            yang = g[g['周涨'] > 0]
            s[1] += float(yang['PR'].sum())
            s[2] += len(yang)
            s[5] += int((yang['HR'] > 3).sum())
            # 阴柱后 PR
            yin = g[g['周涨'] < 0]
            s[3] += float(yin['PR'].sum())
            s[4] += len(yin)
            s[6] += int((yin['HR'] > 3).sum())

    # 输出
    print(f'\n=== WXAB>0 区域内，按地型划分，阳柱/阴柱后表现 ===')
    print(f'{"地型":<6} {"n":>8} {"阳柱后PR":>9} {"阳柱HR>3%":>9} {"阴柱后PR":>9} {"阴柱HR>3%":>9} {"阳-阴差":>8}')
    print('-' * 70)
    results = []
    for d, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        yang_pr = s[1] / s[2] if s[2] else 0
        yin_pr = s[3] / s[4] if s[4] else 0
        yang_hr3 = s[5] / s[2] * 100 if s[2] else 0
        yin_hr3 = s[6] / s[4] * 100 if s[4] else 0
        diff = yang_pr - yin_pr
        results.append((d, n, yang_pr, yang_hr3, yin_pr, yin_hr3, diff))
    results.sort(key=lambda x: -x[6])
    for d, n, yang_pr, yang_hr3, yin_pr, yin_hr3, diff in results:
        print(f'{d:<6} {n:>8} {yang_pr:>9.3f}% {yang_hr3:>8.1f}% {yin_pr:>9.3f}% {yin_hr3:>8.1f}% {diff:>8.3f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['地型', 'n', '阳柱后PR%', '阳柱HR>3%%', '阴柱后PR%', '阴柱HR>3%%', '阳-阴差%'])
        for d, n, yang_pr, yang_hr3, yin_pr, yin_hr3, diff in results:
            w.writerow([d, n, f'{yang_pr:.3f}', f'{yang_hr3:.1f}', f'{yin_pr:.3f}', f'{yin_hr3:.1f}', f'{diff:.3f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()