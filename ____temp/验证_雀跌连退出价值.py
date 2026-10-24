# -*- coding: utf-8 -*-
"""
验证：基础共用层 2.1 第③条 "WXZC>0 雀+跌连 → 截断亏损" 是否值得纳入方法周A退出
雀 = WXAB>0 且 WXZB<0
跌连 = 柱排[8] 柱型序列含 W
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
COL_PAIPAI = 8  # 柱排

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    df = df.iloc[:, [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_AB, COL_PAIPAI]]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'AB', 'paipai']
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'AB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# 跌连判定：柱排[8] 柱型序列含 W
def is_dielian(paipai):
    if not isinstance(paipai, str):
        return False
    return 'W' in paipai

# 逐文件统计
# 条件：WXZC>0 且 雀（AB>0 且 ZB<0）且 跌连
# 看下周收益
next_ret = []
next_ret_hu = []  # 对照组：WXZC>0 且虎
next_ret_que_nodielian = []  # 对照组：WXZC>0 且雀 但非跌连
n_que_dielian = 0
n_hu = 0
n_que_nodielian = 0

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        paipai = df['paipai'].tolist()
        n = len(ret)
        for j in range(n):
            if ZC[j] > 0:  # WXZC>0
                is_que = (AB[j] > 0) and (ZB[j] < 0)
                is_hu = (AB[j] < 0) and (ZB[j] < 0)
                is_dl = is_dielian(paipai[j])
                if is_que and is_dl:
                    n_que_dielian += 1
                    if j+1 < n:
                        next_ret.append(ret[j+1])
                elif is_hu:
                    n_hu += 1
                    if j+1 < n:
                        next_ret_hu.append(ret[j+1])
                elif is_que and not is_dl:
                    n_que_nodielian += 1
                    if j+1 < n:
                        next_ret_que_nodielian.append(ret[j+1])
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('WXZC>0 区域内，不同状态的下一周收益')
print('='*70)

def show(name, arr, n):
    arr = np.array(arr)
    print(f'\n  {name}（n={n}）:')
    print(f'    下周均值: {arr.mean():.2f}%  中位: {np.median(arr):.2f}%  下周涨>0: {(arr>0).mean()*100:.2f}%')

show('雀+跌连（③截断亏损）', next_ret, n_que_dielian)
show('虎（②提前退出）', next_ret_hu, n_hu)
show('雀 非跌连（对照）', next_ret_que_nodielian, n_que_nodielian)

print('\n完成')