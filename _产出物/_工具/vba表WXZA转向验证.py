#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WXZA转向 vs WXAB转向 预测力验证

验证用户问题："不能用WXZA转向来预测WXAB转向"对不对？

区分两种"WXZA转向"：
A. WXZA符号变化（从负转正/从正转负）——是否预测WXAB转向
B. WXZA大小（越大越弱）——是否预测WXAB转向

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [14] WXZA   [20] AB周

用法：
    python _产出物/_工具/vba表WXZA转向验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXZA转向验证结果.csv'

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
                             header=None, skiprows=[0], usecols=[4, 14, 20])
            df.columns = ['WXAB护型', 'WXZA', 'AB周']
        except Exception:
            continue
        for c in ['WXZA', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['WXZA'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        df['next_hx'] = df['hx'].shift(-1)
        df['prev_WXZA'] = df['WXZA'].shift(1)
        df['next_AB'] = df['AB周'].shift(-1)
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

        # ===== A. WXZA 符号变化对 WXAB 转向的预测 =====
        # WXZA 从负转正（prev<0, 今>0）
        mark((df['prev_WXZA'] < 0) & (df['WXZA'] > 0), 'A_WXZA负转正')
        # WXZA 从正转负（prev>0, 今<0）
        mark((df['prev_WXZA'] > 0) & (df['WXZA'] < 0), 'A_WXZA正转负')
        # WXZA 持续正（prev>0, 今>0）
        mark((df['prev_WXZA'] > 0) & (df['WXZA'] > 0), 'A_WXZA持续正')
        # WXZA 持续负（prev<0, 今<0）
        mark((df['prev_WXZA'] < 0) & (df['WXZA'] < 0), 'A_WXZA持续负')

        # ===== B. WXZA 大小对 WXAB 转向的预测（WXZA>0 时）=====
        for za in [1, 2, 3, 4, 5]:
            mark((df['WXZA'] == za), f'B_WXZA={za}')

    # 输出
    print(f'\n{"场景":<20} {"n":>8} {"转正交":>7} {"转正交%":>8}')
    print('-' * 50)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[1] / n * 100
        results.append((name, n, s[1], pct))
    results.sort(key=lambda x: -x[3])
    for name, n, orth, pct in results:
        print(f'{name:<20} {n:>8} {orth:>7} {pct:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '转正交', '转正交%'])
        for name, n, orth, pct in results:
            w.writerow([name, n, orth, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()