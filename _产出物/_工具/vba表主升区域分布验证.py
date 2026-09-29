#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析主升区域（WXAB>0 且 WXZB>0）内各柱的高幅、涨幅分布规律

用户问题（2026-09-29）：
1. WXZC>0 是否覆盖了主升（WXAB>0 且 WXZB>0）的大部分区域？
2. 主升区域内各柱的高幅、涨幅的分布规律，是否有高幅>3% 的基本规律？
3. 是否有阴柱后必有高幅>3% 的基本规律？

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨（本周涨幅）  [2] PR（临涨幅=下周涨幅）  [3] HR（临高幅=下周高幅）
    [15] ZB周=WXZB  [16] ZC周=WXZC  [20] AB周=WXAB

用法：
    python _产出物/_工具/vba表主升区域分布验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升区域分布验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计
    n_main = 0          # 主升区域样本（WXAB>0 且 WXZB>0）
    n_main_zc_gt0 = 0   # 主升中 WXZC>0
    n_main_zc_le0 = 0   # 主升中 WXZC<=0
    # 主升区域内 HR 分布
    hr_bins = defaultdict(int)  # HR 分档
    hr_sum = 0.0
    hr_n = 0
    hr_gt3 = 0          # HR>3%
    hr_gt5 = 0          # HR>5%
    # 主升区域内 周涨 分布
    zhou_sum = 0.0
    zhou_n = 0
    zhou_gt0 = 0
    # 阴柱（周涨<0）后 HR>3%
    n_yin = 0           # 主升中阴柱数
    n_yin_hr_gt3 = 0    # 阴柱后 HR>3%
    # 阳柱（周涨>0）后 HR>3%
    n_yang = 0
    n_yang_hr_gt3 = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 2, 3, 15, 16, 20])
            df.columns = ['周涨', 'PR', 'HR', 'WXZB', 'WXZC', 'WXAB']
        except Exception:
            continue
        for c in ['周涨', 'PR', 'HR', 'WXZB', 'WXZC', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'PR', 'HR', 'WXZB', 'WXZC', 'WXAB'])
        if df.empty:
            continue

        # 主升区域 = WXAB>0 且 WXZB>0
        main = (df['WXAB'] > 0) & (df['WXZB'] > 0)
        sub = df[main]
        if sub.empty:
            continue

        n_main += len(sub)
        n_main_zc_gt0 += int((sub['WXZC'] > 0).sum())
        n_main_zc_le0 += int((sub['WXZC'] <= 0).sum())

        # HR 分布
        for hr in sub['HR']:
            hr_sum += hr
            hr_n += 1
            if hr > 3:
                hr_gt3 += 1
            if hr > 5:
                hr_gt5 += 1
            # 分档
            if hr <= 0:
                hr_bins['<=0'] += 1
            elif hr <= 1:
                hr_bins['0-1'] += 1
            elif hr <= 2:
                hr_bins['1-2'] += 1
            elif hr <= 3:
                hr_bins['2-3'] += 1
            elif hr <= 5:
                hr_bins['3-5'] += 1
            elif hr <= 8:
                hr_bins['5-8'] += 1
            else:
                hr_bins['>8'] += 1

        # 周涨分布
        zhou_sum += float(sub['周涨'].sum())
        zhou_n += len(sub)
        zhou_gt0 += int((sub['周涨'] > 0).sum())

        # 阴柱/阳柱后 HR>3%
        for idx in range(len(sub)):
            if sub['周涨'].iloc[idx] < 0:
                n_yin += 1
                if sub['HR'].iloc[idx] > 3:
                    n_yin_hr_gt3 += 1
            elif sub['周涨'].iloc[idx] > 0:
                n_yang += 1
                if sub['HR'].iloc[idx] > 3:
                    n_yang_hr_gt3 += 1

    # 输出
    print(f'\n=== 主升区域（WXAB>0 且 WXZB>0）分析 ===')
    print(f'主升区域样本: {n_main}')
    print(f'\n--- 问题1：WXZC>0 覆盖主升区域的比例 ---')
    print(f'WXZC>0: {n_main_zc_gt0} ({n_main_zc_gt0/n_main*100:.1f}%)')
    print(f'WXZC<=0: {n_main_zc_le0} ({n_main_zc_le0/n_main*100:.1f}%)')
    print(f'\n--- 问题2：主升区域内 HR（下周高幅）分布 ---')
    print(f'平均HR: {hr_sum/hr_n:.2f}%')
    print(f'P(HR>3%): {hr_gt3/hr_n*100:.1f}%')
    print(f'P(HR>5%): {hr_gt5/hr_n*100:.1f}%')
    print('HR分档:')
    for k in ['<=0', '0-1', '1-2', '2-3', '3-5', '5-8', '>8']:
        print(f'  {k}: {hr_bins[k]} ({hr_bins[k]/hr_n*100:.1f}%)')
    print(f'\n主升区域内 周涨分布:')
    print(f'平均周涨: {zhou_sum/zhou_n:.3f}%')
    print(f'正周涨: {zhou_gt0/zhou_n*100:.1f}%')
    print(f'\n--- 问题3：阴柱后 HR>3% 规律 ---')
    print(f'阴柱（周涨<0）: {n_yin}，后 HR>3%: {n_yin_hr_gt3} ({n_yin_hr_gt3/n_yin*100:.1f}%)')
    print(f'阳柱（周涨>0）: {n_yang}，后 HR>3%: {n_yang_hr_gt3} ({n_yang_hr_gt3/n_yang*100:.1f}%)')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['指标', '值'])
        w.writerow(['主升区域样本', n_main])
        w.writerow(['WXZC>0占比', f'{n_main_zc_gt0/n_main*100:.1f}%'])
        w.writerow(['WXZC<=0占比', f'{n_main_zc_le0/n_main*100:.1f}%'])
        w.writerow(['平均HR', f'{hr_sum/hr_n:.2f}%'])
        w.writerow(['P(HR>3%)', f'{hr_gt3/hr_n*100:.1f}%'])
        w.writerow(['P(HR>5%)', f'{hr_gt5/hr_n*100:.1f}%'])
        w.writerow(['平均周涨', f'{zhou_sum/zhou_n:.3f}%'])
        w.writerow(['正周涨占比', f'{zhou_gt0/zhou_n*100:.1f}%'])
        w.writerow(['阴柱后HR>3%', f'{n_yin_hr_gt3/n_yin*100:.1f}%'])
        w.writerow(['阳柱后HR>3%', f'{n_yang_hr_gt3/n_yang*100:.1f}%'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()