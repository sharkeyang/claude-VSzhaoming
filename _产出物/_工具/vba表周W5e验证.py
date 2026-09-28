#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周类 W5e（戊护型）转己/甲概率 + WXAB<0 转正交概率验证

验证用户问题：
1. 周类戊护型（y开头），首上破WJA（WXZA=1），且为连阳，转己/甲概率
2. WXAB<0 转 WXAB>0 概率（整体）
3. 三种情况：
   (1) 前一周柱 WTAB=1（AB周[20]=1）
   (2) WXAB<0 但 WXZB>0 且 WXZA≥2 在 WJA 之上存在升排
   (3) WXAB<0 但 WXZA>0

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表周W5e验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/周W5e验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：场景 -> [n, 转己, 转甲, 转己甲, 转其他]
    stat = defaultdict(lambda: [0, 0, 0, 0, 0])

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
        df['柱排str'] = df['柱排周'].astype(str)
        df['连阳'] = df['柱排str'].str.startswith('升') & df['柱排str'].str.contains('连')
        df['升排'] = df['柱排str'].str.startswith('升')
        # 下一周护型
        df['next_hx'] = df['hx'].shift(-1)

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_ji = int((next_hx == '己').sum())
            to_jia = int((next_hx == '甲').sum())
            to_other = int((~next_hx.isin(['己', '甲']) & (next_hx != '')).sum())
            s = stat[name]
            s[0] += n
            s[1] += to_ji
            s[2] += to_jia
            s[3] += (to_ji + to_jia)
            s[4] += to_other

        # ===== 1. 戊护型 + WXZA=1 + 连阳 → 转己/甲 =====
        mark((df['hx'] == '戊') & (df['WXZA'] == 1) & (df['连阳']), '戊+WXZA=1+连阳')
        # 对比：戊护型 + WXZA=1（不管连阳）
        mark((df['hx'] == '戊') & (df['WXZA'] == 1), '戊+WXZA=1')
        # 对比：戊护型整体
        mark(df['hx'] == '戊', '戊护型整体')

        # ===== 2. WXAB<0 转 WXAB>0 =====
        # WXAB<0 = AB周<0
        mark(df['AB周'] < 0, 'WXAB<0整体')
        # 对比：WXAB>0
        mark(df['AB周'] > 0, 'WXAB>0整体')

        # ===== 3. 三种情况 =====
        # (1) 前一周柱 WTAB=1（AB周=1）
        mark(df['AB周'] == 1, '情况1_AB周=1')
        # (2) WXAB<0 但 WXZB>0 且 WXZA≥2 在 WJA 之上存在升排
        mark((df['AB周'] < 0) & (df['WXZB'] > 0) & (df['WXZA'] >= 2) & (df['升排']), '情况2_WXAB<0+WXZB>0+WXZA≥2+升排')
        # (3) WXAB<0 但 WXZA>0
        mark((df['AB周'] < 0) & (df['WXZA'] > 0), '情况3_WXAB<0+WXZA>0')

    # 输出
    print(f'\n{"场景":<32} {"n":>8} {"转己":>6} {"转甲":>6} {"转己甲":>7} {"转己甲%":>8} {"转其他":>7}')
    print('-' * 85)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = s[3] / n * 100
        results.append((name, n, s[1], s[2], s[3], pct, s[4]))
    # 按转己甲%降序
    results.sort(key=lambda x: -x[5])
    for name, n, ji, jia, jijia, pct, other in results:
        print(f'{name:<32} {n:>8} {ji:>6} {jia:>6} {jijia:>7} {pct:>7.2f}% {other:>7}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '转己', '转甲', '转己甲', '转己甲%', '转其他'])
        for name, n, ji, jia, jijia, pct, other in results:
            w.writerow([name, n, ji, jia, jijia, f'{pct:.2f}', other])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()