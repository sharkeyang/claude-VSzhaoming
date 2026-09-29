#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于主升区域分布规律的操作策略验证

核心结论（§8.1.5.6）：
1. WXZC>0 覆盖主升区域 94.6%
2. 主升区域内 P(HR>3%)=68.7%
3. 阴柱后 HR>3% 仅 39.4%，阳柱后 90.0%

可操作策略：主升区域内（WXAB>0 且 WXZB>0），阳柱（周涨>0）后持有/介入，
阴柱（周涨<0）后减仓/观望。

验证：
1. 主升区域内，阳柱后下周收益（PR）vs 阴柱后下周收益（PR）
2. 策略（阳柱持有、阴柱空仓）的累计收益 vs 始终持有

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨（本周涨幅）  [2] PR（临涨幅=下周涨幅）
    [15] ZB周=WXZB  [20] AB周=WXAB

用法：
    python _产出物/_工具/vba表主升区域操作策略验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升区域操作策略验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计
    # 主升区域内 阳柱/阴柱 后下周收益
    n_yang = 0
    pr_yang_sum = 0.0
    n_yin = 0
    pr_yin_sum = 0.0
    # 策略收益（阳柱持有、阴柱空仓）
    strat_sum = 0.0
    strat_n = 0
    # 始终持有（主升区域内所有周）
    hold_sum = 0.0
    hold_n = 0
    # 每只股票策略跑赢基准
    n_stock = 0
    n_win = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 2, 15, 20])
            df.columns = ['周涨', 'PR', 'WXZB', 'WXAB']
        except Exception:
            continue
        for c in ['周涨', 'PR', 'WXZB', 'WXAB']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['周涨', 'PR', 'WXZB', 'WXAB'])
        if df.empty:
            continue

        # 主升区域 = WXAB>0 且 WXZB>0
        main = (df['WXAB'] > 0) & (df['WXZB'] > 0)
        sub = df[main]
        if sub.empty:
            continue

        # 阳柱/阴柱后下周收益
        yang = sub[sub['周涨'] > 0]
        yin = sub[sub['周涨'] < 0]
        n_yang += len(yang)
        pr_yang_sum += float(yang['PR'].sum())
        n_yin += len(yin)
        pr_yin_sum += float(yin['PR'].sum())

        # 策略收益（阳柱持有、阴柱空仓）
        strat = float(sub.loc[sub['周涨'] > 0, 'PR'].sum())
        hold = float(sub['PR'].sum())
        strat_sum += strat
        strat_n += int((sub['周涨'] > 0).sum())
        hold_sum += hold
        hold_n += len(sub)

        # 每只股票策略跑赢基准
        n_stock += 1
        if strat > hold:
            n_win += 1

    # 输出
    print(f'\n=== 主升区域内操作策略验证（阳柱持有、阴柱空仓）===')
    print(f'主升区域内阳柱（周涨>0）: {n_yang}，后下周平均收益: {pr_yang_sum/n_yang:.3f}%')
    print(f'主升区域内阴柱（周涨<0）: {n_yin}，后下周平均收益: {pr_yin_sum/n_yin:.3f}%')
    print(f'\n策略（阳柱持有、阴柱空仓）: 累计收益={strat_sum:.2f}% 持有周数={strat_n}')
    print(f'始终持有（主升区域内所有周）: 累计收益={hold_sum:.2f}% 周数={hold_n}')
    print(f'策略/始终持有 累计收益比: {strat_sum/hold_sum:.2f}x')
    print(f'策略跑赢基准的股票: {n_win}/{n_stock} = {n_win/n_stock*100:.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['指标', '值'])
        w.writerow(['阳柱后下周平均收益', f'{pr_yang_sum/n_yang:.3f}%'])
        w.writerow(['阴柱后下周平均收益', f'{pr_yin_sum/n_yin:.3f}%'])
        w.writerow(['策略累计收益', f'{strat_sum:.2f}%'])
        w.writerow(['始终持有累计收益', f'{hold_sum:.2f}%'])
        w.writerow(['策略/始终持有比', f'{strat_sum/hold_sum:.2f}x'])
        w.writerow(['策略跑赢基准股票', f'{n_win/n_stock*100:.1f}%'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()