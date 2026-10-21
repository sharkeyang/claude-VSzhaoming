# -*- coding: utf-8 -*-
"""龙头交/龙头返/龙震芽/龙震根 是否适合周日联合备选 + 是否易诱多 —— 新编码精确验证
数据：谕组周 CSV（2026-10-13 导出，新编码 Ca龙头交/Cb龙头返/Bd龙震芽/Be龙震根）
列（元数据表权威）：波型[7]、ZA周[16]、ZB周[17]、ZC周[18]、AB周[22]、HR[3]、PR[2]、护型[4]
口径：只统计 WXZC>0（周日联合备选前提，与神谕.bas 日漏筛选一致）
下周数据：groupby(fid) shift(-1)（memory 教训：跑下周分析必须用 shift(-1)）
"""
import sys, glob, os
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

# 列索引（元数据表权威）
COLS = {0: '日期', 3: 'HR', 2: 'PR', 4: '护型', 7: '波型', 16: 'ZA', 17: 'ZB', 18: 'ZC', 22: 'AB'}

# 目标波型（新编码）
TARGETS = {
    'Ca龙头交': '龙头交',
    'Cb龙头返': '龙头返',
    'Bd龙震芽': '龙震芽',
    'Be龙震根': '龙震根',
}

files = sorted(glob.glob('谕组周/谕组周_*.csv'))
print(f'共 {len(files)} 个文件', file=sys.stderr)

# 收集所有样本（含 fid 用于 shift）
frames = []
for fi, f in enumerate(files):
    fid = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
    df = pd.read_csv(f, encoding='gbk', usecols=list(COLS.keys()))
    # usecols 返回顺序不保证，按位置重命名
    df.columns = [COLS[i] for i in sorted(COLS.keys())]
    df['fid'] = fid
    frames.append(df)
    if (fi + 1) % 500 == 0:
        print(f'  已读 {fi+1} 文件', file=sys.stderr)

data = pd.concat(frames, ignore_index=True)
print(f'总行数: {len(data)}', file=sys.stderr)

# 数值转换
for c in ['HR', 'PR', 'ZA', 'ZB', 'ZC', 'AB']:
    data[c] = pd.to_numeric(data[c], errors='coerce')

# 下周数据（groupby fid shift(-1)）
data['next_HR'] = data.groupby('fid')['HR'].shift(-1)
data['next_ZA'] = data.groupby('fid')['ZA'].shift(-1)
data['next_涨'] = data.groupby('fid')['PR'].shift(-1)

# 只统计 WXZC>0（周日联合备选前提）
d = data[data['ZC'] > 0].copy()
print(f'WXZC>0 样本: {len(d)}', file=sys.stderr)

# 波型匹配（取 . 前部分）
d['波型名'] = d['波型'].astype(str).str.split('.').str[0]

# 基线
base_n = len(d)
base_p3 = (d['next_HR'] >= 3).sum()
base_hr = d['next_HR'].mean()
base_涨 = (d['next_涨'] > 0).sum()
base_za13 = ((d['ZA'] > 0) & (d['ZA'] <= 3)).sum()
base_za13_nextneg = (((d['ZA'] > 0) & (d['ZA'] <= 3)) & (d['next_ZA'] < 0)).sum()
base_nextneg = (d['next_ZA'] < 0).sum()

print(f'\n{"="*70}')
print(f'基线（WXZC>0 全量，n={base_n}）')
print(f'  下周P3(HR≥3%): {base_p3/base_n*100:.2f}%')
print(f'  下周均HR: {base_hr:.2f}%')
print(f'  下周涨>0: {base_涨/base_n*100:.2f}%')
print(f'  0<ZA≤3比例: {base_za13/base_n*100:.2f}%')
print(f'  下周ZA<0比例: {base_nextneg/base_n*100:.2f}%')
print(f'  诱多率(0<ZA≤3且下周ZA<0, 分母=全量): {base_za13_nextneg/base_n*100:.2f}%')
print(f'  诱多率(0<ZA≤3且下周ZA<0, 分母=0<ZA≤3): {base_za13_nextneg/base_za13*100:.2f}%')

print(f'\n{"="*70}')
print(f'四个波型（WXZC>0 内）')
print(f'{"波型":<8}{"n":>8}{"下周P3":>9}{"下周均HR":>10}{"下周涨>0":>10}{"0<ZA≤3":>9}{"下周ZA<0":>10}{"诱多率(全)":>11}{"诱多率(ZA13)":>13}')
for code, label in TARGETS.items():
    s = d[d['波型名'] == code]
    n = len(s)
    if n == 0:
        print(f'{label:<8}{n:>8}  无样本')
        continue
    p3 = (s['next_HR'] >= 3).sum() / n * 100
    hr = s['next_HR'].mean()
    up = (s['next_涨'] > 0).sum() / n * 100
    za13 = ((s['ZA'] > 0) & (s['ZA'] <= 3)).sum() / n * 100
    nextneg = (s['next_ZA'] < 0).sum() / n * 100
    youduo_all = (((s['ZA'] > 0) & (s['ZA'] <= 3)) & (s['next_ZA'] < 0)).sum() / n * 100
    za13_n = ((s['ZA'] > 0) & (s['ZA'] <= 3)).sum()
    youduo_za13 = (((s['ZA'] > 0) & (s['ZA'] <= 3)) & (s['next_ZA'] < 0)).sum() / za13_n * 100 if za13_n else 0
    print(f'{label:<8}{n:>8}{p3:>8.2f}%{hr:>9.2f}%{up:>9.2f}%{za13:>8.2f}%{nextneg:>9.2f}%{youduo_all:>10.2f}%{youduo_za13:>12.2f}%')

print(f'\n{"="*70}')
print(f'诱多判定（0<ZA≤3 且 下周ZA<0 = 下破WJA）—— 与神谕.bas 注释对照')
print(f'神谕.bas 2747: 龙震芽 0<ZA≤3 占 86.98%，诱多风险高')
print(f'神谕.bas 2744: 龙震根/龙头返 下周ZA<0 高达 57-71%')
print(f'神谕.bas 2754: 龙头交 价值弱 51.49%')
print(f'神谕.bas 2742: 龙扩根 下周ZA<0 高达 75%')
