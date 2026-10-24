# -*- coding: utf-8 -*-
"""
验证：是否应该只做金（金银唏嘘屎尿六势型）
金=上升主趋势(91.9%维持,12-14周)，银=背离(4-5周)，唏=选择方向(2.44周)
金/银/唏都是ZC>0区。用户问：方法周A框架下(WXZC>0+龙骨WXAB>0)，是否只做金？
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
COL_SHIXING = 12  # 周层势型，第2字符=金银唏嘘屎尿

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    df = df.iloc[:, [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_AB, COL_SHIXING]]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'AB', 'shixing']
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'AB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# 金银唏嘘屎尿 = 势型[12] 第2字符
def get_jinyin(shixing):
    if not isinstance(shixing, str) or len(shixing) < 2:
        return ''
    return shixing[1]

# 统计：方法周A 介入条件（WXZC>0 + 龙骨WXAB>0）下，金银唏的表现
# 以及全量 WXZC>0 下金银唏的表现
stats = {'金': {'n':0,'ret':[],'ret4':[],'hr3':0},
         '银': {'n':0,'ret':[],'ret4':[],'hr3':0},
         '唏': {'n':0,'ret':[],'ret4':[],'hr3':0}}
# 方法周A 条件：WXZC>0 且 WXAB>0（龙骨）
stats_A = {'金': {'n':0,'ret':[],'ret4':[],'hr3':0},
           '银': {'n':0,'ret':[],'ret4':[],'hr3':0},
           '唏': {'n':0,'ret':[],'ret4':[],'hr3':0}}

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        HR = df['HR'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        shixing = df['shixing'].tolist()
        n = len(ret)
        for j in range(n):
            jy = get_jinyin(shixing[j])
            if jy not in stats: continue
            if ZC[j] > 0:  # WXZC>0
                stats[jy]['n'] += 1
                if j+1 < n:
                    stats[jy]['ret'].append(ret[j+1])
                    if HR[j+1] >= 3: stats[jy]['hr3'] += 1
                if j+4 < n:
                    stats[jy]['ret4'].append(sum(ret[j+1:j+5]))
                # 方法周A 条件：WXAB>0（龙骨）
                if AB[j] > 0:
                    stats_A[jy]['n'] += 1
                    if j+1 < n:
                        stats_A[jy]['ret'].append(ret[j+1])
                        if HR[j+1] >= 3: stats_A[jy]['hr3'] += 1
                    if j+4 < n:
                        stats_A[jy]['ret4'].append(sum(ret[j+1:j+5]))
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('WXZC>0 区域内，金银唏的表现（全量）')
print('='*70)
for jy in ['金', '银', '唏']:
    s = stats[jy]
    ret = np.array(s['ret'])
    ret4 = np.array(s['ret4'])
    print(f'\n  {jy}（n={s["n"]}）:')
    print(f'    下周均值: {ret.mean():.2f}%  中位: {np.median(ret):.2f}%  下周涨>0: {(ret>0).mean()*100:.2f}%  下周HR≥3%: {s["hr3"]/max(s["n"],1)*100:.2f}%')
    print(f'    未来4周均值: {ret4.mean():.2f}%  中位: {np.median(ret4):.2f}%  涨>0: {(ret4>0).mean()*100:.2f}%')

print('\n' + '='*70)
print('方法周A 条件（WXZC>0 + 龙骨WXAB>0）下，金银唏的表现')
print('='*70)
for jy in ['金', '银', '唏']:
    s = stats_A[jy]
    ret = np.array(s['ret'])
    ret4 = np.array(s['ret4'])
    print(f'\n  {jy}（n={s["n"]}）:')
    print(f'    下周均值: {ret.mean():.2f}%  中位: {np.median(ret):.2f}%  下周涨>0: {(ret>0).mean()*100:.2f}%  下周HR≥3%: {s["hr3"]/max(s["n"],1)*100:.2f}%')
    print(f'    未来4周均值: {ret4.mean():.2f}%  中位: {np.median(ret4):.2f}%  涨>0: {(ret4>0).mean()*100:.2f}%')

print('\n完成')