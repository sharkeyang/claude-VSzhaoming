#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比：主升、非主升、不区分主升 三者的表现，验证主升条件是否有明显区分作用

用户问题（2026-09-29）：主升、非主升、不区分主升，三者表现如何？是否主升条件有明显的区分作用？

主升区域 = WXAB>0 且 WXZB>0
非主升区域 = WXAB<=0 或 WXZB<=0
不区分 = 全部样本

对比指标：平均周涨、正周涨%、平均HR、P(HR>3%)、阳柱后/阴柱后下周收益

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [2] PR（临涨幅=下周涨幅）  [3] HR（临高幅=下周高幅）
    [15] ZB周=WXZB  [20] AB周=WXAB

用法：
    python _产出物/_工具/vba表主升非主升对比.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升非主升对比结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：区域 -> [n, 周涨和, 正周涨数, HR和, HR>3数, 阳柱后PR和, 阳柱数, 阴柱后PR和, 阴柱数]
    stat = defaultdict(lambda: [0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 2, 3, 15, 20])
            df.columns = ['周涨', 'PR', 'HR', 'WXZB', 'WXAB']
        except Exception:
            continue
        for c in ['周涨', 'PR', 'HR', 'WXZB', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'PR', 'HR', 'WXZB', 'WXAB'])
        if df.empty:
            continue

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += float(sub['周涨'].sum())
            s[2] += int((sub['周涨'] > 0).sum())
            s[3] += float(sub['HR'].sum())
            s[4] += int((sub['HR'] > 3).sum())
            # 阳柱后 PR
            yang = sub[sub['周涨'] > 0]
            s[5] += float(yang['PR'].sum())
            s[6] += len(yang)
            # 阴柱后 PR
            yin = sub[sub['周涨'] < 0]
            s[7] += float(yin['PR'].sum())
            s[8] += len(yin)

        # 主升区域
        mark((df['WXAB'] > 0) & (df['WXZB'] > 0), '主升')
        # 非主升区域
        mark(~((df['WXAB'] > 0) & (df['WXZB'] > 0)), '非主升')
        # 不区分
        mark(df['周涨'].notna(), '不区分')

    # 输出
    print(f'\n=== 主升 / 非主升 / 不区分 三者表现对比 ===')
    print(f'{"区域":<8} {"n":>10} {"平均周涨":>9} {"正周涨%":>8} {"平均HR":>8} {"P(HR>3%)":>9} {"阳柱后PR":>9} {"阴柱后PR":>9}')
    print('-' * 85)
    for name in ['主升', '非主升', '不区分']:
        s = stat[name]
        if s[0] == 0:
            continue
        n = s[0]
        avg_zhou = s[1] / n
        p_zhou = s[2] / n * 100
        avg_hr = s[3] / n
        p_hr3 = s[4] / n * 100
        yang_pr = s[5] / s[6] if s[6] else 0
        yin_pr = s[7] / s[8] if s[8] else 0
        print(f'{name:<8} {n:>10} {avg_zhou:>9.3f}% {p_zhou:>7.1f}% {avg_hr:>8.2f}% {p_hr3:>8.1f}% {yang_pr:>9.3f}% {yin_pr:>9.3f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['区域', 'n', '平均周涨%', '正周涨%', '平均HR%', 'P(HR>3%)%', '阳柱后PR%', '阴柱后PR%'])
        for name in ['主升', '非主升', '不区分']:
            s = stat[name]
            if s[0] == 0:
                continue
            n = s[0]
            avg_zhou = s[1] / n
            p_zhou = s[2] / n * 100
            avg_hr = s[3] / n
            p_hr3 = s[4] / n * 100
            yang_pr = s[5] / s[6] if s[6] else 0
            yin_pr = s[7] / s[8] if s[8] else 0
            w.writerow([name, n, f'{avg_zhou:.3f}', f'{p_zhou:.1f}', f'{avg_hr:.2f}', f'{p_hr3:.1f}', f'{yang_pr:.3f}', f'{yin_pr:.3f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()