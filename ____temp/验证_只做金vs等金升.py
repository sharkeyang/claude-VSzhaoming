# -*- coding: utf-8 -*-
"""
验证：哪种结论可靠？
结论A：只做金（金银唏中只做金，不做银/唏）
结论B：等金升才进场（金银唏中，CD>0金升 vs CD≤0银升）

关键：金银唏 = WXCD势型[12]第2字符；金升/银升 = CD[27]正负（CD=JC vs JD交叉）
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
COL_CD = 27   # WXCD = JC vs JD 交叉天数
COL_SHIXING = 12  # 周层势型，第2字符=金银唏嘘屎尿

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    df = df.iloc[:, [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_AB, COL_CD, COL_SHIXING]]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'AB', 'CD', 'shixing']
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'AB', 'CD']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def get_jinyin(shixing):
    if not isinstance(shixing, str) or len(shixing) < 2:
        return ''
    return shixing[1]

# 方法周A 条件：WXZC>0 + 龙骨WXAB>0
# 统计：金银唏 × 金升(CD>0)/银升(CD≤0) 的表现
stats = {}
# key: (金银, 金升/银升)
for jy in ['金', '银', '唏']:
    for cd in ['金升', '银升']:
        stats[(jy, cd)] = {'n':0,'ret':[],'ret4':[],'hr3':0,'win1':0}

for i, fp in enumerate(files):
    try:
        df = read_file(fp)
        ret = df['week_ret'].to_numpy(dtype=float)
        HR = df['HR'].to_numpy(dtype=float)
        ZB = df['ZB'].to_numpy(dtype=float)
        ZC = df['ZC'].to_numpy(dtype=float)
        AB = df['AB'].to_numpy(dtype=float)
        CD = df['CD'].to_numpy(dtype=float)
        shixing = df['shixing'].tolist()
        n = len(ret)
        for j in range(n):
            jy = get_jinyin(shixing[j])
            if jy not in ['金', '银', '唏']: continue
            if ZC[j] <= 0 or AB[j] <= 0: continue  # 方法周A 条件
            cd_key = '金升' if CD[j] > 0 else '银升'
            key = (jy, cd_key)
            s = stats[key]
            s['n'] += 1
            if j+1 < n:
                s['ret'].append(ret[j+1])
                if ret[j+1] > 0: s['win1'] += 1
                if HR[j+1] >= 3: s['hr3'] += 1
            if j+4 < n:
                s['ret4'].append(sum(ret[j+1:j+5]))
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已处理 {i+1}/{len(files)}')

print(f'\n处理完成')

print('\n' + '='*70)
print('方法周A 框架（WXZC>0 + 龙骨WXAB>0）下，金银唏 × 金升/银升 的表现')
print('='*70)
print(f'{"势型":<4}{"金升/银升":<8}{"n":<10}{"下周均值":<10}{"下周涨>0":<10}{"下周HR≥3%":<12}{"未来4周均值":<12}')
for jy in ['金', '银', '唏']:
    for cd in ['金升', '银升']:
        s = stats[(jy, cd)]
        ret = np.array(s['ret'])
        ret4 = np.array(s['ret4'])
        if s['n'] == 0:
            print(f'{jy:<4}{cd:<8}{0:<10}{"-":<10}{"-":<10}{"-":<12}{"-":<12}')
            continue
        print(f'{jy:<4}{cd:<8}{s["n"]:<10}{ret.mean():<10.2f}{(s["win1"]/s["n"]*100):<10.2f}{(s["hr3"]/s["n"]*100):<12.2f}{ret4.mean():<12.2f}')

print('\n' + '='*70)
print('汇总对比：结论A（只做金）vs 结论B（等金升）')
print('='*70)

# 结论A：只做金（金全部）vs 金银唏全部
def agg(keys):
    n = sum(stats[k]['n'] for k in keys)
    ret = []
    ret4 = []
    win1 = 0
    hr3 = 0
    for k in keys:
        s = stats[k]
        ret.extend(s['ret'])
        ret4.extend(s['ret4'])
        win1 += s['win1']
        hr3 += s['hr3']
    return n, np.array(ret), np.array(ret4), win1, hr3

# 只做金
n_jin, ret_jin, ret4_jin, win_jin, hr3_jin = agg([('金','金升'),('金','银升')])
# 金银唏全部
n_all, ret_all, ret4_all, win_all, hr3_all = agg([(j,c) for j in ['金','银','唏'] for c in ['金升','银升']])
# 只做金升
n_jinsheng, ret_jinsheng, ret4_jinsheng, win_js, hr3_js = agg([('金','金升'),('银','金升'),('唏','金升')])
# 金银唏 银升
n_yinsheng, ret_yinsheng, ret4_yinsheng, win_ys, hr3_ys = agg([('金','银升'),('银','银升'),('唏','银升')])

def show(name, n, ret, ret4, win, hr3):
    print(f'\n  {name}（n={n}）:')
    print(f'    下周均值: {ret.mean():.2f}%  下周涨>0: {win/n*100:.2f}%  下周HR≥3%: {hr3/n*100:.2f}%')
    print(f'    未来4周均值: {ret4.mean():.2f}%  未来4周涨>0: {(ret4>0).mean()*100:.2f}%')

print('\n--- 结论A：只做金 vs 金银唏全部 ---')
show('只做金', n_jin, ret_jin, ret4_jin, win_jin, hr3_jin)
show('金银唏全部', n_all, ret_all, ret4_all, win_all, hr3_all)

print('\n--- 结论B：金升（CD>0）vs 银升（CD≤0） ---')
show('金升（CD>0）', n_jinsheng, ret_jinsheng, ret4_jinsheng, win_js, hr3_js)
show('银升（CD≤0）', n_yinsheng, ret_yinsheng, ret4_yinsheng, win_ys, hr3_ys)

print('\n完成')