#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
所有 WXAB 护型的持续时长（周类）

与日类 §8.1.3.5.1 对应：统计每个 WXAB 护型（甲/乙/丙/丁/戊/己）的持续时长。
乙/戊 拆分 ZA>0/ZA<0（护型字符串中 J=ZA>0，K=ZA<0）。

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型   [20] AB周

护型字符串结构：首字母(护型) + 方向(J=ZA>0/K=ZA<0) + 护级 + 持续数字
    a甲→J中1.I   = 甲，ZA>0，护级中，持续1
    z丁→K中-1.Y  = 丁，ZA<0，护级中，持续-1

用法：
    python _产出物/_工具/vba表WXAB护型持续时长.py
"""
import csv, os, io, re
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB护型持续时长结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def parse_hx(s):
    """解析护型字符串，返回护型字母或 None"""
    if not isinstance(s, str) or len(s) < 1:
        return None
    return HX_MAP.get(s[0])


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：护型 -> [段数, 持续周数和, 最长, 持续周数列表]
    stat = defaultdict(lambda: [0, 0, 0, []])
    # 每只股票的护型段
    all_segments = defaultdict(list)  # 护型 -> [持续周数...]

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 14])
            df.columns = ['WXAB护型', 'WXZA']
        except Exception:
            continue
        if df.empty:
            continue

        # 解析护型，识别连续段（乙/戊拆分 ZA>0/ZA<0，用列[14] WXZA 判断）
        hx_list = []
        for s, za in zip(df['WXAB护型'].astype(str), df['WXZA'].astype(float)):
            hx = parse_hx(s)
            if hx is None:
                hx_list.append(None)
                continue
            # 乙/戊 拆分 ZA>0/ZA<0；甲/丙/丁/己 不拆分
            if hx in ('乙', '戊'):
                za_dir = '>0' if za > 0 else '<0'
                hx_list.append(f'{hx}(ZA{za_dir})')
            else:
                hx_list.append(hx)

        # 识别连续段
        prev = None
        run_len = 0
        for h in hx_list:
            if h is None:
                continue
            if h == prev:
                run_len += 1
            else:
                if prev is not None and run_len > 0:
                    stat[prev][0] += 1
                    stat[prev][1] += run_len
                    stat[prev][2] = max(stat[prev][2], run_len)
                    stat[prev][3].append(run_len)
                    all_segments[prev].append(run_len)
                prev = h
                run_len = 1
        # 处理末尾段
        if prev is not None and run_len > 0:
            stat[prev][0] += 1
            stat[prev][1] += run_len
            stat[prev][2] = max(stat[prev][2], run_len)
            stat[prev][3].append(run_len)
            all_segments[prev].append(run_len)

    # 输出
    print(f'\n=== 所有 WXAB 护型持续时长（周类，高波池）===')
    print(f'{"护型":<12} {"段数":>8} {"平均(周)":>8} {"中位(周)":>8} {"最长(周)":>8}')
    print('-' * 50)
    results = []
    for h, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        avg = s[1] / n
        median = sorted(s[3])[len(s[3]) // 2] if s[3] else 0
        results.append((h, n, avg, median, s[2]))
    # 按平均降序
    results.sort(key=lambda x: -x[2])
    for h, n, avg, median, longest in results:
        print(f'{h:<12} {n:>8} {avg:>8.2f} {median:>8} {longest:>8}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['护型', '段数', '平均(周)', '中位(周)', '最长(周)'])
        for h, n, avg, median, longest in results:
            w.writerow([h, n, f'{avg:.2f}', median, longest])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
