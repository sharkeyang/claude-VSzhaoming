#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
W5e（戊护型）WXZA>0 越大势头越弱验证

验证用户猜想：戊护型（y开头），WTZA>0（WXZA>0，在WJA之上），
在WJA之上越大（WXZA越大），势头越弱，越不会转为WXAB正交。

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [6] 柱排周   [14] WXZA   [15] WXZB   [16] WXZC   [20] AB周

用法：
    python _产出物/_工具/vba表W5e势头验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/W5e势头验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0, 0])  # [n, 转己, 转甲]

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
        df['next_hx'] = df['hx'].shift(-1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['连阳'] = df['柱排str'].str.startswith('升') & df['柱排str'].str.contains('连')

        # 戊护型 + WXZA>0，按 WXZA 分组
        wu = df[df['hx'] == '戊']
        for za in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            sub = wu[wu['WXZA'] == za]
            if sub.empty:
                continue
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_ji = int((next_hx == '己').sum())
            to_jia = int((next_hx == '甲').sum())
            s = stat[f'WXZA={za}']
            s[0] += n
            s[1] += to_ji
            s[2] += to_jia
        # WXZA>10 合并
        sub = wu[wu['WXZA'] > 10]
        if not sub.empty:
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_ji = int((next_hx == '己').sum())
            to_jia = int((next_hx == '甲').sum())
            s = stat['WXZA>10']
            s[0] += n
            s[1] += to_ji
            s[2] += to_jia

        # 对比：戊护型 + WXZA<=0
        sub = wu[wu['WXZA'] <= 0]
        if not sub.empty:
            n = len(sub)
            next_hx = sub['next_hx'].fillna('')
            to_ji = int((next_hx == '己').sum())
            to_jia = int((next_hx == '甲').sum())
            s = stat['WXZA<=0']
            s[0] += n
            s[1] += to_ji
            s[2] += to_jia

    # 输出
    print(f'\n{"场景":<12} {"n":>8} {"转己":>6} {"转甲":>6} {"转己甲":>7} {"转己甲%":>8}')
    print('-' * 55)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        pct = (s[1] + s[2]) / n * 100
        results.append((name, n, s[1], s[2], s[1] + s[2], pct))
    # 按 WXZA 排序（1,2,3...）
    def sort_key(x):
        name = x[0]
        if name == 'WXZA<=0':
            return 0
        if name == 'WXZA>10':
            return 99
        return int(name.split('=')[1])
    results.sort(key=sort_key)
    for name, n, ji, jia, jijia, pct in results:
        print(f'{name:<12} {n:>8} {ji:>6} {jia:>6} {jijia:>7} {pct:>7.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '转己', '转甲', '转己甲', '转己甲%'])
        for name, n, ji, jia, jijia, pct in results:
            w.writerow([name, n, ji, jia, jijia, f'{pct:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()