# -*- coding: utf-8 -*-
"""
验证：镜面映射 —— 不以WJB作为退出条件(下破WJB不退出)，则也不应以上破WJB作为介入条件
用户推理：WXZA<0本不应退出但87%伴随WXZB<0，所以"下破WJB退出"本质是"因WXZA<0而退出"；
镜面：WXZA>0本不应介入，若也高比例伴随WXZB>0，则"上破WJB介入"本质是"因WXZA>0而介入"。
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

# 统计
n_za_pos = 0
n_za_pos_zb_pos = 0  # WXZA>0 且 WXZB>0
n_za_pos_zb_neg = 0  # WXZA>0 但 WXZB<0

# 上破 WJB 事件（WXZB 从负转正）的后续收益
break_up_WJB_ret = []   # 上破WJB当周后未来1周收益
break_up_WJB_ret4 = []  # 未来4周
break_up_WJB_win1 = 0
break_up_WJB_win4 = 0
n_break_up_WJB = 0

# 上破 WJC 事件（WXZC 从负转正）的后续收益（对比）
break_up_WJC_ret = []
break_up_WJC_ret4 = []
break_up_WJC_win1 = 0
break_up_WJC_win4 = 0
n_break_up_WJC = 0

# 龙骨转正事件（WXAB 从负转正）的后续收益（对比）
break_up_AB_ret = []
break_up_AB_ret4 = []
break_up_AB_win1 = 0
break_up_AB_win4 = 0
n_break_up_AB = 0

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        ZA = df['ZA'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        n = len(ret)
        for j in range(n):
            # 镜面映射：WXZA>0 时 WXZB>0 的比例
            if ZA[j] > 0:
                n_za_pos += 1
                if ZB[j] > 0:
                    n_za_pos_zb_pos += 1
                else:
                    n_za_pos_zb_neg += 1
            # 上破 WJB 事件（本周ZB>0 且 上周ZB<=0）
            if j > 0 and ZB[j] > 0 and ZB[j-1] <= 0:
                n_break_up_WJB += 1
                if j+1 < n:
                    r1 = ret[j+1]
                    break_up_WJB_ret.append(r1)
                    if r1 > 0: break_up_WJB_win1 += 1
                if j+4 < n:
                    r4 = sum(ret[j+1:j+5])
                    break_up_WJB_ret4.append(r4)
                    if r4 > 0: break_up_WJB_win4 += 1
            # 上破 WJC 事件（本周ZC>0 且 上周ZC<=0）
            if j > 0 and ZC[j] > 0 and ZC[j-1] <= 0:
                n_break_up_WJC += 1
                if j+1 < n:
                    r1 = ret[j+1]
                    break_up_WJC_ret.append(r1)
                    if r1 > 0: break_up_WJC_win1 += 1
                if j+4 < n:
                    r4 = sum(ret[j+1:j+5])
                    break_up_WJC_ret4.append(r4)
                    if r4 > 0: break_up_WJC_win4 += 1
            # 龙骨转正事件（本周AB>0 且 上周AB<=0）
            if j > 0 and AB[j] > 0 and AB[j-1] <= 0:
                n_break_up_AB += 1
                if j+1 < n:
                    r1 = ret[j+1]
                    break_up_AB_ret.append(r1)
                    if r1 > 0: break_up_AB_win1 += 1
                if j+4 < n:
                    r4 = sum(ret[j+1:j+5])
                    break_up_AB_ret4.append(r4)
                    if r4 > 0: break_up_AB_win4 += 1
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('镜面映射验证：WXZA>0 时 WXZB>0 的比例（对称于 WXZA<0 时 87% 伴随 WXZB<0）')
print('='*70)
print(f'  WXZA>0 样本: {n_za_pos}')
print(f'  WXZA>0 且 WXZB>0(上破WJB): {n_za_pos_zb_pos} ({n_za_pos_zb_pos/n_za_pos*100:.1f}%)')
print(f'  WXZA>0 但 WXZB<0(未上破WJB): {n_za_pos_zb_neg} ({n_za_pos_zb_neg/n_za_pos*100:.1f}%)')

print('\n' + '='*70)
print('介入信号价值对比：上破WJB vs 上破WJC vs 龙骨转正(WXAB>0)')
print('='*70)

def show(name, arr, arr4, win1, win4, n):
    arr = np.array(arr)
    arr4 = np.array(arr4)
    print(f'\n  {name}（n={n}）:')
    print(f'    未来1周: 均值 {arr.mean():.2f}%  中位 {np.median(arr):.2f}%  涨>0 {(arr>0).mean()*100:.2f}%')
    print(f'    未来4周: 均值 {arr4.mean():.2f}%  中位 {np.median(arr4):.2f}%  涨>0 {(arr4>0).mean()*100:.2f}%')

show('上破WJB（WXZB转正）', break_up_WJB_ret, break_up_WJB_ret4, break_up_WJB_win1, break_up_WJB_win4, n_break_up_WJB)
show('上破WJC（WXZC转正）', break_up_WJC_ret, break_up_WJC_ret4, break_up_WJC_win1, break_up_WJC_win4, n_break_up_WJC)
show('龙骨转正（WXAB>0）', break_up_AB_ret, break_up_AB_ret4, break_up_AB_win1, break_up_AB_win4, n_break_up_AB)

print('\n完成')