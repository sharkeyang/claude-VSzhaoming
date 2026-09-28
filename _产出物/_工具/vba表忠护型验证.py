#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
忠 中 WXAB 护型分布与获利性验证

验证用户问题：DXCD忠的问题，是过分考虑了DXZC的因素，而没有充分考虑DXCD（WXAB）因素。
WXAB是股票真实运行的结构单元。

验证：忠 中 WXAB 护型的分布，以及不同护型在忠 中的获利性。

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [8] DXCD   [9] 护型   [13] 日ZA   [14] 日ZC   [26] 次日高幅

用法：
    python _产出物/_工具/vba表忠护型验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/忠护型验证结果.csv'

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
                             header=None, skiprows=[0], usecols=[8, 9, 13, 14, 26])
            df.columns = ['DXCD', '护型', '日ZA', '日ZC', '次日高幅']
        except Exception:
            continue
        for c in ['日ZA', '日ZC', '次日高幅']:
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

        # ===== 忠 中 WXAB 护型分布与获利性 =====
        for hx in ['甲', '乙', '丙', '丁', '戊', '己']:
            mark((df['DXCD'] == '忠') & (df['hx'] == hx), f'忠_{hx}')
        # 忠 中甲乙己 vs 丙丁戊
        mark((df['DXCD'] == '忠') & (df['hx'].isin(['甲', '乙', '己'])), '忠_甲乙己')
        mark((df['DXCD'] == '忠') & (df['hx'].isin(['丙', '丁', '戊'])), '忠_丙丁戊')

        # ===== 对比：上/忐 中 WXAB 护型 =====
        for hx in ['甲', '乙', '己']:
            mark((df['DXCD'].isin(['上', '忐'])) & (df['hx'] == hx), f'上忐_{hx}')

        # ===== 忠 中护型 × 日ZA =====
        # 忠 中甲乙己 + 日ZA>0
        mark((df['DXCD'] == '忠') & (df['hx'].isin(['甲', '乙', '己'])) & (df['日ZA'] > 0), '忠_甲乙己+ZA>0')
        # 忠 中丙丁戊 + 日ZA<0
        mark((df['DXCD'] == '忠') & (df['hx'].isin(['丙', '丁', '戊'])) & (df['日ZA'] < 0), '忠_丙丁戊+ZA<0')

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