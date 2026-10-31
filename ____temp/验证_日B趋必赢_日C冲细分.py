# -*- coding: utf-8 -*-
"""
方法日B趋(6.1) 必赢验证 + 方法日C冲(6.3) 介入点/退出点深入分析
============================================================
1. 方法日B趋：DJC丘内介入，DJC止盈，验证是否必赢
   - DJC丘内（DXZC>0）介入的收益分布
   - DJC止盈 vs 周类两出口的对比
   - 必赢验证：DJC丘内介入后，持有到DJC转负的累计收益
2. 方法日C冲：DJA均上期权
   - 介入点细分：即将上破DJA / DJA之上阳柱 / DJA之上阴柱 / 即将下破DJA
   - 退出点细分：DJA之上止盈 / 下破DJA两柱 / 周类止损
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

    # 列名（usecols 后）
    # 0=日期 1=收 2=涨幅 3=高幅 4=日ZA 5=日ZC 6=次日高幅 7=柱型 8=层界 9=DTZB 10=周护型 11=周层界 12=周ZA 13=周ZB 14=周ZC 15=周AB
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
    # 方法日B趋 (6.1)：DJC丘内介入，DJC止盈，验证必赢
    # ============================================================
    print('='*80)
    print('【方法日B趋 6.1】DJC丘内介入，DJC止盈，必赢验证')
    print('='*80)

    # DJC丘 = DXZC>0区域。DJC丘内介入 = 进入主升后，DXZC>0时介入
    # 必赢验证：DJC丘内介入后，持有到DJC转负（DXZC<0）的累计收益
    # 用事件法：找到每个DJC丘（DXZC>0连续区域），统计丘内介入的收益

    # 方法：对每个fid，找到DXZC>0的区域（DJC丘），
    # 丘内每一天都作为介入点，统计持有到丘末（DXZC转负前一天）的累计收益
    print('\n--- DJC丘内介入，持有到DJC转负的累计收益 ---')
    print(f"{'路径':<6} {'介入数':>8} {'均持有天数':>10} {'累计收益%':>10} {'正收益占比%':>12} {'冲高≥3%':>10}")

    # 对每个fid，找到DJC丘
    results = []
    for fid, sub in data.groupby('fid'):
        sub = sub.reset_index(drop=True)
        zc_arr = sub['日ZC'].astype(float).values
        ret_arr = sub['涨幅'].astype(float).values
        hr_arr = sub['次日高幅'].astype(float).values
        path_arr = sub['_path'].values
        in_main = sub['_in_main'].values
        n = len(sub)
        i = 0
        while i < n:
            # 找DJC丘起点（DXZC>0）
            if zc_arr[i] <= 0 or in_main[i] != 1:
                i += 1
                continue
            start = i
            # 找丘末（DXZC<=0）
            while i < n and zc_arr[i] > 0:
                i += 1
            end = i
            # 丘内每一天作为介入点
            for j in range(start, end):
                path = path_arr[j]
                if path not in ('A', 'B'):
                    continue
                # 持有到丘末（end-1）的累计收益
                cum = ret_arr[j+1:end].sum() if end > j+1 else 0
                # 持有期间最高冲高
                max_hr = hr_arr[j+1:end].max() if end > j+1 else 0
                hold_days = end - j - 1
                results.append((path, hold_days, cum, max_hr))

    if results:
        df_res = pd.DataFrame(results, columns=['path', 'hold_days', 'cum', 'max_hr'])
        for path in ['A', 'B']:
            sub = df_res[df_res['path'] == path]
            n = len(sub)
            if n == 0: continue
            avg_hold = sub['hold_days'].mean()
            avg_cum = sub['cum'].mean()
            pos_pct = (sub['cum'] > 0).mean() * 100
            hr3 = (sub['max_hr'] >= 3).mean() * 100
            print(f"{path:<6} {n:>8} {avg_hold:>10.1f} {avg_cum:>10.3f} {pos_pct:>11.1f}% {hr3:>9.1f}%")

    # DJC止盈 vs 周类两出口：更精确对比
    print('\n--- DJC止盈 vs 周类两出口（进入主升后）---')
    print(f"{'退出信号':<16} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'次日冲高≥3%':>12} {'次日跌≥3%':>10}")
    in_main = data['_in_main'].values

    # DJC止盈：DXZC<0（在进入主升后）
    zc_neg = (zc < 0) & (in_main == 1)
    idx = data.index[zc_neg]
    if len(idx) > 0:
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{'DXZC<0(DJC止盈)':<16} {len(idx):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {hr3:>11.1f}% {neg3:>9.1f}%")

    # 周类两出口：WXZC<0
    wzc_neg = (wzc < 0) & (in_main == 1)
    idx = data.index[wzc_neg]
    if len(idx) > 0:
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{'WXZC<0(周类出口)':<16} {len(idx):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {hr3:>11.1f}% {neg3:>9.1f}%")

    # 周类两出口：WXZC<0或(WXZC>0且虎)
    is_hu = (wab < 0) & (wzb < 0)
    wzc_stop = (wzc < 0) | ((wzc > 0) & is_hu)
    wzc_stop_evt = wzc_stop & (in_main == 1)
    idx = data.index[wzc_stop_evt]
    if len(idx) > 0:
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{'WXZC<0或虎':<16} {len(idx):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {hr3:>11.1f}% {neg3:>9.1f}%")

    # ============================================================
    # 方法日C冲 (6.3)：DJA均上期权，介入点/退出点细分
    # ============================================================
    print('\n' + '='*80)
    print('【方法日C冲 6.3】DJA均上期权，介入点/退出点细分')
    print('='*80)

    # 介入点细分（进入主升后）：
    # 1. 即将上破DJA：DJA之下阳柱（DXZA<=0且涨幅>0）
    # 2. 首上破DJA：DXZA由<=0转>0
    # 3. DJA之上阳柱：DXZA>0且涨幅>0
    # 4. DJA之上阴柱：DXZA>0且涨幅<0
    # 5. 即将下破DJA：DJA之上阴柱（DXZA>0且涨幅<0）
    # 6. 下破DJA两柱：DXZA<0连续2天

    events = data[data['_enter_main'] == 1].copy()
    events['_za'] = za.loc[events.index].values
    events['_zc'] = zc.loc[events.index].values
    events['_ret'] = ret.loc[events.index].values
    events['_next_hr'] = next_hr.loc[events.index].values

    # 前一日DXZA
    prev_za = g['日ZA'].shift(1)
    events['_prev_za'] = prev_za.loc[events.index].values

    print('\n--- 介入点细分（进入主升后）---')
    print(f"{'介入点':<16} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'次日冲高≥3%':>12} {'次日跌≥3%':>10}")

    # 定义介入点
    def calc_entry(mask, label):
        sub = events[mask]
        n = len(sub)
        if n == 0:
            print(f"{label:<16} {0:>8}")
            return
        idx = sub.index
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        r10 = pd.Series(0.0, index=idx)
        for i in range(1, 11):
            r10 = r10 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{label:<16} {n:>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {r10.mean():>9.3f}% {hr3:>11.1f}% {neg3:>9.1f}%")

    # 1. DJA之下阳柱（即将上破DJA）
    calc_entry((events['_za'] <= 0) & (events['_ret'] > 0), 'DJA之下阳柱')
    # 2. 首上破DJA（DXZA由<=0转>0）
    calc_entry((events['_za'] > 0) & (events['_prev_za'] <= 0), '首上破DJA')
    # 3. DJA之上阳柱
    calc_entry((events['_za'] > 0) & (events['_ret'] > 0), 'DJA之上阳柱')
    # 4. DJA之上阴柱
    calc_entry((events['_za'] > 0) & (events['_ret'] < 0), 'DJA之上阴柱')
    # 5. 即将下破DJA（DJA之上阴柱）
    calc_entry((events['_za'] > 0) & (events['_ret'] < 0), '即将下破DJA')

    # 6. 下破DJA两柱（DXZA<0连续2天）
    za_neg2 = (za < 0) & (g['日ZA'].shift(1) < 0) & (data['_in_main'] == 1)
    idx2 = data.index[za_neg2]
    if len(idx2) > 0:
        nr = g['涨幅'].shift(-1).loc[idx2]
        r5 = pd.Series(0.0, index=idx2)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx2].fillna(0)
        r10 = pd.Series(0.0, index=idx2)
        for i in range(1, 11):
            r10 = r10 + g['涨幅'].shift(-i).loc[idx2].fillna(0)
        hr3 = (next_hr.loc[idx2] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{'下破DJA两柱':<16} {len(idx2):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {r10.mean():>9.3f}% {hr3:>11.1f}% {neg3:>9.1f}%")

    # 退出点细分
    print('\n--- 退出点细分（进入主升后）---')
    print(f"{'退出点':<16} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'次日冲高≥3%':>12} {'次日跌≥3%':>10}")

    # 1. DJA之上止盈（下日冲高思想）：DXZA>0时次日冲高≥3%
    # 简化：DJA之上时，次日冲高≥3%的概率（作为止盈参考）
    za_pos = (za > 0) & (in_main == 1)
    idx = data.index[za_pos]
    if len(idx) > 0:
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        print(f"{'DJA之上冲高≥3%':<16} {len(idx):>8} {'':>9} {'':>9} {hr3:>11.1f}% {'':>10}")

    # 2. 下破DJA两柱
    # 已在上面计算

    # 3. 周类止损
    # 已在上面计算

    # 必赢验证：DJC丘内介入，持有到丘末的累计收益分布
    print('\n--- DJC丘内介入累计收益分布（必赢验证）---')
    if results:
        df_res = pd.DataFrame(results, columns=['path', 'hold_days', 'cum', 'max_hr'])
        for path in ['A', 'B']:
            sub = df_res[df_res['path'] == path]
            n = len(sub)
            if n == 0: continue
            # 累计收益分布
            pct_neg = (sub['cum'] < 0).mean() * 100
            pct_0 = (sub['cum'] == 0).mean() * 100
            pct_pos = (sub['cum'] > 0).mean() * 100
            pct_pos3 = (sub['cum'] >= 3).mean() * 100
            pct_pos5 = (sub['cum'] >= 5).mean() * 100
            print(f"{path}: n={n}, 累计<0 {pct_neg:.1f}%, =0 {pct_0:.1f}%, >0 {pct_pos:.1f}%, ≥3% {pct_pos3:.1f}%, ≥5% {pct_pos5:.1f}%")

    print('\n完成')

if __name__ == '__main__':
    main()