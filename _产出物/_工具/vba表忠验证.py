#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DXCD=忠 获利性验证 — 是否危险的诱多

验证用户问题：DXCD=忠 不是好机会，很危险的诱多，要特别谨慎。

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD   [9] 护型   [13] 日ZA   [14] 日ZC   [15] 日ZE   [26] 次日高幅

用法：
    python _产出物/_工具/vba表忠验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/忠验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0, 0.0])  # [n, hit3, 次日高幅和]

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[5, 8, 9, 13, 14, 15, 26])
            df.columns = ['涨幅', 'DXCD', '护型', '日ZA', '日ZC', '日ZE', '次日高幅']
        except Exception:
            continue
        for c in ['涨幅', '日ZA', '日ZC', '日ZE', '次日高幅']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['次日高幅'])
        if df.empty:
            continue

        df['hx'] = df['护型'].astype(str).str[0].map(HX_MAP)
        df['hit3'] = (df['次日高幅'] >= 3).astype(int)

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += int(sub['hit3'].sum())
            s[2] += float(sub['次日高幅'].sum())

        # ===== 1. DXCD 各状态整体获利性 =====
        for cd in ['上', '忐', '忠', '中', '下', '忑']:
            mark(df['DXCD'] == cd, f'DXCD={cd}整体')

        # ===== 2. 忠 中 DXZC>0 vs DXZC<0 =====
        mark((df['DXCD'] == '忠') & (df['日ZC'] > 0), '忠_DXZC>0')
        mark((df['DXCD'] == '忠') & (df['日ZC'] <= 0), '忠_DXZC<=0')
        # 对比：上/忐 中 DXZC>0
        mark((df['DXCD'].isin(['上', '忐'])) & (df['日ZC'] > 0), '上忐_DXZC>0')

        # ===== 3. 忠 中升连（柱排）的获利性 =====
        # 忠 中升连（用涨幅>0近似，或需柱排列）
        # 这里用涨幅>0 且 前一日涨幅>0 近似连阳
        df['prev_涨幅'] = df['涨幅'].shift(1)
        mark((df['DXCD'] == '忠') & (df['涨幅'] > 0) & (df['prev_涨幅'] > 0), '忠_连阳')

        # ===== 4. 忠 中甲乙己护型的获利性 =====
        mark((df['DXCD'] == '忠') & (df['hx'].isin(['甲', '乙', '己'])), '忠_甲乙己')

        # ===== 5. 忠 介入后是否容易亏损（次日高幅<0 比例）=====
        # 用次日高幅<0 近似"介入后亏损"
        df['hit_neg'] = (df['次日高幅'] < 0).astype(int)
        for cd in ['上', '忐', '忠']:
            sub = df[df['DXCD'] == cd]
            if sub.empty:
                continue
            s = stat[f'DXCD={cd}次日跌']
            s[0] += len(sub)
            s[1] += int(sub['hit_neg'].sum())

    # 输出
    print(f'\n{"场景":<20} {"n":>8} {"P(≥3%)":>8} {"均高幅":>7}')
    print('-' * 50)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        p3 = s[1] / n * 100
        avg = s[2] / n
        results.append((name, n, p3, avg))
    # 按 P(≥3%) 降序
    results.sort(key=lambda x: -x[2])
    for name, n, p3, avg in results:
        print(f'{name:<20} {n:>8} {p3:>7.2f}% {avg:>6.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', 'P(≥3%)', '均高幅'])
        for name, n, p3, avg in results:
            w.writerow([name, n, f'{p3:.2f}', f'{avg:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()