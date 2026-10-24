#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：主升区域（DXZE>0 + DXCD=上）跌破各均线后 20 日恢复率

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [8]  DXCD（上/中/下/忐/忠/忑）
    [13] 日ZA = DTZA（JZ vs JA，>0=站上DJA）
    [14] 日ZC = DTZC（JZ vs JC，>0=站上DJC）
    [15] 日ZE = DTZE（JZ vs JE，>0=站上DJE）
    [66] DTZB（JZ vs JB，>0=站上DJB）
    [67] DTZD（JZ vs JD，>0=站上DJD）

验证目标：
    主升区域（DXZE>0 + DXCD=上）跌破各均线（DJA/DJB/DJC/DJD）后，
    未来 5/10/20 日内重新站上的比例（恢复率）。
"""
import os, json
import pandas as pd
import numpy as np

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}

def load_board_map():
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)

def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计：均线 -> [跌破事件数, 5日恢复, 10日恢复, 20日恢复]
    stat = {
        'DJA': [0, 0, 0, 0],
        'DJB': [0, 0, 0, 0],
        'DJC': [0, 0, 0, 0],
        'DJD': [0, 0, 0, 0],
    }

    n_files = 0
    for i, fname in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        n_files += 1
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0],
                             usecols=[8, 13, 14, 15, 66, 67])
            df.columns = ['DXCD', 'DTZA', 'DTZC', 'DTZE', 'DTZB', 'DTZD']
        except Exception:
            continue
        if df.empty:
            continue

        for c in ['DTZA', 'DTZC', 'DTZE', 'DTZB', 'DTZD']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['DTZA', 'DTZC', 'DTZE', 'DTZB', 'DTZD'])
        if df.empty:
            continue

        # 主升区域：DXZE>0 + DXCD=上
        dxcd = df['DXCD'].astype(str).str[0]
        main_up = (df['DTZE'] > 0) & (dxcd == '上')
        if not main_up.any():
            continue

        za = df['DTZA'].values
        zb = df['DTZB'].values
        zc = df['DTZC'].values
        zd = df['DTZD'].values
        n = len(df)

        # 对每个主升区域内的"跌破"事件，检查未来 N 日恢复率
        for idx in range(n):
            if not main_up.iloc[idx]:
                continue
            # 跌破 DJA（DTZA 由 >0 转 <=0）
            if za[idx] <= 0 and idx > 0 and za[idx-1] > 0:
                stat['DJA'][0] += 1
                for k in range(1, min(21, n - idx)):
                    if za[idx + k] > 0:
                        if k <= 5: stat['DJA'][1] += 1
                        if k <= 10: stat['DJA'][2] += 1
                        if k <= 20: stat['DJA'][3] += 1
                        break
            # 跌破 DJB（DTZB 由 >0 转 <=0）
            if zb[idx] <= 0 and idx > 0 and zb[idx-1] > 0:
                stat['DJB'][0] += 1
                for k in range(1, min(21, n - idx)):
                    if zb[idx + k] > 0:
                        if k <= 5: stat['DJB'][1] += 1
                        if k <= 10: stat['DJB'][2] += 1
                        if k <= 20: stat['DJB'][3] += 1
                        break
            # 跌破 DJC（DTZC 由 >0 转 <=0）
            if zc[idx] <= 0 and idx > 0 and zc[idx-1] > 0:
                stat['DJC'][0] += 1
                for k in range(1, min(21, n - idx)):
                    if zc[idx + k] > 0:
                        if k <= 5: stat['DJC'][1] += 1
                        if k <= 10: stat['DJC'][2] += 1
                        if k <= 20: stat['DJC'][3] += 1
                        break
            # 跌破 DJD（DTZD 由 >0 转 <=0）
            if zd[idx] <= 0 and idx > 0 and zd[idx-1] > 0:
                stat['DJD'][0] += 1
                for k in range(1, min(21, n - idx)):
                    if zd[idx + k] > 0:
                        if k <= 5: stat['DJD'][1] += 1
                        if k <= 10: stat['DJD'][2] += 1
                        if k <= 20: stat['DJD'][3] += 1
                        break

    print(f'\n处理完成：{n_files} 只股票')
    print(f'\n=== 主升区域（DXZE>0 + DXCD=上）跌破各均线后恢复率 ===')
    print(f'{"均线":<6} {"跌破事件":>10} {"5日恢复":>8} {"10日恢复":>8} {"20日恢复":>8}')
    print('-' * 50)
    for ma in ['DJA', 'DJB', 'DJC', 'DJD']:
        s = stat[ma]
        if s[0] == 0:
            continue
        n = s[0]
        print(f'{ma:<6} {n:>10,} {s[1]/n*100:>7.1f}% {s[2]/n*100:>7.1f}% {s[3]/n*100:>7.1f}%')

if __name__ == '__main__':
    main()