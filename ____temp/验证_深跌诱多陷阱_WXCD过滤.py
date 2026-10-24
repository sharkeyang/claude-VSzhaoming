# -*- coding: utf-8 -*-
"""
深跌诱多陷阱 — WXCD 过滤验证（v2）
=====================================
核心问题：WXZC 由负转正（站上 WJC）时，能否靠 WXCD 验证过滤诱多陷阱？
用户假设：WXAB 由负转正、WXZC 由负转正时，沿 WJA 柱排列（WXZA>0）可能是真突破。

关键对比：
- 深跌 run 内 WXZC 转正（WXCD 仍为负）→ 诱多陷阱？
- 深跌 run 结束后 WXZC 转正（WXCD 已转正）→ 真突破？
- 沿 WJA（WXZA>0）+ WXAB 转正 作为过滤条件的效果

列索引（元数据权威，0-based）：
- 周涨[1]、PR[2]、HR[3]
- WXZA[16]、WXZB[17]、WXZC[18]、WXZD[19]、WXZE[20]
- WXAB[22]、WXCD[27]
"""
import pandas as pd
import numpy as np
import glob
import os

DATA_DIR = '昭明算展/谕组周'
COL_WEEK_RET = 1   # 周涨
COL_WXZA = 16      # WXZA（价格 vs WJA=EMA5）
COL_WXZC = 18      # WXZC（价格 vs WJC=EMA26）
COL_WXAB = 22      # WXAB（JA vs JB）
COL_WXCD = 27      # WXCD（JC vs JD）

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
    data = data.sort_values(['fid', data.columns[0]]).reset_index(drop=True)

    za = data.iloc[:, COL_WXZA].astype(int)
    zc = data.iloc[:, COL_WXZC].astype(int)
    ab = data.iloc[:, COL_WXAB].astype(int)
    cd = data.iloc[:, COL_WXCD].astype(int)
    ret = data.iloc[:, COL_WEEK_RET].astype(float)
    g = data.groupby('fid')

    COL_ZA_NAME = data.columns[COL_WXZA]
    COL_ZC_NAME = data.columns[COL_WXZC]
    COL_AB_NAME = data.columns[COL_WXAB]
    COL_CD_NAME = data.columns[COL_WXCD]
    COL_RET_NAME = data.columns[COL_WEEK_RET]

    # 1. WXCD<0 连续 run（深跌深度）
    cd_neg = (cd < 0).astype(int)
    data['_cd_neg'] = cd_neg
    data['_grp'] = (data['fid'] != data['fid'].shift()) | (data['_cd_neg'] != data['_cd_neg'].shift())
    data['_grp_id'] = data['_grp'].cumsum()
    data['_cd_neg_run'] = data.groupby('_grp_id')['_cd_neg'].transform('sum')

    # 2. 历史最大 _cd_neg_run（标记是否经历过深跌）
    data['_cd_neg_run_max'] = data.groupby('fid')['_cd_neg_run'].cummax()

    # 3. WXZC 由负转正事件（站上 WJC）
    data['_zc_pos'] = (zc > 0).astype(int)
    prev_zc_pos = g['_zc_pos'].shift(1).fillna(0)
    data['_break'] = ((data['_zc_pos'] == 1) & (prev_zc_pos == 0)).astype(int)

    # 4. WXCD 由负转正事件（JC 上穿 JD）
    data['_cd_pos'] = (cd > 0).astype(int)
    prev_cd_pos = g['_cd_pos'].shift(1).fillna(0)
    data['_cd_turn'] = ((data['_cd_pos'] == 1) & (prev_cd_pos == 0)).astype(int)

    # 5. WXAB 由负转正事件（JA 上穿 JB）
    data['_ab_pos'] = (ab > 0).astype(int)
    prev_ab_pos = g['_ab_pos'].shift(1).fillna(0)
    data['_ab_turn'] = ((data['_ab_pos'] == 1) & (prev_ab_pos == 0)).astype(int)

    # 6. 未来 4 周内跌破 WXZC<0（诱多陷阱）
    def future_neg_any(col, k):
        result = pd.Series(False, index=data.index)
        for i in range(1, k + 1):
            shifted = g[col].shift(-i)
            result = result | (shifted == 0)
        return result
    data['_trap_4w'] = future_neg_any('_zc_pos', 4)

    # 7. 未来 4 周收益
    rs1 = g[COL_RET_NAME].shift(-1)
    rs2 = g[COL_RET_NAME].shift(-2)
    rs3 = g[COL_RET_NAME].shift(-3)
    rs4 = g[COL_RET_NAME].shift(-4)
    data['_ret_4w'] = (rs1 + rs2 + rs3 + rs4)

    # 8. 分析 WXZC 转正事件
    events = data[data['_break'] == 1].copy()
    print(f'\n总 WXZC 转正事件数: {len(events)}')

    # 分层：深跌 run 内 / 深跌后 WXCD 已转正 / 非深跌
    cd_val = events.iloc[:, COL_WXCD].astype(int)
    za_val = events.iloc[:, COL_WXZA].astype(int)
    ab_val = events.iloc[:, COL_WXAB].astype(int)

    # 深跌 run 内：当前 _cd_neg_run >= 20（WXCD 仍为负）
    in_deep_run = (events['_cd_neg_run'] >= 20) & (cd_val < 0)
    # 深跌后 WXCD 已转正：历史最大 >= 20 且当前 WXCD>0
    after_deep = (events['_cd_neg_run_max'] >= 20) & (cd_val > 0)
    # 非深跌：历史最大 < 20
    non_deep = events['_cd_neg_run_max'] < 20

    print('\n=== 全局：WXZC 转正时，按 WXCD 状态分层 ===')
    print(f"{'WXCD状态':<16} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}")
    for label, mask in [
        ('WXCD>0(已转正)', cd_val > 0),
        ('WXCD<0(仍为负)', cd_val < 0),
    ]:
        sub = events[mask]
        n = len(sub)
        if n == 0:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        print(f"{label:<16} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}")

    print('\n=== 深跌场景分层（历史最大 WXCD连续为负 >=20周）===')
    print(f"{'场景':<20} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}")
    for label, mask in [
        ('深跌run内(WXCD仍负)', in_deep_run),
        ('深跌后WXCD已转正', after_deep),
        ('非深跌', non_deep),
    ]:
        sub = events[mask]
        n = len(sub)
        if n == 0:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        print(f"{label:<20} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}")

    print('\n=== 深跌run内（WXCD仍负）WXZC转正，按过滤条件细分 ===')
    deep_in = events[in_deep_run]
    print(f"{'过滤条件':<24} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}")
    for label, mask in [
        ('WXZA>0(沿WJA)', deep_in.iloc[:, COL_WXZA].astype(int) > 0),
        ('WXZA<=0(未沿WJA)', deep_in.iloc[:, COL_WXZA].astype(int) <= 0),
        ('WXAB>0(龙骨正)', deep_in.iloc[:, COL_WXAB].astype(int) > 0),
        ('WXAB<0(龙骨负)', deep_in.iloc[:, COL_WXAB].astype(int) < 0),
        ('WXAB当周转正', deep_in['_ab_turn'] == 1),
        ('WXAB未转正', deep_in['_ab_turn'] == 0),
    ]:
        sub = deep_in[mask]
        n = len(sub)
        if n == 0:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        print(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}")

    print('\n=== 深跌run内，组合过滤（WXZA + WXAB）===')
    za_d = deep_in.iloc[:, COL_WXZA].astype(int)
    ab_d = deep_in.iloc[:, COL_WXAB].astype(int)
    for label, mask in [
        ('WXZA>0+WXAB>0', (za_d > 0) & (ab_d > 0)),
        ('WXZA>0+WXAB<0', (za_d > 0) & (ab_d < 0)),
        ('WXZA<=0+WXAB>0', (za_d <= 0) & (ab_d > 0)),
        ('WXZA<=0+WXAB<0', (za_d <= 0) & (ab_d < 0)),
    ]:
        sub = deep_in[mask]
        n = len(sub)
        if n == 0:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        print(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}")

    print('\n=== 深跌后WXCD已转正，WXZC转正（真突破候选）===')
    deep_after = events[after_deep]
    print(f"{'过滤条件':<24} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}")
    for label, mask in [
        ('WXZA>0(沿WJA)', deep_after.iloc[:, COL_WXZA].astype(int) > 0),
        ('WXZA<=0(未沿WJA)', deep_after.iloc[:, COL_WXZA].astype(int) <= 0),
        ('WXAB>0(龙骨正)', deep_after.iloc[:, COL_WXAB].astype(int) > 0),
        ('WXAB<0(龙骨负)', deep_after.iloc[:, COL_WXAB].astype(int) < 0),
    ]:
        sub = deep_after[mask]
        n = len(sub)
        if n == 0:
            continue
        trap4 = sub['_trap_4w'].mean() * 100
        avg_ret4 = sub['_ret_4w'].mean()
        print(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}")

    # 保存结果
    out = '____temp/_深跌诱多陷阱_WXCD过滤结果.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('=== 全局：WXZC 转正时，按 WXCD 状态分层 ===\n')
        f.write(f"{'WXCD状态':<16} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}\n")
        for label, mask in [('WXCD>0(已转正)', cd_val > 0), ('WXCD<0(仍为负)', cd_val < 0)]:
            sub = events[mask]
            n = len(sub)
            if n == 0:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            f.write(f"{label:<16} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}\n")
        f.write('\n=== 深跌场景分层（历史最大 WXCD连续为负 >=20周）===\n')
        f.write(f"{'场景':<20} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}\n")
        for label, mask in [('深跌run内(WXCD仍负)', in_deep_run), ('深跌后WXCD已转正', after_deep), ('非深跌', non_deep)]:
            sub = events[mask]
            n = len(sub)
            if n == 0:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            f.write(f"{label:<20} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}\n")
        f.write('\n=== 深跌run内（WXCD仍负）WXZC转正，按过滤条件细分 ===\n')
        f.write(f"{'过滤条件':<24} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}\n")
        for label, mask in [
            ('WXZA>0(沿WJA)', deep_in.iloc[:, COL_WXZA].astype(int) > 0),
            ('WXZA<=0(未沿WJA)', deep_in.iloc[:, COL_WXZA].astype(int) <= 0),
            ('WXAB>0(龙骨正)', deep_in.iloc[:, COL_WXAB].astype(int) > 0),
            ('WXAB<0(龙骨负)', deep_in.iloc[:, COL_WXAB].astype(int) < 0),
            ('WXAB当周转正', deep_in['_ab_turn'] == 1),
            ('WXAB未转正', deep_in['_ab_turn'] == 0),
        ]:
            sub = deep_in[mask]
            n = len(sub)
            if n == 0:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            f.write(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}\n")
        f.write('\n=== 深跌run内，组合过滤（WXZA + WXAB）===\n')
        f.write(f"{'组合':<24} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}\n")
        for label, mask in [
            ('WXZA>0+WXAB>0', (za_d > 0) & (ab_d > 0)),
            ('WXZA>0+WXAB<0', (za_d > 0) & (ab_d < 0)),
            ('WXZA<=0+WXAB>0', (za_d <= 0) & (ab_d > 0)),
            ('WXZA<=0+WXAB<0', (za_d <= 0) & (ab_d < 0)),
        ]:
            sub = deep_in[mask]
            n = len(sub)
            if n == 0:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            f.write(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}\n")
        f.write('\n=== 深跌后WXCD已转正，WXZC转正（真突破候选）===\n')
        f.write(f"{'过滤条件':<24} {'事件数':>8} {'4周内转负%':>10} {'4周均收益%':>10}\n")
        for label, mask in [
            ('WXZA>0(沿WJA)', deep_after.iloc[:, COL_WXZA].astype(int) > 0),
            ('WXZA<=0(未沿WJA)', deep_after.iloc[:, COL_WXZA].astype(int) <= 0),
            ('WXAB>0(龙骨正)', deep_after.iloc[:, COL_WXAB].astype(int) > 0),
            ('WXAB<0(龙骨负)', deep_after.iloc[:, COL_WXAB].astype(int) < 0),
        ]:
            sub = deep_after[mask]
            n = len(sub)
            if n == 0:
                continue
            trap4 = sub['_trap_4w'].mean() * 100
            avg_ret4 = sub['_ret_4w'].mean()
            f.write(f"{label:<24} {n:>8} {trap4:>10.2f} {avg_ret4:>10.3f}\n")
    print(f'\n结果已保存到 {out}')

if __name__ == '__main__':
    main()
