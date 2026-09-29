#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研究 WXZB>0 且 WXAB<=0 的集合特征

用户问题（2026-09-29）：
1. 当 WXAB<0 但 WXZB>0 时，是否很多不会转变为 WXAB>0，且会产生较大阴柱？
2. WXAB>0 是否更稳定（WJA/WJB 比 WJZ 稳定，维持更长时间）？

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR  [15] WXZB  [20] AB周

验证：
1. WXZB>0 且 WXAB<=0 时，后续 N 周内转变为 WXAB>0 的比例
2. WXZB>0 且 WXAB<=0 时，产生较大阴柱（周涨<-3%）的比例
3. 对比 WXZB>0 且 WXAB>0

用法：
    python _产出物/_工具/vba表WXZB_WXAB差集研究.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXZB_WXAB差集研究结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：集合 -> [n, 1周转正, 3周转正, 5周转正, 10周转正, 大阴柱数, 周涨和, 正周涨数]
    stat = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0.0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 3, 15, 20])
            df.columns = ['周涨', 'HR', 'WXZB', 'AB周']
        except Exception:
            continue
        for c in ['周涨', 'HR', 'WXZB', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'HR', 'WXZB', 'AB周'])
        if df.empty:
            continue

        ab = df['AB周'].values
        zb = df['WXZB'].values
        zhou = df['周涨'].values
        n = len(df)

        def mark(cond, name):
            idxs = np.where(cond)[0]
            if len(idxs) == 0:
                return
            s = stat[name]
            s[0] += len(idxs)
            # 后续 N 周内转正（WXAB>0）
            for idx in idxs:
                # 1周内转正
                if idx + 1 < n and ab[idx + 1] > 0:
                    s[1] += 1
                # 3周内转正
                if any(ab[idx + k] > 0 for k in range(1, min(4, n - idx))):
                    s[2] += 1
                # 5周内转正
                if any(ab[idx + k] > 0 for k in range(1, min(6, n - idx))):
                    s[3] += 1
                # 10周内转正
                if any(ab[idx + k] > 0 for k in range(1, min(11, n - idx))):
                    s[4] += 1
                # 本周大阴柱（周涨<-3%）
                if zhou[idx] < -3:
                    s[5] += 1
                s[6] += zhou[idx]
                if zhou[idx] > 0:
                    s[7] += 1

        # WXZB>0 且 WXAB<=0
        mark((zb > 0) & (ab <= 0), 'WXZB>0+WXAB<=0')
        # WXZB>0 且 WXAB>0
        mark((zb > 0) & (ab > 0), 'WXZB>0+WXAB>0')
        # WXZB>0 单独
        mark(zb > 0, 'WXZB>0')

    # 输出
    print(f'\n=== WXZB>0 且 WXAB<=0 集合特征研究 ===')
    print(f'{"集合":<20} {"n":>8} {"1周转正":>7} {"3周转正":>7} {"5周转正":>7} {"10周转正":>8} {"大阴柱%":>7} {"平均周涨":>8} {"正周涨%":>7}')
    print('-' * 90)
    for name in ['WXZB>0+WXAB<=0', 'WXZB>0+WXAB>0', 'WXZB>0']:
        s = stat[name]
        if s[0] == 0:
            continue
        n = s[0]
        print(f'{name:<20} {n:>8} {s[1]/n*100:>6.1f}% {s[2]/n*100:>6.1f}% {s[3]/n*100:>6.1f}% {s[4]/n*100:>7.1f}% {s[5]/n*100:>6.1f}% {s[6]/n:>8.3f}% {s[7]/n*100:>6.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['集合', 'n', '1周转正%', '3周转正%', '5周转正%', '10周转正%', '大阴柱%', '平均周涨%', '正周涨%'])
        for name in ['WXZB>0+WXAB<=0', 'WXZB>0+WXAB>0', 'WXZB>0']:
            s = stat[name]
            if s[0] == 0:
                continue
            n = s[0]
            w.writerow([name, n, f'{s[1]/n*100:.1f}', f'{s[2]/n*100:.1f}', f'{s[3]/n*100:.1f}', f'{s[4]/n*100:.1f}', f'{s[5]/n*100:.1f}', f'{s[6]/n:.3f}', f'{s[7]/n*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()