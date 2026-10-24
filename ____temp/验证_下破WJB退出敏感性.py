# -*- coding: utf-8 -*-
"""
验证：方法周A 退出条件 —— 下破 WJB（WXZB<0）作为退出信号是否过于敏感？
用户困扰：下破 WJB 后并不一定转为虎主跌或下破 WXZC<0，导致过早退出踏空。
提议：将退出条件限定为 WXZC<0 或（WXZC>0 且为虎）。

本脚本回答：
1. 下破 WJB 事件后，未来 N 周内下破 WXZC<0 的比例（真正转坏）
2. 下破 WJB 事件后，未来 N 周内转为虎（WXAB<0 且 WXZB<0）的比例
3. 下破 WJB 事件后，重新站上 WJB（WXZB>0）的比例（假信号/洗盘）
4. 下破 WJB 事件后，未来 N 周内重新站上 WJC（WXZC>0）的比例
"""
import pandas as pd
import numpy as np
import glob
import io

DATA_DIR = '昭明算展/谕组周'
files = glob.glob(f'{DATA_DIR}/谕组周_*.csv')
print(f'共 {len(files)} 个文件')

# 列索引（0-based，见元数据_vba数据映射_周类.md）
COL_DATE = 0
COL_WEEK_RET = 1   # 周涨
COL_HR = 3         # 临高幅
COL_HU = 4         # 护型
COL_ZA = 16        # WXZA
COL_ZB = 17        # WXZB
COL_ZC = 18        # WXZC
COL_AB = 22        # WXAB

def read_file(fp):
    df = pd.read_csv(fp, encoding='gbk', header=0, dtype=str)
    # 只保留需要的列
    keep = [COL_DATE, COL_WEEK_RET, COL_HR, COL_HU, COL_ZA, COL_ZB, COL_ZC, COL_AB]
    df = df.iloc[:, keep]
    df.columns = ['date', 'week_ret', 'HR', 'hu', 'ZA', 'ZB', 'ZC', 'AB']
    # 数值化
    for c in ['week_ret', 'HR', 'ZA', 'ZB', 'ZC', 'AB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['fid'] = fp.split('_')[-1].replace('.csv', '')
    return df

# 读取全部（分批，避免内存过大）
frames = []
for i, fp in enumerate(files):
    try:
        frames.append(read_file(fp))
    except Exception as e:
        print(f'  skip {fp}: {e}')
    if (i+1) % 500 == 0:
        print(f'  已读 {i+1}/{len(files)}')
df = pd.concat(frames, ignore_index=True)
print(f'总行数: {len(df)}')

# 排序（按 fid + date）
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['fid', 'date']).reset_index(drop=True)

# 定义信号
df['ZB_pos'] = df['ZB'] > 0      # 站上 WJB
df['ZC_pos'] = df['ZC'] > 0      # 站上 WJC
df['AB_pos'] = df['AB'] > 0      # WXAB 正交

# 下破 WJB 事件：本周 ZB<=0 且上周 ZB>0
df['prev_ZB_pos'] = df.groupby('fid')['ZB_pos'].shift(1)
df['break_WJB'] = (~df['ZB_pos']) & df['prev_ZB_pos']

# 下破 WJC 事件：本周 ZC<=0 且上周 ZC>0
df['prev_ZC_pos'] = df.groupby('fid')['ZC_pos'].shift(1)
df['break_WJC'] = (~df['ZC_pos']) & df['prev_ZC_pos']

# 虎：WXAB<0 且 WXZB<0
df['is_hu'] = (df['AB'] < 0) & (df['ZB'] < 0)

# 未来 N 周内下破 WXZC<0（用 groupby shift 取未来）
def future_any(col, n):
    """未来 n 周内（含本周）该布尔列是否出现过 True"""
    # 用 rolling 反向：对每个 fid，未来 n 行内是否有 True
    # 方法：反转后 rolling，再反转
    g = df.groupby('fid')[col]
    # 未来 n 行内 any True：用 shift(-k) 累积
    result = pd.Series(False, index=df.index)
    for k in range(0, n+1):
        result = result | g.shift(-k).fillna(False)
    return result

# 未来 N 周内下破 WXZC<0（即未来某周 ZC<=0）
for n in [1, 2, 4, 8, 12]:
    df[f'fut{n}_ZC_neg'] = future_any('ZC_pos', n) == False  # 未来n周内出现ZC<=0
    # 修正：future_any 返回未来n周内 ZC_pos 出现过 True；ZC_neg = 未来n周内出现过 ZC<=0
    # 需要单独算：未来n周内 ZC<=0
    g = df.groupby('fid')['ZC_pos']
    fut_pos = pd.Series(False, index=df.index)
    for k in range(0, n+1):
        fut_pos = fut_pos | g.shift(-k).fillna(False)
    df[f'fut{n}_ZC_neg'] = ~fut_pos

# 未来 N 周内转虎
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['is_hu']
    fut_hu = pd.Series(False, index=df.index)
    for k in range(0, n+1):
        fut_hu = fut_hu | g.shift(-k).fillna(False)
    df[f'fut{n}_hu'] = fut_hu

# 未来 N 周内重新站上 WJB（WXZB>0）
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['ZB_pos']
    fut_zb = pd.Series(False, index=df.index)
    for k in range(0, n+1):
        fut_zb = fut_zb | g.shift(-k).fillna(False)
    df[f'fut{n}_ZB_pos'] = fut_zb

# 未来 N 周内重新站上 WJC（WXZC>0）
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['ZC_pos']
    fut_zc = pd.Series(False, index=df.index)
    for k in range(0, n+1):
        fut_zc = fut_zc | g.shift(-k).fillna(False)
    df[f'fut{n}_ZC_pos'] = fut_zc

# ============ 分析1：下破 WJB 事件后的后续走势 ============
print('\n' + '='*70)
print('分析1：下破 WJB（WXZB 从正转非正）事件后的后续走势')
print('='*70)

ev = df[df['break_WJB']].copy()
print(f'下破 WJB 事件总数: {len(ev)}')

print('\n--- 下破 WJB 后，未来 N 周内下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = ev[f'fut{n}_ZC_neg'].mean() * 100
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {pct:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内转为虎（WXAB<0 且 WXZB<0）的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = ev[f'fut{n}_hu'].mean() * 100
    print(f'  未来 {n:>2} 周内转虎: {pct:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内重新站上 WJB（WXZB>0）的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = ev[f'fut{n}_ZB_pos'].mean() * 100
    print(f'  未来 {n:>2} 周内重新站上 WJB: {pct:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内重新站上 WJC（WXZC>0）的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = ev[f'fut{n}_ZC_pos'].mean() * 100
    print(f'  未来 {n:>2} 周内重新站上 WJC: {pct:.2f}%')

# 下破 WJB 当周的 ZC 状态
print('\n--- 下破 WJB 当周，WXZC 状态分布 ---')
zc_state = ev['ZC'].apply(lambda x: 'ZC>0' if x > 0 else ('ZC=0' if x == 0 else 'ZC<0'))
print(zc_state.value_counts(normalize=True).mul(100).round(2))

# 下破 WJB 当周，是否已转虎
print('\n--- 下破 WJB 当周，是否已为虎（WXAB<0 且 WXZB<0） ---')
print(f'  当周已为虎: {ev["is_hu"].mean()*100:.2f}%')

# ============ 分析2：下破 WJB 当周 ZC>0 的子集（关键！） ============
print('\n' + '='*70)
print('分析2：下破 WJB 但 WXZC>0（尚未下破 WJC）的子集 —— 用户困扰的核心')
print('='*70)
sub = ev[ev['ZC'] > 0].copy()
print(f'下破 WJB 且当周 WXZC>0 的事件数: {len(sub)}（占全部下破WJB的 {len(sub)/len(ev)*100:.1f}%）')

print('\n--- 该子集（下破WJB但ZC>0）未来 N 周内下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub[f'fut{n}_ZC_neg'].mean() * 100
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {pct:.2f}%')

print('\n--- 该子集未来 N 周内转虎的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub[f'fut{n}_hu'].mean() * 100
    print(f'  未来 {n:>2} 周内转虎: {pct:.2f}%')

print('\n--- 该子集未来 N 周内重新站上 WJB 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub[f'fut{n}_ZB_pos'].mean() * 100
    print(f'  未来 {n:>2} 周内重新站上 WJB: {pct:.2f}%')

# 该子集下破 WJB 当周的周涨
print('\n--- 该子集下破 WJB 当周周涨分布 ---')
print(sub['week_ret'].describe().round(2))
print(f'  当周周涨>0: {(sub["week_ret"]>0).mean()*100:.2f}%')

# 该子集下破 WJB 后，未来1周周涨
print('\n--- 该子集下破 WJB 后，未来1周周涨 ---')
sub['next_ret'] = sub.groupby('fid')['week_ret'].shift(-1)
print(sub['next_ret'].describe().round(2))
print(f'  下周周涨>0: {(sub["next_ret"]>0).mean()*100:.2f}%')

# ============ 分析3：下破 WJB 但 ZC>0 且非虎 的子集（用户提议的"不退出"情形） ============
print('\n' + '='*70)
print('分析3：下破 WJB 但（ZC>0 且非虎）的子集 —— 用户提议中"不退出"的情形')
print('='*70)
sub3 = ev[(ev['ZC'] > 0) & (~ev['is_hu'])].copy()
print(f'下破 WJB 且（ZC>0 且非虎）的事件数: {len(sub3)}（占全部下破WJB的 {len(sub3)/len(ev)*100:.1f}%）')

print('\n--- 该子集未来 N 周内下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub3[f'fut{n}_ZC_neg'].mean() * 100
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {pct:.2f}%')

print('\n--- 该子集未来 N 周内转虎的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub3[f'fut{n}_hu'].mean() * 100
    print(f'  未来 {n:>2} 周内转虎: {pct:.2f}%')

print('\n--- 该子集未来 N 周内重新站上 WJB 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    pct = sub3[f'fut{n}_ZB_pos'].mean() * 100
    print(f'  未来 {n:>2} 周内重新站上 WJB: {pct:.2f}%')

# 该子集下破 WJB 后未来1周周涨
sub3['next_ret'] = sub3.groupby('fid')['week_ret'].shift(-1)
print('\n--- 该子集下破 WJB 后，未来1周周涨 ---')
print(sub3['next_ret'].describe().round(2))
print(f'  下周周涨>0: {(sub3["next_ret"]>0).mean()*100:.2f}%')

print('\n完成')