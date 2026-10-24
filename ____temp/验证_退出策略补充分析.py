# -*- coding: utf-8 -*-
"""
补充分析：策略B（WXZC<0 或虎退出）中"虎退出"的贡献
以及：下破 WJB 但 ZC>0 且非虎 的子集，继续持有的收益（回答"过早退出是否踏空"）
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

# 逐文件处理
# 统计：策略B 中，退出原因分布（WXZC<0 vs 虎）
exit_reason = {'ZC_neg': 0, 'hu': 0}
# 下破 WJB 但 ZC>0 且非虎 的子集，继续持有收益
sub_ret_1w = []
sub_ret_4w = []
sub_ret_8w = []
sub_win_1w = 0
sub_win_4w = 0
sub_total = 0

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        n = len(ret)
        ZB_pos = ZB > 0
        ZC_pos = ZC > 0
        is_hu = (AB < 0) & (ZB < 0)
        prev_ZB_pos = np.concatenate([[False], ZB_pos[:-1]])
        break_WJB = (~ZB_pos) & prev_ZB_pos  # 下破 WJB 事件

        # 策略B 退出原因统计
        for j in range(n):
            if ZC_pos[j] and is_hu[j]:
                # 这是"虎退出"条件（ZC>0 且虎）
                # 但需要判断是否真的在持仓中触发退出，这里简化：统计所有满足"ZC>0且虎"的周
                exit_reason['hu'] += 1
            if not ZC_pos[j]:
                exit_reason['ZC_neg'] += 1

        # 下破 WJB 但 ZC>0 且非虎 的子集
        for j in range(n):
            if break_WJB[j] and ZC[j] > 0 and not is_hu[j]:
                sub_total += 1
                # 未来1/4/8周累计收益（不含当周）
                r1 = sum(ret[j+1:j+2]) if j+1 < n else np.nan
                r4 = sum(ret[j+1:j+5]) if j+4 < n else np.nan
                r8 = sum(ret[j+1:j+9]) if j+8 < n else np.nan
                if not np.isnan(r1):
                    sub_ret_1w.append(r1)
                    if r1 > 0: sub_win_1w += 1
                if not np.isnan(r4):
                    sub_ret_4w.append(r4)
                    if r4 > 0: sub_win_4w += 1
                if not np.isnan(r8):
                    sub_ret_8w.append(r8)
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('分析1：策略B 退出条件中，"WXZC<0" vs "WXZC>0且虎" 的触发周数')
print('='*70)
print(f'  WXZC<0 触发周数: {exit_reason["ZC_neg"]}')
print(f'  WXZC>0且虎 触发周数: {exit_reason["hu"]}')
total = exit_reason['ZC_neg'] + exit_reason['hu']
print(f'  虎退出占比: {exit_reason["hu"]/total*100:.2f}%')

print('\n' + '='*70)
print('分析2：下破 WJB 但 ZC>0 且非虎 的子集，继续持有的收益')
print('（用户提议中"不退出"的情形 —— 过早退出是否踏空？）')
print('='*70)
print(f'  事件总数: {sub_total}')
sub_ret_1w = np.array(sub_ret_1w)
sub_ret_4w = np.array(sub_ret_4w)
sub_ret_8w = np.array(sub_ret_8w)
print(f'\n  未来1周: 均值 {sub_ret_1w.mean():.2f}%  中位 {np.median(sub_ret_1w):.2f}%  正收益 {(sub_ret_1w>0).mean()*100:.2f}%')
print(f'  未来4周: 均值 {sub_ret_4w.mean():.2f}%  中位 {np.median(sub_ret_4w):.2f}%  正收益 {(sub_ret_4w>0).mean()*100:.2f}%')
print(f'  未来8周: 均值 {sub_ret_8w.mean():.2f}%  中位 {np.median(sub_ret_8w):.2f}%  正收益 {(sub_ret_8w>0).mean()*100:.2f}%')

print('\n完成')