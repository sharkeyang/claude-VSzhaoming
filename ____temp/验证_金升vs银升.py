# -*- coding: utf-8 -*-
"""
重跑"金升 vs 银升"全量验证（当前 2026-10-15 数据，3449 只）
金升 = CD>0（JC 在 JD 之上，长期趋势向上）
银升 = CD≤0 + ZD>0（价格在 EMA60 之上，但长期趋势未确认）
对比：胜率、收益均值、收益中位数、假信号率
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
COL_ZD = 19   # WXZD
COL_ZE = 20   # WXZE
COL_AB = 22
COL_CD = 27   # WXCD = JC vs JD 交叉天数

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    df = df.iloc[:, [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_ZD, COL_ZE, COL_AB, COL_CD]]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'ZD', 'ZE', 'AB', 'CD']
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'ZD', 'ZE', 'AB', 'CD']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# 统计
# 金升：CD>0
# 银升：CD<=0 + ZD>0
# 看"未来是否转金升"（假信号率）和收益
stats = {
    '金升': {'n': 0, 'ret': [], 'win': 0},
    '银升': {'n': 0, 'ret': [], 'win': 0, 'to_jin': 0, 'to_jin_ret': []},
}

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        ZD = df['ZD'].to_numpy(dtype=float)
        CD = df['CD'].to_numpy(dtype=float)
        n = len(ret)
        for j in range(n):
            # 金升：CD>0
            if CD[j] > 0:
                s = stats['金升']
                s['n'] += 1
                if j+1 < n:
                    s['ret'].append(ret[j+1])
                    if ret[j+1] > 0: s['win'] += 1
            # 银升：CD<=0 + ZD>0
            elif CD[j] <= 0 and ZD[j] > 0:
                s = stats['银升']
                s['n'] += 1
                if j+1 < n:
                    s['ret'].append(ret[j+1])
                    if ret[j+1] > 0: s['win'] += 1
                # 未来是否转金升（未来4周内 CD>0）
                if j+4 < n:
                    fut_cd = CD[j+1:j+5]
                    if (fut_cd > 0).any():
                        s['to_jin'] += 1
                        s['to_jin_ret'].append(sum(ret[j+1:j+5]))
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('金升 vs 银升 全量验证（当前 2026-10-15 数据）')
print('='*70)

for name in ['金升', '银升']:
    s = stats[name]
    ret = np.array(s['ret'])
    print(f'\n  {name}（n={s["n"]}）:')
    print(f'    胜率（下周涨>0）: {s["win"]/s["n"]*100:.2f}%')
    print(f'    收益均值: {ret.mean():.2f}%')
    print(f'    收益中位数: {np.median(ret):.2f}%')
    if name == '银升':
        print(f'    未来4周内转金升率: {s["to_jin"]/s["n"]*100:.2f}%')
        print(f'    假信号率（未转金升）: {(1-s["to_jin"]/s["n"])*100:.2f}%')
        to_jin_ret = np.array(s['to_jin_ret'])
        print(f'    转金升后未来4周收益: {to_jin_ret.mean():.2f}%')

print('\n完成')