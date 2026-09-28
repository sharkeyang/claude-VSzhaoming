#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.3.5 全文审核修复 — 数据重跑验证

重跑多个被质疑的数据点：
1. 等1连阳 vs 单阳 次日P≥3%（§4.1.1 vs §4.7.3 矛盾）
2. 等7/等6 BSHA<3 次日P≥3%（§4.5.1/§4.6.1 表格 vs 结论）
3. 等5整体值（§4.4.2）
4. 主战场含忐 vs 忐应剔除（§6.1.2 vs §6.1.5.5.3）

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD   [9] 护型   [10] 柱排   [13] 日ZA   [14] 日ZC   [15] 日ZE
    [19] BSHA   [21] 管宽哼JA   [26] 次日高幅   [27] 柱型   [30] 上符串   [44] 日等型

用法：
    python _产出物/_工具/vba表审核重跑.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/审核重跑结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计
    stat = defaultdict(lambda: [0, 0])  # [n, hit]

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0],
                             usecols=[5, 8, 9, 10, 13, 14, 15, 19, 21, 26, 27, 30, 44])
            df.columns = ['涨幅', 'DXCD', '护型', '柱排', '日ZA', '日ZC', '日ZE', 'BSHA', '管宽', '次日高幅', '柱型', '上符串', '日等型']
        except Exception:
            continue
        for c in ['涨幅', '日ZA', '日ZC', '日ZE', 'BSHA', '管宽', '次日高幅']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['日ZA', '次日高幅'])
        if df.empty:
            continue

        df['护型码'] = df['护型'].astype(str).str[0]
        df['hx'] = df['护型码'].map(HX_MAP)
        df['等型'] = df['日等型'].astype(str).str[1]
        df['hit3'] = (df['次日高幅'] >= 3).astype(int)

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            stat[name][0] += len(sub)
            stat[name][1] += int(sub['hit3'].sum())

        # ===== 1. 等1连阳 vs 单阳（柱型列[27]）=====
        # 连阳 = 柱型含"连"，单阳 = 柱型含"单"且非阴
        df['柱型str'] = df['柱型'].astype(str)
        df['连阳'] = df['柱型str'].str.contains('连')
        df['单阳'] = df['柱型str'].str.contains('单') & ~df['柱型str'].str.contains('阴')
        for hx in ['甲', '乙', '己']:
            mark((df['等型'] == '1') & (df['hx'] == hx) & (df['连阳']), f'等1_{hx}_连阳')
            mark((df['等型'] == '1') & (df['hx'] == hx) & (df['单阳']), f'等1_{hx}_单阳')

        # ===== 2. 等7/等6 BSHA<3 =====
        mark((df['等型'] == '7') & (df['BSHA'] < 3), '等7_BSHA<3')
        mark((df['等型'] == '6') & (df['BSHA'] < 3), '等6_BSHA<3')

        # ===== 3. 等5整体 =====
        mark(df['等型'] == '5', '等5_整体')
        mark(df['等型'] == '6', '等6_整体')
        mark(df['等型'] == '7', '等7_整体')

        # ===== 4. 主战场：DXZE>0 + CD上/忐 =====
        mark((df['日ZE'] > 0) & (df['DXCD'] == '上'), '主战场_CD上')
        mark((df['日ZE'] > 0) & (df['DXCD'] == '忐'), '主战场_CD忐')
        mark((df['日ZE'] > 0) & (df['DXCD'].isin(['上', '忐'])), '主战场_CD上忐')

    # 输出
    print(f'\n{"数据点":<24} {"n":>10} {"P(≥3%)":>8}')
    print('-' * 48)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        results.append((name, s[0], s[1] / s[0] * 100))
    results.sort(key=lambda x: x[0])
    for name, n, p in results:
        print(f'{name:<24} {n:>10} {p:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['数据点', 'n', 'P(≥3%)'])
        for name, n, p in results:
            w.writerow([name, n, f'{p:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
