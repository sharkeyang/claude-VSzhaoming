# -*- coding: utf-8 -*-
"""
方法日B趋(6.1) 完整策略模拟：DJC丘策略必赢验证
================================================
模拟完整策略：
1. 周A/周B满足（周级别进入主升）后，进入可交易状态
2. DJC入口介入：DXZC>0时介入（DJC丘内）
3. DJC止盈：DXZC<0时退出
4. 空仓等待下一个DJC丘

统计：整个策略的累计收益、正收益占比、跑赢基准概率
对比：始终持有（不看日类）vs DJC丘策略
"""
import pandas as pd
import numpy as np
import glob
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组日'
NEED_COLS = [0, 1, 5, 6, 13, 14, 26, 27, 28, 66, 73, 80, 85, 86, 87, 91]

def load_all():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'读取 {len(files)} 个文件...', flush=True)
    frames = []
    for i, f in enumerate(files):
        fid = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        df = pd.read_csv(f, encoding='gbk', usecols=NEED_COLS, low_memory=False)
        df['fid'] = fid
        frames.append(df)
        if (i+1) % 500 == 0:
            print(f'  已读 {i+1}/{len(files)}', flush=True)
    data = pd.concat(frames, ignore_index=True)
    print(f'总行数: {len(data)}', flush=True)
    return data

def main():
    data = load_all()
    data = data.sort_values(['fid', '日期']).reset_index(drop=True)
    g = data.groupby('fid')

    ret = data['涨幅'].astype(float)
    za = data['日ZA'].astype(float)
    zc = data['日ZC'].astype(float)
    zb = data['DTZB'].astype(float)
    next_hr = data['次日高幅'].astype(float)
    wza = data['周ZA'].astype(float)
    wzb = data['周ZB'].astype(float)
    wzc = data['周ZC'].astype(float)
    wab = data['周AB'].astype(float)

    # 周层界首位
    wjie = data['周层界'].astype(str)
    data['_wjie_first'] = wjie.apply(lambda s: s[1:] if s.startswith('_') else s).str[0]
    prev_wjie = g['_wjie_first'].shift(1)
    data['_prev_wjie'] = prev_wjie
    data['_enter_main'] = ((data['_wjie_first'] == '主') & (prev_wjie != '主')).astype(int)
    data['_path'] = ''
    data.loc[(data['_enter_main'] == 1) & (prev_wjie.isin(['初', '储'])), '_path'] = 'A'
    data.loc[(data['_enter_main'] == 1) & (prev_wjie == '再'), '_path'] = 'B'
    data['_in_main'] = (data['_wjie_first'] == '主').astype(int)

    # ============================================================
    # 完整策略模拟
    # ============================================================
    print('='*80)
    print('【方法日B趋 6.1】完整DJC丘策略模拟')
    print('='*80)

    # 对每个fid，模拟策略
    # 状态机：空仓(0) -> 介入(DXZC>0且周A/周B满足) -> 持有 -> 退出(DXZC<0)
    # 周A/周B满足 = 进入主升后（_in_main=1）
    # 但周A/周B是"进入主升"事件，不是持续状态。
    # 简化：周A/周B满足 = 进入主升后持有（_in_main=1）

    # 策略1：DJC丘策略（周A/周B满足 + DJC丘内介入 + DJC止盈）
    # 策略2：始终持有（周A/周B满足后一直持有，不看日类）
    # 策略3：周类出口（周A/周B满足 + WXZC<0退出）

    # 对每个fid，模拟
    strat_djc = []  # (fid, 累计收益, 交易次数, 正收益交易数)
    strat_hold = []  # (fid, 累计收益)
    strat_wzc = []  # (fid, 累计收益)

    for fid, sub in data.groupby('fid'):
        sub = sub.reset_index(drop=True)
        n = len(sub)
        ret_arr = sub['涨幅'].astype(float).values
        zc_arr = sub['日ZC'].astype(float).values
        wzc_arr = sub['周ZC'].astype(float).values
        in_main = sub['_in_main'].values
        path_arr = sub['_path'].values

        # 策略1：DJC丘策略
        # 状态：0=空仓, 1=持有
        state = 0
        cum = 0.0
        trades = 0
        pos_trades = 0
        for i in range(n):
            if state == 0:
                # 空仓：周A/周B满足（进入主升后）且DXZC>0时介入
                if in_main[i] == 1 and zc_arr[i] > 0:
                    state = 1
                    entry_price = 1.0  # 基准
                    cum_entry = cum
            else:
                # 持有：累计当日收益
                cum += ret_arr[i]
                # DJC止盈：DXZC<0时退出
                if zc_arr[i] < 0:
                    state = 0
                    trades += 1
                    if cum - cum_entry > 0:
                        pos_trades += 1
        # 结束：如果还在持有，结算
        if state == 1:
            trades += 1
            if cum - cum_entry > 0:
                pos_trades += 1
        strat_djc.append((fid, cum, trades, pos_trades))

        # 策略2：始终持有（周A/周B满足后一直持有）
        cum2 = 0.0
        holding = False
        for i in range(n):
            if in_main[i] == 1:
                holding = True
            if holding:
                cum2 += ret_arr[i]
        strat_hold.append((fid, cum2))

        # 策略3：周类出口（WXZC<0退出）
        cum3 = 0.0
        holding3 = False
        for i in range(n):
            if in_main[i] == 1:
                holding3 = True
            if holding3:
                cum3 += ret_arr[i]
                if wzc_arr[i] < 0:
                    holding3 = False
        strat_wzc.append((fid, cum3))

    # 汇总
    df_djc = pd.DataFrame(strat_djc, columns=['fid', 'cum', 'trades', 'pos_trades'])
    df_hold = pd.DataFrame(strat_hold, columns=['fid', 'cum'])
    df_wzc = pd.DataFrame(strat_wzc, columns=['fid', 'cum'])

    print(f'\n股票数: {len(df_djc)}')
    print(f'\n--- 策略累计收益对比 ---')
    print(f"{'策略':<20} {'股票数':>8} {'均累计收益%':>10} {'正收益股票占比%':>14} {'均交易次数':>10} {'正收益交易占比%':>14}")
    print(f"{'DJC丘策略':<20} {len(df_djc):>8} {df_djc['cum'].mean():>10.3f} {(df_djc['cum']>0).mean()*100:>13.1f}% {df_djc['trades'].mean():>10.1f} {df_djc['pos_trades'].sum()/df_djc['trades'].sum()*100:>13.1f}%")
    print(f"{'始终持有':<20} {len(df_hold):>8} {df_hold['cum'].mean():>10.3f} {(df_hold['cum']>0).mean()*100:>13.1f}%")
    print(f"{'周类出口':<20} {len(df_wzc):>8} {df_wzc['cum'].mean():>10.3f} {(df_wzc['cum']>0).mean()*100:>13.1f}%")

    # DJC丘策略 vs 始终持有 对比
    print(f'\n--- DJC丘策略 vs 始终持有 ---')
    merged = df_djc.merge(df_hold, on='fid', suffixes=('_djc', '_hold'))
    merged = merged.merge(df_wzc, on='fid')
    merged.columns = ['fid', 'cum_djc', 'trades', 'pos_trades', 'cum_hold', 'cum_wzc']
    # DJC丘策略跑赢始终持有的比例
    beat_hold = (merged['cum_djc'] > merged['cum_hold']).mean() * 100
    beat_wzc = (merged['cum_djc'] > merged['cum_wzc']).mean() * 100
    print(f'DJC丘策略跑赢始终持有: {beat_hold:.1f}%')
    print(f'DJC丘策略跑赢周类出口: {beat_wzc:.1f}%')
    print(f'DJC丘策略均累计: {merged["cum_djc"].mean():.3f}% vs 始终持有: {merged["cum_hold"].mean():.3f}% vs 周类出口: {merged["cum_wzc"].mean():.3f}%')

    # 必赢验证：DJC丘策略累计收益为正的股票占比
    print(f'\n--- 必赢验证 ---')
    print(f'DJC丘策略累计收益>0的股票占比: {(merged["cum_djc"]>0).mean()*100:.1f}%')
    print(f'DJC丘策略累计收益<0的股票占比: {(merged["cum_djc"]<0).mean()*100:.1f}%')
    print(f'始终持有累计收益>0的股票占比: {(merged["cum_hold"]>0).mean()*100:.1f}%')
    print(f'周类出口累计收益>0的股票占比: {(merged["cum_wzc"]>0).mean()*100:.1f}%')

    # 交易次数分布
    print(f'\n--- DJC丘策略交易次数分布 ---')
    print(f'均交易次数: {merged["trades"].mean():.1f}')
    print(f'交易次数>0的股票: {(merged["trades"]>0).mean()*100:.1f}%')
    print(f'交易次数=0的股票: {(merged["trades"]==0).mean()*100:.1f}%')

    print('\n完成')

if __name__ == '__main__':
    main()