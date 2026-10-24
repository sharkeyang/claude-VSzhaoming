# -*- coding: utf-8 -*-
"""
深跌诱多陷阱分析（WJC入口失效场景）
====================================
假设：长时间深跌后（WXCD长期为负），价格在底部反复围绕WJC（EMA26）突破/跌破，
此时WXZC>0（站上WJC）是诱多陷阱——因为中期趋势（WXCD）仍为负，这是下跌趋势中的反弹。

列索引（元数据权威，0-based）：
- 周涨[1]、PR[2]、HR[3]
- WXAB护型[4]、周势型[12]（WXCD护型）
- WXZA[16]、WXZB[17]、WXZC[18]、WXZD[19]、WXZE[20]
- WXAB交叉[22]、WXCD交叉[27]
"""
import pandas as pd
import numpy as np
import glob
import os

DATA_DIR = '昭明算展/谕组周'
COL_WEEK_RET = 1   # 周涨
COL_WXZC = 18      # WXZC（价格 vs WJC=EMA26 交叉天数）
COL_WXCD = 27      # WXCD（JC vs JD 交叉天数）

def load_all():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组周_*.csv')))
    print(f'读取 {len(files)} 个文件...')
    frames = []
    for f in files:
        fid = os.path.basename(f).replace('谕组周_', '').replace('.csv', '')
        df = pd.read_csv(f, encoding='gbk')
        df['fid'] = fid
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    print(f'总行数: {len(data)}')
    return data

def main():
    data = load_all()
    # 按 fid + 日期排序
    data = data.sort_values(['fid', data.columns[0]]).reset_index(drop=True)

    zc = data.iloc[:, COL_WXZC].astype(int)
    cd = data.iloc[:, COL_WXCD].astype(int)
    ret = data.iloc[:, COL_WEEK_RET].astype(float)
    # 列名（GBK 中文，用位置取列名）
    COL_RET_NAME = data.columns[COL_WEEK_RET]
    COL_ZC_NAME = data.columns[COL_WXZC]
    COL_CD_NAME = data.columns[COL_WXCD]
    g = data.groupby('fid')

    # 1. WXCD<0 连续 run（按 fid）
    cd_neg = (cd < 0).astype(int)
    data['_cd_neg'] = cd_neg
    data['_grp'] = (data['fid'] != data['fid'].shift()) | (data['_cd_neg'] != data['_cd_neg'].shift())
    data['_grp_id'] = data['_grp'].cumsum()
    data['_cd_neg_run'] = data.groupby('_grp_id')['_cd_neg'].transform('sum')

    # 2. 站上 WJC 事件：WXZC 由 <=0 转 >0
    data['_zc_pos'] = (zc > 0).astype(int)
    prev_zc_pos = g['_zc_pos'].shift(1).fillna(0)
    data['_break'] = ((data['_zc_pos'] == 1) & (prev_zc_pos == 0)).astype(int)

    # 3. 未来 k 周内是否跌破（zc_pos 变 0）
    def future_neg_any(col, k):
        result = pd.Series(False, index=data.index)
        for i in range(1, k + 1):
            shifted = g[col].shift(-i)
            result = result | (shifted == 0)
        return result

    data['_trap_4w'] = future_neg_any('_zc_pos', 4)
    data['_trap_8w'] = future_neg_any('_zc_pos', 8)

    # 4. 未来 4 周收益（shift(-1)~shift(-4) 求和）与最高
    ret_shift1 = g[COL_RET_NAME].shift(-1)
    ret_shift2 = g[COL_RET_NAME].shift(-2)
    ret_shift3 = g[COL_RET_NAME].shift(-3)
    ret_shift4 = g[COL_RET_NAME].shift(-4)
    data['_ret_4w'] = (ret_shift1 + ret_shift2 + ret_shift3 + ret_shift4)
    data['_ret_4w_max'] = pd.concat([ret_shift1, ret_shift2, ret_shift3, ret_shift4], axis=1).max(axis=1)

    # 5. 深跌阈值探索
    events = data[data['_break'] == 1].copy()
    print(f'\n总突破事件数: {len(events)}')

    print('\n=== WXCD<0 连续周数分布（全量，按股票最大连续为负）===')
    max_run = data[data['_cd_neg'] == 1].groupby('fid')['_cd_neg_run'].max()
    print(max_run.describe())
    for th in [4, 8, 12, 16, 20, 26, 30]:
        print(f'  连续为负 >= {th}周 的股票数: {(max_run >= th).sum()}')

    print('\n=== 深跌 vs 正常 站上WJC 后续表现 ===')
    print(f"{'N':>3} {'组别':<6} {'事件数':>8} {'4周内转负%':>10} {'8周内转负%':>10} {'4周均收益%':>10} {'4周最高均%':>10}")
    for N in [4, 8, 12, 16, 20, 26, 30]:
        deep_mask = (events['_cd_neg_run'] >= N) & (events.iloc[:, COL_WXCD].astype(int) < 0)
        normal_mask = ~deep_mask
        for label, mask in [('深跌', deep_mask), ('正常', normal_mask)]:
            ev = events[mask]
            n = len(ev)
            if n == 0:
                continue
            trap4 = ev['_trap_4w'].mean() * 100
            trap8 = ev['_trap_8w'].mean() * 100
            # _ret_4w 已是百分比数值（如 1.136 表示 1.136%），直接显示
            avg_ret4 = ev['_ret_4w'].mean()
            avg_ret4max = ev['_ret_4w_max'].mean()
            print(f"{N:>3} {label:<6} {n:>8} {trap4:>10.2f} {trap8:>10.2f} {avg_ret4:>10.3f} {avg_ret4max:>10.3f}")

    # 6. 反复突破次数 vs 诱多
    print('\n=== 深跌期间反复突破次数 vs 诱多陷阱率 ===')
    deep_runs = data[data['_cd_neg'] == 1].copy()
    break_in_run = deep_runs.groupby('_grp_id')['_break'].sum()
    first_break_in_run = deep_runs[deep_runs['_break'] == 1].groupby('_grp_id').first()
    first_break_in_run['_n_break'] = break_in_run
    print(f"{'run内突破次数':>10} {'run数':>8} {'首次突破后4周转负%':>18}")
    for nb in sorted(first_break_in_run['_n_break'].unique()):
        sub = first_break_in_run[first_break_in_run['_n_break'] == nb]
        n = len(sub)
        if n < 10:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        print(f"{nb:>10} {n:>8} {trap4:>18.2f}")

    # 7. 价格深度（前8周WXZC最小值）vs 诱多
    print('\n=== 价格深度（前8周WXZC最小值）vs 诱多陷阱率 ===')
    # 前 8 周内 WXZC 最小值（负值越大 = 价格越深低于 WJC）
    zc_min_prev8 = g[COL_ZC_NAME].rolling(8, min_periods=1).min().shift(1).reset_index(level=0, drop=True)
    data['_zc_min_prev8'] = zc_min_prev8
    events = data[data['_break'] == 1].copy()
    # 按价格深度分层
    bins = [-999, -30, -20, -10, -5, 0]
    labels = ['<-30', '-30~-20', '-20~-10', '-10~-5', '-5~0']
    events['_depth_bin'] = pd.cut(events['_zc_min_prev8'], bins=bins, labels=labels)
    print(f"{'价格深度':>10} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10} {'4周最高均%':>10}")
    for lb in labels:
        sub = events[events['_depth_bin'] == lb]
        n = len(sub)
        if n < 10:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        avg_ret4max = sub['_ret_4w_max'].mean()
        print(f"{lb:>10} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f} {avg_ret4max:>10.3f}")

    # 保存结果
    out = '____temp/_深跌诱多陷阱结果.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('=== WXCD<0 连续周数分布（全量，按股票最大连续为负）===\n')
        f.write(str(max_run.describe()) + '\n')
        for th in [4, 8, 12, 16, 20, 26, 30]:
            f.write(f'  连续为负 >= {th}周 的股票数: {(max_run >= th).sum()}\n')
        f.write('\n=== 深跌 vs 正常 站上WJC 后续表现 ===\n')
        f.write(f"{'N':>3} {'组别':<6} {'事件数':>8} {'4周内转负%':>10} {'8周内转负%':>10} {'4周均收益%':>10} {'4周最高均%':>10}\n")
        for N in [4, 8, 12, 16, 20, 26, 30]:
            deep_mask = (events['_cd_neg_run'] >= N) & (events.iloc[:, COL_WXCD].astype(int) < 0)
            normal_mask = ~deep_mask
            for label, mask in [('深跌', deep_mask), ('正常', normal_mask)]:
                ev = events[mask]
                n = len(ev)
                if n == 0:
                    continue
                trap4 = ev['_trap_4w'].mean() * 100
                trap8 = ev['_trap_8w'].mean() * 100
                avg_ret4 = ev['_ret_4w'].mean()
                avg_ret4max = ev['_ret_4w_max'].mean()
                f.write(f"{N:>3} {label:<6} {n:>8} {trap4:>10.2f} {trap8:>10.2f} {avg_ret4:>10.3f} {avg_ret4max:>10.3f}\n")
        f.write('\n=== 深跌期间反复突破次数 vs 诱多陷阱率 ===\n')
        f.write(f"{'run内突破次数':>10} {'run数':>8} {'首次突破后4周转负%':>18}\n")
        for nb in sorted(first_break_in_run['_n_break'].unique()):
            sub = first_break_in_run[first_break_in_run['_n_break'] == nb]
            n = len(sub)
            if n < 10:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            f.write(f"{nb:>10} {n:>8} {trap4:>18.2f}\n")
        f.write('\n=== 价格深度（前8周WXZC最小值）vs 诱多陷阱率 ===\n')
        f.write(f"{'价格深度':>10} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10} {'4周最高均%':>10}\n")
        for lb in labels:
            sub = events[events['_depth_bin'] == lb]
            n = len(sub)
            if n < 10:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            avg_ret4max = sub['_ret_4w_max'].mean()
            f.write(f"{lb:>10} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f} {avg_ret4max:>10.3f}\n")
    print(f'\n结果已保存到 {out}')

if __name__ == '__main__':
    main()
