# -*- coding: utf-8 -*-
"""
方法日A趋(6.0) / 方法日B趋(6.1) / 方法日C冲(6.3) 综合分析
========================================================
使用日类数据（含并入的周类指标 col70-130）做周日联合分析。
只加载需要的列，提高效率。

关键列（0-based，元数据权威）：
- 日期[0] 收[1] 涨幅[5] 高幅[6] 次日高幅[26]
- 日ZA[13]=DXZA 日ZC[14]=DXZC 日ZB[66]=DXZB
- 层界[28]=日层界
- 周层界[80]=周层界 周ZA[85]=WXZA 周ZB[86]=WXZB 周ZC[87]=WXZC 周AB[91]=WXAB
- 周护型[73]=WXAB护型 周柱排[77] 周波型[79]
"""
import pandas as pd
import numpy as np
import glob
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组日'

# 需要的列（0-based）
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
    data = data.sort_values(['fid', data.columns[0]]).reset_index(drop=True)
    g = data.groupby('fid')

    # 列名（用位置取，注意 usecols 后列被重排为 0-15）
    # NEED_COLS = [0,1,5,6,13,14,26,27,28,66,73,80,85,86,87,91]
    # 新位置: 0=日期 1=收 2=涨幅 3=高幅 4=日ZA 5=日ZC 6=次日高幅 7=柱型 8=层界 9=日ZB 10=周护型 11=周层界 12=周ZA 13=周ZB 14=周ZC 15=周AB
    C_RET = 2; C_HR = 3; C_NEXT_HR = 6
    C_ZA = 4; C_ZC = 5; C_ZB = 9
    C_WJIE = 11; C_WZA = 12; C_WZB = 13; C_WZC = 14; C_WAB = 15
    C_WHX = 10

    # 周层界首位
    wjie = data.iloc[:, C_WJIE].astype(str)
    data['_wjie_first'] = wjie.apply(lambda s: s[1:] if s.startswith('_') else s).str[0]
    prev_wjie = g['_wjie_first'].shift(1)
    data['_prev_wjie'] = prev_wjie

    # 进入主升事件：前一周首位 != 主，本周首位 = 主
    data['_enter_main'] = ((data['_wjie_first'] == '主') & (prev_wjie != '主')).astype(int)
    data['_path'] = ''
    data.loc[(data['_enter_main'] == 1) & (prev_wjie.isin(['初', '储'])), '_path'] = 'A'
    data.loc[(data['_enter_main'] == 1) & (prev_wjie == '再'), '_path'] = 'B'

    # 周A/周B满足 = 进入主升后持有（周层界=主）
    data['_in_main'] = (data['_wjie_first'] == '主').astype(int)

    # 日类指标
    za = data.iloc[:, C_ZA].astype(float)
    zc = data.iloc[:, C_ZC].astype(float)
    zb = data.iloc[:, C_ZB].astype(float)
    ret = data.iloc[:, C_RET].astype(float)
    next_hr = data.iloc[:, C_NEXT_HR].astype(float)
    wza = data.iloc[:, C_WZA].astype(float)
    wzb = data.iloc[:, C_WZB].astype(float)
    wzc = data.iloc[:, C_WZC].astype(float)
    wab = data.iloc[:, C_WAB].astype(float)

    # ============================================================
    # 方法日A趋 (6.0)：周A/周B满足时持有，不看日类
    # ============================================================
    print('='*80)
    print('【方法日A趋 6.0】周A/周B满足时持有，统计下破DXZC/DXZB比率')
    print('='*80)

    events = data[data['_enter_main'] == 1].copy()
    events['_za'] = za.loc[events.index].values
    events['_zc'] = zc.loc[events.index].values
    events['_zb'] = zb.loc[events.index].values
    events['_wza'] = wza.loc[events.index].values
    events['_wzb'] = wzb.loc[events.index].values
    events['_wzc'] = wzc.loc[events.index].values
    events['_wab'] = wab.loc[events.index].values
    events['_ret'] = ret.loc[events.index].values
    events['_next_hr'] = next_hr.loc[events.index].values

    print(f'\n总进入主升事件数: {len(events)}')
    print(f'周A趋(初/储进入): {(events["_path"]=="A").sum()} 周B趋(再进入): {(events["_path"]=="B").sum()}')

    # 进入主升当日日类状态
    print('\n--- 进入主升当日日类状态 ---')
    print(f"{'路径':<6} {'n':>8} {'DXZA>0%':>9} {'DXZC>0%':>9} {'DXZB>0%':>9} {'WXZA>0%':>9} {'WXZC>0%':>9}")
    for path in ['A', 'B', '']:
        sub = events[events['_path'] == path] if path else events
        n = len(sub)
        if n == 0: continue
        print(f"{path or '全部':<6} {n:>8} {(sub['_za']>0).mean()*100:>8.1f}% {(sub['_zc']>0).mean()*100:>8.1f}% {(sub['_zb']>0).mean()*100:>8.1f}% {(sub['_wza']>0).mean()*100:>8.1f}% {(sub['_wzc']>0).mean()*100:>8.1f}%")

    # 持有期间下破DXZC/DXZB比率
    print('\n--- 进入主升后未来N天日类下破比率 ---')
    print(f"{'路径':<6} {'n':>8} {'5天下破ZC':>10} {'10天下破ZC':>11} {'20天下破ZC':>11} {'5天下破ZB':>10} {'10天下破ZB':>11} {'20天下破ZB':>11}")
    for path in ['A', 'B', '']:
        sub = events[events['_path'] == path] if path else events
        n = len(sub)
        if n == 0: continue
        idx = sub.index
        row = []
        for k in [5, 10, 20]:
            neg_zc = pd.Series(False, index=idx)
            for i in range(1, k+1):
                neg_zc = neg_zc | (g["日ZC"].shift(-i).loc[idx] < 0)
            row.append(f"{neg_zc.mean()*100:>9.1f}%")
        for k in [5, 10, 20]:
            neg_zb = pd.Series(False, index=idx)
            for i in range(1, k+1):
                neg_zb = neg_zb | (g["DTZB"].shift(-i).loc[idx] < 0)
            row.append(f"{neg_zb.mean()*100:>9.1f}%")
        print(f"{path or '全部':<6} {n:>8} {' '.join(row)}")

    # 进入主升后未来收益
    print('\n--- 进入主升后未来收益（纯持有，不看日类）---')
    print(f"{'路径':<6} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'20日均涨%':>10} {'次日冲高≥3%':>12}")
    for path in ['A', 'B', '']:
        sub = events[events['_path'] == path] if path else events
        n = len(sub)
        if n == 0: continue
        idx = sub.index
        next_ret = g["涨幅"].shift(-1).loc[idx]
        ret5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            ret5 = ret5 + g["涨幅"].shift(-i).loc[idx].fillna(0)
        ret10 = pd.Series(0.0, index=idx)
        for i in range(1, 11):
            ret10 = ret10 + g["涨幅"].shift(-i).loc[idx].fillna(0)
        ret20 = pd.Series(0.0, index=idx)
        for i in range(1, 21):
            ret20 = ret20 + g["涨幅"].shift(-i).loc[idx].fillna(0)
        next_hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        print(f"{path or '全部':<6} {n:>8} {next_ret.mean():>8.3f}% {ret5.mean():>8.3f}% {ret10.mean():>9.3f}% {ret20.mean():>9.3f}% {next_hr3:>11.1f}%")

    # ============================================================
    # 方法日B趋 (6.1)：周A/周B + DJC入口介入，用DJC作为止盈线
    # ============================================================
    print('\n' + '='*80)
    print('【方法日B趋 6.1】周A/周B + DJC入口介入，DJC止盈')
    print('='*80)

    print('\n--- 进入主升后按DXZC状态分组（DJC丘内 vs 丘外）---')
    print(f"{'路径':<6} {'DXZC':<6} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'次日冲高≥3%':>12}")
    for path in ['A', 'B']:
        for zc_state, label in [(1, '>0'), (0, '<=0')]:
            sub = events[(events['_path'] == path) & ((events['_zc'] > 0) == (zc_state == 1))]
            n = len(sub)
            if n == 0: continue
            idx = sub.index
            next_ret = g["涨幅"].shift(-1).loc[idx]
            ret5 = pd.Series(0.0, index=idx)
            for i in range(1, 6):
                ret5 = ret5 + g["涨幅"].shift(-i).loc[idx].fillna(0)
            ret10 = pd.Series(0.0, index=idx)
            for i in range(1, 11):
                ret10 = ret10 + g["涨幅"].shift(-i).loc[idx].fillna(0)
            next_hr3 = (next_hr.loc[idx] >= 3).mean() * 100
            print(f"{path:<6} {label:<6} {n:>8} {next_ret.mean():>8.3f}% {ret5.mean():>8.3f}% {ret10.mean():>9.3f}% {next_hr3:>11.1f}%")

    # DJC止盈 vs 周类出口
    print('\n--- DJC止盈(DXZC<0退出) vs 周类出口(WXZC<0退出) ---')
    in_main = data['_in_main'].values
    print(f"{'退出信号':<12} {'n':>8} {'次日均涨%':>9} {'次日冲高≥3%':>12} {'次日跌≥3%':>10}")
    zc_neg_evt = (zc < 0) & (in_main == 1)
    idx_zc = data.index[zc_neg_evt]
    if len(idx_zc) > 0:
        next_ret = g["涨幅"].shift(-1).loc[idx_zc]
        next_hr3 = (next_hr.loc[idx_zc] >= 3).mean() * 100
        next_neg3 = (next_ret <= -3).mean() * 100
        print(f"{'DXZC<0':<12} {len(idx_zc):>8} {next_ret.mean():>8.3f}% {next_hr3:>11.1f}% {next_neg3:>9.1f}%")
    wzc_neg_evt = (wzc < 0) & (in_main == 1)
    idx_wzc = data.index[wzc_neg_evt]
    if len(idx_wzc) > 0:
        next_ret = g["涨幅"].shift(-1).loc[idx_wzc]
        next_hr3 = (next_hr.loc[idx_wzc] >= 3).mean() * 100
        next_neg3 = (next_ret <= -3).mean() * 100
        print(f"{'WXZC<0':<12} {len(idx_wzc):>8} {next_ret.mean():>8.3f}% {next_hr3:>11.1f}% {next_neg3:>9.1f}%")

    # ============================================================
    # 方法日C冲 (6.3)：周A/周B + DJA均上期权
    # ============================================================
    print('\n' + '='*80)
    print('【方法日C冲 6.3】周A/周B + DJA均上期权')
    print('='*80)

    print('\n--- 进入主升后按DXZA状态分组（DJA之上 vs 之下）---')
    print(f"{'路径':<6} {'DXZA':<6} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'次日冲高≥3%':>12}")
    for path in ['A', 'B']:
        for za_state, label in [(1, '>0'), (0, '<=0')]:
            sub = events[(events['_path'] == path) & ((events['_za'] > 0) == (za_state == 1))]
            n = len(sub)
            if n == 0: continue
            idx = sub.index
            next_ret = g["涨幅"].shift(-1).loc[idx]
            ret5 = pd.Series(0.0, index=idx)
            for i in range(1, 6):
                ret5 = ret5 + g["涨幅"].shift(-i).loc[idx].fillna(0)
            ret10 = pd.Series(0.0, index=idx)
            for i in range(1, 11):
                ret10 = ret10 + g["涨幅"].shift(-i).loc[idx].fillna(0)
            next_hr3 = (next_hr.loc[idx] >= 3).mean() * 100
            print(f"{path:<6} {label:<6} {n:>8} {next_ret.mean():>8.3f}% {ret5.mean():>8.3f}% {ret10.mean():>9.3f}% {next_hr3:>11.1f}%")

    # DJA之上阳柱 vs 阴柱
    print('\n--- DJA之上按柱型分组（阳柱 vs 阴柱）---')
    print(f"{'路径':<6} {'柱型':<6} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'次日冲高≥3%':>12}")
    for path in ['A', 'B']:
        for yang_state, label in [(1, '阳柱'), (0, '阴柱')]:
            sub = events[(events['_path'] == path) & (events['_za'] > 0) & ((ret.loc[events.index] > 0) == (yang_state == 1))]
            n = len(sub)
            if n == 0: continue
            idx = sub.index
            next_ret = g["涨幅"].shift(-1).loc[idx]
            ret5 = pd.Series(0.0, index=idx)
            for i in range(1, 6):
                ret5 = ret5 + g["涨幅"].shift(-i).loc[idx].fillna(0)
            next_hr3 = (next_hr.loc[idx] >= 3).mean() * 100
            print(f"{path:<6} {label:<6} {n:>8} {next_ret.mean():>8.3f}% {ret5.mean():>8.3f}% {next_hr3:>11.1f}%")

    # DJA之上阴柱后下破DJA比率
    print('\n--- DJA之上阴柱后未来N天下破DJA(DXZA<0)比率 ---')
    print(f"{'路径':<6} {'n':>8} {'3天下破':>9} {'5天下破':>9} {'10天下破':>10}")
    for path in ['A', 'B']:
        sub = events[(events['_path'] == path) & (events['_za'] > 0) & (ret.loc[events.index] < 0)]
        n = len(sub)
        if n == 0: continue
        idx = sub.index
        row = []
        for k in [3, 5, 10]:
            neg_za = pd.Series(False, index=idx)
            for i in range(1, k+1):
                neg_za = neg_za | (g["日ZA"].shift(-i).loc[idx] < 0)
            row.append(f"{neg_za.mean()*100:>8.1f}%")
        print(f"{path:<6} {n:>8} {' '.join(row)}")

    # 退出点分析
    print('\n--- 退出点分析 ---')
    za_neg_evt = (za < 0) & (in_main == 1)
    idx_za = data.index[za_neg_evt]
    if len(idx_za) > 0:
        next_ret = g["涨幅"].shift(-1).loc[idx_za]
        next_hr3 = (next_hr.loc[idx_za] >= 3).mean() * 100
        next_neg3 = (next_ret <= -3).mean() * 100
        print(f"{'下破DJA(DXZA<0)':<16} {len(idx_za):>8} {next_ret.mean():>8.3f}% {next_hr3:>11.1f}% {next_neg3:>9.1f}%")

    # 下破DJA两柱
    za_neg2 = (za < 0) & (g["日ZA"].shift(1) < 0) & (in_main == 1)
    idx_za2 = data.index[za_neg2]
    if len(idx_za2) > 0:
        next_ret = g["涨幅"].shift(-1).loc[idx_za2]
        next_hr3 = (next_hr.loc[idx_za2] >= 3).mean() * 100
        next_neg3 = (next_ret <= -3).mean() * 100
        print(f"{'下破DJA两柱':<16} {len(idx_za2):>8} {next_ret.mean():>8.3f}% {next_hr3:>11.1f}% {next_neg3:>9.1f}%")

    # 周类止损
    is_hu = (wab < 0) & (wzb < 0)
    wzc_stop = (wzc < 0) | ((wzc > 0) & is_hu)
    wzc_stop_evt = wzc_stop & (in_main == 1)
    idx_wstop = data.index[wzc_stop_evt]
    if len(idx_wstop) > 0:
        next_ret = g["涨幅"].shift(-1).loc[idx_wstop]
        next_hr3 = (next_hr.loc[idx_wstop] >= 3).mean() * 100
        next_neg3 = (next_ret <= -3).mean() * 100
        print(f"{'周类止损(WXZC<0或虎)':<16} {len(idx_wstop):>8} {next_ret.mean():>8.3f}% {next_hr3:>11.1f}% {next_neg3:>9.1f}%")

    print('\n完成')

if __name__ == '__main__':
    main()