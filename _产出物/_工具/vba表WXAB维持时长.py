#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周类 WXAB 转为正交后的维持时长验证

参考日类 DXAB 分析（§2.1 DXAB正交后转负概率）：
- WXAB>0 后 N 周内转负（AB周<0）的概率，按护型分组
- 平均转负周数
- 是否频繁相交（WXAB 交叉次数分布）

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [20] AB周

用法：
    python _产出物/_工具/vba表WXAB维持时长.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB维持时长结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：护型 -> [n, 1周转负, 3周转负, 5周转负, 10周转负, 转负周数和, 5周内反向相交, 转负样本数]
    stat = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0, 0])
    # 交叉次数分布
    cross_count = defaultdict(int)

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 20])
            df.columns = ['WXAB护型', 'AB周']
        except Exception:
            continue
        df['AB周'] = pd.to_numeric(df['AB周'], errors='coerce')
        df = df.dropna(subset=['AB周'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        ab = df['AB周'].values
        hx = df['hx'].values
        n = len(df)

        # ===== WXAB>0 后 N 周内转负概率 =====
        # 对每个 WXAB>0 的起点，看后续 N 周内是否转负（AB周<0）
        for idx in range(n):
            if ab[idx] > 0 and hx[idx] in ('甲', '乙', '丙'):
                h = hx[idx]
                s = stat[h]
                s[0] += 1
                # 1周内转负
                if idx + 1 < n and ab[idx + 1] < 0:
                    s[1] += 1
                # 3周内转负
                if any(ab[idx + k] < 0 for k in range(1, min(4, n - idx))):
                    s[2] += 1
                # 5周内转负（频繁相交定义：正交后5周期内反向相交）
                if any(ab[idx + k] < 0 for k in range(1, min(6, n - idx))):
                    s[3] += 1
                    s[6] += 1
                # 10周内转负
                if any(ab[idx + k] < 0 for k in range(1, min(11, n - idx))):
                    s[4] += 1
                # 转负周数（到第一次转负，不限10周，统计所有转负样本）
                for k in range(1, n - idx):
                    if ab[idx + k] < 0:
                        s[5] += k
                        s[7] += 1  # 转负样本数
                        break
                # 如果到末尾都没转负，不计入平均（该样本未转负）

        # ===== WXAB 交叉次数分布 =====
        # 统计每只股票 WXAB 正负符号变化次数
        sign = (ab > 0).astype(int)
        changes = np.sum(sign[1:] != sign[:-1])
        cross_count[changes] += 1

    # 输出
    print(f'\n=== WXAB>0 后 N 周内转负概率（按护型）===')
    print(f'{"护型":<8} {"n":>8} {"1周":>6} {"3周":>6} {"5周":>6} {"10周":>6} {"平均转负周数":>10} {"5周内反向相交%":>12}')
    print('-' * 75)
    for h in ['甲', '乙', '丙']:
        s = stat[h]
        if s[0] == 0:
            continue
        n = s[0]
        # 平均转负周数 = 转负周数和 / 转负样本数（s[7]，只统计转负的）
        n_turn = s[7]
        avg = s[5] / n_turn if n_turn else 0
        freq = s[6] / n * 100
        print(f'{h:<8} {n:>8} {s[1]/n*100:>5.1f}% {s[2]/n*100:>5.1f}% {s[3]/n*100:>5.1f}% {s[4]/n*100:>5.1f}% {avg:>10.2f}周 {freq:>12.1f}%')

    print(f'\n=== WXAB 交叉次数分布（每只股票）===')
    total = sum(cross_count.values())
    for c in sorted(cross_count.keys()):
        print(f'  {c}次: {cross_count[c]} ({cross_count[c]/total*100:.1f}%)')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['护型', 'n', '1周转负%', '3周转负%', '5周转负%', '10周转负%', '平均转负周数'])
        for h in ['甲', '乙', '丙']:
            s = stat[h]
            if s[0] == 0:
                continue
            n = s[0]
            avg = s[5] / s[0] if s[0] else 0
            w.writerow([h, n, f'{s[1]/n*100:.1f}', f'{s[2]/n*100:.1f}', f'{s[3]/n*100:.1f}', f'{s[4]/n*100:.1f}', f'{avg:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()