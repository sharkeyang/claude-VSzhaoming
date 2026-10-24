# -*- coding: utf-8 -*-
"""
验证：方法周A 退出条件 —— 下破 WJB（WXZB<0）作为退出信号是否过于敏感？
用户提议：将退出条件限定为 WXZC<0 或（WXZC>0 且为虎）。

本脚本（修正版）：
1. 下破 WJB 事件后，未来 N 周内（不含当周）下破 WXZC<0 的比例
2. 下破 WJB 事件后，未来 N 周内（不含当周）转虎的比例
3. 下破 WJB 事件后，未来 N 周内重新站上 WJB 的比例
4. 下破 WJB 事件后，未来 N 周内重新站上 WJC 的比例
5. 下破 WJB 事件后，未来 1/2/4 周的实际周涨（关键：是否值得继续持有）
6. 策略对比：策略A（WXZB<0 退出）vs 策略B（WXZC<0 或虎退出）
"""
import pandas as pd
import numpy as np
import glob
import io

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
    df['fid'] = fp.split('_')[-1].replace('.csv', '')
    return df

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

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['fid', 'date']).reset_index(drop=True)

df['ZB_pos'] = df['ZB'] > 0
df['ZC_pos'] = df['ZC'] > 0
df['AB_pos'] = df['AB'] > 0
df['prev_ZB_pos'] = df.groupby('fid')['ZB_pos'].shift(1)
df['break_WJB'] = (~df['ZB_pos']) & df['prev_ZB_pos']
df['is_hu'] = (df['AB'] < 0) & (df['ZB'] < 0)

# 未来 k 周（不含当周）的布尔列是否出现过 True
def future_any_excl(col, n):
    """未来 1..n 周（不含当周）内该布尔列是否出现过 True"""
    g = df.groupby('fid')[col]
    result = pd.Series(False, index=df.index)
    for k in range(1, n+1):
        result = result | g.shift(-k).fillna(False)
    return result

# 未来 k 周（不含当周）ZC<=0
for n in [1, 2, 4, 8, 12]:
    df[f'fut{n}_ZC_neg'] = future_any_excl('ZC_pos', n) == False
    # 注意：future_any_excl 返回未来1..n周内 ZC_pos 出现过 True；ZC_neg = 未来1..n周内出现过 ZC<=0
    # 但若未来某周 ZC_pos 为 NaN（数据末尾），shift 后 fillna(False) 会误判为 ZC_neg
    # 需排除：未来1..n周内 ZC_pos 出现过 True 才算"未下破"
    # 修正：ZC_neg = 未来1..n周内 ZC_pos 从未为 True（且未来有数据）
    g = df.groupby('fid')['ZC_pos']
    fut_pos = pd.Series(False, index=df.index)
    for k in range(1, n+1):
        fut_pos = fut_pos | g.shift(-k).fillna(False)
    df[f'fut{n}_ZC_neg'] = ~fut_pos

# 未来 k 周（不含当周）转虎
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['is_hu']
    fut_hu = pd.Series(False, index=df.index)
    for k in range(1, n+1):
        fut_hu = fut_hu | g.shift(-k).fillna(False)
    df[f'fut{n}_hu'] = fut_hu

# 未来 k 周（不含当周）重新站上 WJB
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['ZB_pos']
    fut_zb = pd.Series(False, index=df.index)
    for k in range(1, n+1):
        fut_zb = fut_zb | g.shift(-k).fillna(False)
    df[f'fut{n}_ZB_pos'] = fut_zb

# 未来 k 周（不含当周）重新站上 WJC
for n in [1, 2, 4, 8, 12]:
    g = df.groupby('fid')['ZC_pos']
    fut_zc = pd.Series(False, index=df.index)
    for k in range(1, n+1):
        fut_zc = fut_zc | g.shift(-k).fillna(False)
    df[f'fut{n}_ZC_pos'] = fut_zc

# 未来 1/2/4 周累计周涨（不含当周）
for n in [1, 2, 4]:
    g = df.groupby('fid')['week_ret']
    cum = pd.Series(0.0, index=df.index)
    for k in range(1, n+1):
        cum = cum + g.shift(-k).fillna(0)
    df[f'fut{n}_cumret'] = cum

# ============ 分析1：全部下破 WJB 事件 ============
print('\n' + '='*70)
print('分析1：下破 WJB（WXZB 从正转非正）事件后的后续走势（不含当周）')
print('='*70)
ev = df[df['break_WJB']].copy()
print(f'下破 WJB 事件总数: {len(ev)}')

print('\n--- 下破 WJB 后，未来 N 周内（不含当周）下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {ev[f"fut{n}_ZC_neg"].mean()*100:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内（不含当周）转虎的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内转虎: {ev[f"fut{n}_hu"].mean()*100:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内（不含当周）重新站上 WJB 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内重新站上 WJB: {ev[f"fut{n}_ZB_pos"].mean()*100:.2f}%')

print('\n--- 下破 WJB 后，未来 N 周内（不含当周）重新站上 WJC 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内重新站上 WJC: {ev[f"fut{n}_ZC_pos"].mean()*100:.2f}%')

print('\n--- 下破 WJB 后，未来 1/2/4 周累计周涨 ---')
for n in [1, 2, 4]:
    print(f'  未来{n}周累计周涨: 均值 {ev[f"fut{n}_cumret"].mean():.2f}%  中位 {ev[f"fut{n}_cumret"].median():.2f}%  正收益 {(ev[f"fut{n}_cumret"]>0).mean()*100:.2f}%')

print('\n--- 下破 WJB 当周，WXZC 状态分布 ---')
zc_state = ev['ZC'].apply(lambda x: 'ZC>0' if x > 0 else ('ZC=0' if x == 0 else 'ZC<0'))
print(zc_state.value_counts(normalize=True).mul(100).round(2))

print('\n--- 下破 WJB 当周，是否已为虎 ---')
print(f'  当周已为虎: {ev["is_hu"].mean()*100:.2f}%')

# ============ 分析2：下破 WJB 但当周 ZC>0 的子集 ============
print('\n' + '='*70)
print('分析2：下破 WJB 但当周 WXZC>0（尚未下破 WJC）的子集')
print('='*70)
sub = ev[ev['ZC'] > 0].copy()
print(f'下破 WJB 且当周 WXZC>0 的事件数: {len(sub)}（占全部下破WJB的 {len(sub)/len(ev)*100:.1f}%）')

print('\n--- 该子集未来 N 周内（不含当周）下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {sub[f"fut{n}_ZC_neg"].mean()*100:.2f}%')

print('\n--- 该子集未来 N 周内（不含当周）转虎的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内转虎: {sub[f"fut{n}_hu"].mean()*100:.2f}%')

print('\n--- 该子集未来 N 周内（不含当周）重新站上 WJB 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内重新站上 WJB: {sub[f"fut{n}_ZB_pos"].mean()*100:.2f}%')

print('\n--- 该子集未来 N 周内（不含当周）重新站上 WJC 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内重新站上 WJC: {sub[f"fut{n}_ZC_pos"].mean()*100:.2f}%')

print('\n--- 该子集未来 1/2/4 周累计周涨 ---')
for n in [1, 2, 4]:
    print(f'  未来{n}周累计周涨: 均值 {sub[f"fut{n}_cumret"].mean():.2f}%  中位 {sub[f"fut{n}_cumret"].median():.2f}%  正收益 {(sub[f"fut{n}_cumret"]>0).mean()*100:.2f}%')

print('\n--- 该子集下破 WJB 当周周涨 ---')
print(f'  当周周涨均值: {sub["week_ret"].mean():.2f}%  周涨>0: {(sub["week_ret"]>0).mean()*100:.2f}%')

# ============ 分析3：下破 WJB 且（ZC>0 且非虎）的子集 ============
print('\n' + '='*70)
print('分析3：下破 WJB 且（ZC>0 且非虎）的子集 —— 用户提议中"不退出"的情形')
print('='*70)
sub3 = ev[(ev['ZC'] > 0) & (~ev['is_hu'])].copy()
print(f'下破 WJB 且（ZC>0 且非虎）的事件数: {len(sub3)}（占全部下破WJB的 {len(sub3)/len(ev)*100:.1f}%）')

print('\n--- 该子集未来 N 周内（不含当周）下破 WXZC<0 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内下破 WXZC<0: {sub3[f"fut{n}_ZC_neg"].mean()*100:.2f}%')

print('\n--- 该子集未来 N 周内（不含当周）转虎的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内转虎: {sub3[f"fut{n}_hu"].mean()*100:.2f}%')

print('\n--- 该子集未来 N 周内（不含当周）重新站上 WJB 的比例 ---')
for n in [1, 2, 4, 8, 12]:
    print(f'  未来 {n:>2} 周内重新站上 WJB: {sub3[f"fut{n}_ZB_pos"].mean()*100:.2f}%')

print('\n--- 该子集未来 1/2/4 周累计周涨 ---')
for n in [1, 2, 4]:
    print(f'  未来{n}周累计周涨: 均值 {sub3[f"fut{n}_cumret"].mean():.2f}%  中位 {sub3[f"fut{n}_cumret"].median():.2f}%  正收益 {(sub3[f"fut{n}_cumret"]>0).mean()*100:.2f}%')

print('\n--- 该子集下破 WJB 当周周涨 ---')
print(f'  当周周涨均值: {sub3["week_ret"].mean():.2f}%  周涨>0: {(sub3["week_ret"]>0).mean()*100:.2f}%')

print('\n完成')