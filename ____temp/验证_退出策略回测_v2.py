# -*- coding: utf-8 -*-
"""
策略回测（向量化）：方法周A 退出条件对比
策略A（当前）：介入后 WXZB<0（下破 WJB）即退出
策略B（提议）：介入后 WXZC<0（下破 WJC）或（WXZC>0 且虎）才退出
"""
import pandas as pd
import numpy as np
import glob

DATA_DIR = '昭明算展/谕组周'
files = glob.glob(f'{DATA_DIR}/谕组周_*.csv')
print(f'共 {len(files)} 个文件')

COL_DATE = 0
COL_WEEK_RET = 1
COL_HR = 3
COL_HU = 4
COL_ZA = 16
COL_ZB = 17
COL_ZC = 18
COL_AB = 22

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    df = df.iloc[:, [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_AB]]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'AB']
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'AB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# 逐文件回测（避免 concat 大表 + groupby 开销）
def backtest_fid(ret, ZB, ZC, AB):
    """对单个 fid 的 numpy 数组回测，返回 (策略A交易收益列表, 策略B交易收益列表, A持有周数, B持有周数)"""
    n = len(ret)
    ZB_pos = ZB > 0
    ZC_pos = ZC > 0
    is_hu = (AB < 0) & (ZB < 0)
    # 介入：ZC_pos 且 前一周非 ZC_pos 且 ZC<=2
    entry = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if ZC_pos[i] and not ZC_pos[i-1] and ZC[i] <= 2:
            entry[i] = True
    # 策略A退出：ZB<=0
    exit_A = ~ZB_pos
    # 策略B退出：ZC<=0 或 (ZC>0 且虎)
    exit_B = (~ZC_pos) | (ZC_pos & is_hu)

    trades_A = []
    trades_B = []
    hold_A = []
    hold_B = []
    # 策略A
    holding = False; acc = 0.0; h = 0
    for i in range(n):
        if not holding:
            if entry[i]:
                holding = True; acc = ret[i]; h = 1
        else:
            if exit_A[i]:
                trades_A.append(acc); hold_A.append(h); holding = False
            else:
                acc += ret[i]; h += 1
    if holding:
        trades_A.append(acc); hold_A.append(h)
    # 策略B
    holding = False; acc = 0.0; h = 0
    for i in range(n):
        if not holding:
            if entry[i]:
                holding = True; acc = ret[i]; h = 1
        else:
            if exit_B[i]:
                trades_B.append(acc); hold_B.append(h); holding = False
            else:
                acc += ret[i]; h += 1
    if holding:
        trades_B.append(acc); hold_B.append(h)
    return trades_A, trades_B, hold_A, hold_B

trades_A_all = []
trades_B_all = []
hold_A_all = []
hold_B_all = []

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        ta, tb, ha, hb = backtest_fid(ret, ZB, ZC, AB)
        trades_A_all.extend(ta)
        trades_B_all.extend(tb)
        hold_A_all.extend(ha)
        hold_B_all.extend(hb)
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成，共 {len(files)} 个文件')

print('\n' + '='*70)
print('策略回测结果（方法周A 介入，不同退出条件）')
print('='*70)

for name, trades, holds in [('A', trades_A_all, hold_A_all), ('B', trades_B_all, hold_B_all)]:
    trades = np.array(trades)
    holds = np.array(holds)
    print(f'\n--- 策略{name}（{"WXZB<0退出" if name=="A" else "WXZC<0或虎退出"}）---')
    print(f'  交易次数: {len(trades)}')
    print(f'  平均每笔收益: {trades.mean():.2f}%')
    print(f'  中位每笔收益: {np.median(trades):.2f}%')
    print(f'  盈利交易占比: {(trades>0).mean()*100:.2f}%')
    print(f'  累计收益(简单加总): {trades.sum():.2f}%')
    print(f'  平均持有周数: {holds.mean():.1f}')
    print(f'  中位持有周数: {np.median(holds):.1f}')
    # 年化（假设平均每周收益，52周/年）
    avg_weekly = trades.mean() / holds.mean() if holds.mean() > 0 else 0
    print(f'  平均每周收益: {avg_weekly:.3f}%')
    print(f'  年化(简单): {avg_weekly*52:.1f}%')

print('\n完成')