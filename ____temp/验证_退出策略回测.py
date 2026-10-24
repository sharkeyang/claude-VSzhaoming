# -*- coding: utf-8 -*-
"""
策略回测：方法周A 退出条件对比
策略A（当前）：介入后 WXZB<0（下破 WJB）即退出
策略B（提议）：介入后 WXZC<0（下破 WJC）或（WXZC>0 且虎）才退出

介入信号（方法周A）：WXZC 刚转正（0-2）时介入
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
df['prev_ZC_pos'] = df.groupby('fid')['ZC_pos'].shift(1).fillna(False)
df['prev_ZB_pos'] = df.groupby('fid')['ZB_pos'].shift(1).fillna(False)
df['is_hu'] = (df['AB'] < 0) & (df['ZB'] < 0)

# 介入信号：WXZC 刚转正（本周 ZC>0 且上周 ZC<=0），且 ZC 值 0-2（刚突破）
df['entry'] = df['ZC_pos'] & (~df['prev_ZC_pos']) & (df['ZC'] <= 2)

# 策略A退出：WXZB<0（下破 WJB）
df['exit_A'] = ~df['ZB_pos']
# 策略B退出：WXZC<0 或（WXZC>0 且虎）
df['exit_B'] = (~df['ZC_pos']) | (df['ZC_pos'] & df['is_hu'])

# 回测：对每个 fid 模拟持仓
def backtest(g, exit_col):
    """返回该 fid 的持仓收益序列（每笔交易的收益）"""
    trades = []
    holding = False
    entry_ret = 0.0
    for _, r in g.iterrows():
        if not holding:
            if r['entry']:
                holding = True
                entry_ret = r['week_ret']  # 介入当周收益
        else:
            if r[exit_col]:
                # 退出：记录这笔交易收益（介入当周 + 持有期间）
                trades.append(entry_ret)
                holding = False
            else:
                # 继续持有，累加收益
                entry_ret += r['week_ret']
    # 若最后仍持仓，记录（到数据末尾）
    if holding:
        trades.append(entry_ret)
    return trades

# 逐 fid 回测
results = {'A': [], 'B': []}
for fid, g in df.groupby('fid'):
    g = g.reset_index(drop=True)
    results['A'].extend(backtest(g, 'exit_A'))
    results['B'].extend(backtest(g, 'exit_B'))

print('\n' + '='*70)
print('策略回测结果（方法周A 介入，不同退出条件）')
print('='*70)

for name, trades in results.items():
    trades = np.array(trades)
    print(f'\n--- 策略{name}（{"WXZB<0退出" if name=="A" else "WXZC<0或虎退出"}）---')
    print(f'  交易次数: {len(trades)}')
    print(f'  平均每笔收益: {trades.mean():.2f}%')
    print(f'  中位每笔收益: {np.median(trades):.2f}%')
    print(f'  盈利交易占比: {(trades>0).mean()*100:.2f}%')
    print(f'  累计收益(简单加总): {trades.sum():.2f}%')
    # 复利累计
    cum = np.prod(1 + trades/100) - 1
    print(f'  累计收益(复利): {cum*100:.2f}%')
    # 平均持有周数
    print(f'  平均持有周数: {trades.size:.1f}')  # 每笔=1次交易，持有周数需另算

# 平均持有周数
print('\n--- 平均持有周数 ---')
def avg_hold(g, exit_col):
    holds = []
    holding = False
    h = 0
    for _, r in g.iterrows():
        if not holding:
            if r['entry']:
                holding = True
                h = 1
        else:
            if r[exit_col]:
                holds.append(h)
                holding = False
            else:
                h += 1
    if holding:
        holds.append(h)
    return holds

hold_A = []
hold_B = []
for fid, g in df.groupby('fid'):
    g = g.reset_index(drop=True)
    hold_A.extend(avg_hold(g, 'exit_A'))
    hold_B.extend(avg_hold(g, 'exit_B'))
print(f'  策略A 平均持有周数: {np.mean(hold_A):.1f}')
print(f'  策略B 平均持有周数: {np.mean(hold_B):.1f}')

print('\n完成')