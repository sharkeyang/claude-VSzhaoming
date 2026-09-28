#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周类操作原则验证 — 三个原则是否有道理

原则1：WXAB由负转正要严格谨慎，由正转负要宽容慢半拍
原则2：宁要WXAB>0时破线，也不要WXAB<0时突破
原则3：WXAB>0时，WXZA>0好；WXZA<0要在DXZC<0退出但准备上破介入；WXZB<0谨慎

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [13] WXCD大局   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表周原则验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/周原则验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])  # [n, 转己甲]

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 6, 13, 14, 15, 16, 20])
            df.columns = ['WXAB护型', '柱排周', 'WXCD大局', 'WXZA', 'WXZB', 'WXZC', 'AB周']
        except Exception:
            continue
        for c in ['WXZA', 'WXZB', 'WXZC', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['WXZA'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        df['next_hx'] = df['hx'].shift(-1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['升排'] = df['柱排str'].str.startswith('升')
        # 正交护型（甲乙己）与非正交护型（戊/丙/丁）
        df['正交'] = df['hx'].isin(['甲', '乙', '己'])
        df['非正交'] = df['hx'].isin(['戊', '丙', '丁'])

        def mark(cond, name, target='转正交'):
            """target='转正交'：非正交→下一周正交；target='维持正交'：正交→下一周仍正交"""
            if target == '转正交':
                sub = df[cond & df['非正交']]
                hit = sub['next_hx'].isin(['己', '甲'])
            else:
                sub = df[cond & df['正交']]
                hit = sub['next_hx'].isin(['甲', '乙', '己'])
            if sub.empty:
                return
            n = len(sub)
            s = stat[name]
            s[0] += n
            s[1] += int(hit.sum())

        # ===== 原则1：WXAB由负转正 vs 由正转负 =====
        # 由负转正（严格谨慎的依据）：非正交护型 AB周<0 转正交概率
        mark(df['AB周'] < 0, '原则1_WXAB<0转正交', '转正交')
        # 由正转负（宽容慢半拍的依据）：正交护型 AB周>0 维持正交概率
        mark(df['AB周'] > 0, '原则1_WXAB>0维持', '维持正交')

        # ===== 原则2：宁要WXAB>0破线，不要WXAB<0突破 =====
        # WXAB>0 破线（正交护型跌破WJA，WXZA<0）：维持正交概率
        mark((df['AB周'] > 0) & (df['WXZA'] < 0), '原则2_WXAB>0+WXZA<0(破线)', '维持正交')
        # WXAB<0 突破（非正交护型上破WJA，WXZA>0）：转正交概率
        mark((df['AB周'] < 0) & (df['WXZA'] > 0), '原则2_WXAB<0+WXZA>0(突破)', '转正交')

        # ===== 原则3：WXAB>0 时 WXZA/WXZB 的影响（正交护型维持正交）=====
        mark((df['AB周'] > 0) & (df['WXZA'] > 0), '原则3_WXAB>0+WXZA>0', '维持正交')
        mark((df['AB周'] > 0) & (df['WXZA'] < 0), '原则3_WXAB>0+WXZA<0', '维持正交')
        mark((df['AB周'] > 0) & (df['WXZB'] < 0), '原则3_WXAB>0+WXZB<0', '维持正交')
        mark((df['AB周'] > 0) & (df['WXZB'] > 0), '原则3_WXAB>0+WXZB>0', '维持正交')

    # 输出
    print(f'\n{"场景":<32} {"n":>8} {"转己甲":>7} {"转己甲%":>8}')
    print('-' * 60)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[1] / n * 100
        results.append((name, n, s[1], pct))
    results.sort(key=lambda x: -x[3])
    for name, n, jijia, pct in results:
        print(f'{name:<32} {n:>8} {jijia:>7} {pct:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '转己甲', '转己甲%'])
        for name, n, jijia, pct in results:
            w.writerow([name, n, jijia, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()