#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
周类 WJC 择时策略验证：只依赖 WJC，WXZC>0 持有、WXZC<0 退出，是否必赢？

用户假设（2026-09-29）：针对周类，只依赖 WJC（周线 EMA26 = 半年线），
当 WXZC>0（价格在 WJC 之上）时持有，当 WXZC<0（价格在 WJC 之下）时退出，就能必赢。

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨（本周涨幅）  [16] ZC周 = WXZC（价格 vs WJC 交叉）

策略：每周看 WXZC，>0 则持有（获得本周涨幅），<0 则空仓（收益0）。
对比基准：始终持有（所有周涨幅之和）。

用法：
    python _产出物/_工具/vba表WJC择时验证.py
"""
import csv, os, io
import pandas as pd
import numpy as np
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WJC择时验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 全量统计
    tot_hold = 0.0      # 始终持有累计涨幅
    tot_strat = 0.0     # 策略累计涨幅
    n_hold = 0          # 始终持有周数
    n_strat = 0         # 策略持有周数（WXZC>0）
    n_stock = 0         # 股票数
    n_win = 0           # 策略跑赢基准的股票数
    n_neg = 0           # 策略累计收益为负的股票数
    n_hold_neg = 0      # 始终持有累计收益为负的股票数

    # 每只股票统计
    stock_stats = []    # (代码, 始终持有累计, 策略累计, 策略周数, 总周数)

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 16])
            df.columns = ['周涨', 'WXZC']
        except Exception:
            continue
        df['周涨'] = pd.to_numeric(df['周涨'], errors='coerce')
        df['WXZC'] = pd.to_numeric(df['WXZC'], errors='coerce')
        df = df.dropna(subset=['周涨', 'WXZC'])
        if df.empty:
            continue

        n_stock += 1
        hold = float(df['周涨'].sum())          # 始终持有
        strat = float(df.loc[df['WXZC'] > 0, '周涨'].sum())  # WXZC>0持有
        n_hold += len(df)
        n_strat += int((df['WXZC'] > 0).sum())
        tot_hold += hold
        tot_strat += strat
        if strat > hold:
            n_win += 1
        if strat < 0:
            n_neg += 1
        if hold < 0:
            n_hold_neg += 1
        stock_stats.append((cidl, hold, strat, int((df['WXZC'] > 0).sum()), len(df)))

    # 输出
    print(f'\n=== 周类 WJC 择时策略验证（WXZC>0 持有 / WXZC<0 退出）===')
    print(f'股票数: {n_stock}')
    print(f'始终持有: 累计涨幅={tot_hold:.2f}% 周数={n_hold} 平均周涨幅={tot_hold/n_hold:.3f}%')
    print(f'策略:     累计涨幅={tot_strat:.2f}% 周数={n_strat} 平均周涨幅={tot_strat/n_strat:.3f}%')
    print(f'策略/始终持有 累计涨幅比: {tot_strat/tot_hold:.2f}x')
    print(f'策略持有周占比: {n_strat/n_hold*100:.1f}%')
    print(f'策略跑赢基准的股票: {n_win}/{n_stock} = {n_win/n_stock*100:.1f}%')
    print(f'策略累计收益为负的股票: {n_neg}/{n_stock} = {n_neg/n_stock*100:.1f}%')
    print(f'始终持有累计收益为负的股票: {n_hold_neg}/{n_stock} = {n_hold_neg/n_stock*100:.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['代码', '始终持有累计%', '策略累计%', '策略周数', '总周数', '策略/持有比'])
        for cidl, hold, strat, ns, nt in stock_stats:
            ratio = strat / hold if hold != 0 else 0
            w.writerow([cidl, f'{hold:.2f}', f'{strat:.2f}', ns, nt, f'{ratio:.2f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()