#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
跌破 DJB 低吸安全性验证

验证用户问题："跌破 DJB 时仍然要买入吗？"
区分两种"跌破 DJB"：
A. 跌破 DJB 但 DXCD=上（主升区域内浅回调）——低吸是否安全
B. 跌破 DJB 且 DXAB<0（护型变丙丁戊）——真正转负，应谨慎

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [8] DXCD   [9] 护型   [13] 日ZA   [14] 日ZC   [26] 次日高幅   [62] DTZB(JZ vs JB)

用法：
    python _产出物/_工具/vba表跌破DJB验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/跌破DJB验证结果.csv'

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
                             header=None, skiprows=[0], usecols=[8, 9, 13, 14, 26, 62])
            df.columns = ['DXCD', '护型', '日ZA', '日ZC', '次日高幅', 'DTZB']
        except Exception:
            continue
        for c in ['日ZA', '日ZC', '次日高幅', 'DTZB']:
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

        # ===== 1. 跌破 DJB（DTZB<0）时，DXCD 分布 =====
        # 跌破 DJB = DTZB<0
        for cd in ['上', '忐', '忠', '中', '下', '忑']:
            mark((df['DTZB'] < 0) & (df['DXCD'] == cd), f'跌破DJB_DXCD={cd}')

        # ===== 2. 跌破 DJB 时，护型分布 =====
        mark((df['DTZB'] < 0) & (df['hx'].isin(['甲', '乙', '己'])), '跌破DJB_甲乙己')
        mark((df['DTZB'] < 0) & (df['hx'].isin(['丙', '丁', '戊'])), '跌破DJB_丙丁戊')

        # ===== 3. 跌破 DJB 但 DXCD=上（主升浅回调）的获利性 =====
        mark((df['DTZB'] < 0) & (df['DXCD'] == '上'), '跌破DJB+CD上')
        # 对比：跌破 DJB 且 DXCD 变坏（中/下/忑）
        mark((df['DTZB'] < 0) & (df['DXCD'].isin(['中', '下', '忑'])), '跌破DJB+CD中下忑')

        # ===== 4. 跌破 DJB 且 DXAB<0（护型丙丁戊）的获利性 =====
        mark((df['DTZB'] < 0) & (df['hx'].isin(['丙', '丁', '戊'])), '跌破DJB+丙丁戊')

        # ===== 5. 跌破 DJB 但 DXAB>0（护型甲乙己）的获利性 =====
        mark((df['DTZB'] < 0) & (df['hx'].isin(['甲', '乙', '己'])), '跌破DJB+甲乙己')

    # 输出
    print(f'\n{"场景":<24} {"n":>8} {"P(≥3%)":>8} {"均高幅":>7}')
    print('-' * 55)
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
        print(f'{name:<24} {n:>8} {p3:>7.2f}% {avg:>6.2f}%')

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