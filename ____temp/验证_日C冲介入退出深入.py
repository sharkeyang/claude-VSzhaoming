# -*- coding: utf-8 -*-
"""
方法日C冲(6.3) 介入点/退出点深入分析
====================================
针对用户提出的具体介入点/退出点做详尽分析。

介入点：
1. 即将上破DJA（DJA之下阳柱、首上破DJA）
2. DJA之上阳柱（最佳介入点，最好形成启动结构）
3. DJA之上阴柱（是否形成日漏）
4. 即将下破DJA（首先破DJA、价下破DJA、下破DJA两柱）
5. 放弃下破DJA两柱

退出点：
1. DJA之上止盈（下日冲高思想）
2. 下破DJA两柱
3. 周类止损（WXZC<0或(WXZC>0且虎)）
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

    # 前一日/前两日DXZA
    prev_za = g['日ZA'].shift(1)
    prev2_za = g['日ZA'].shift(2)
    data['_prev_za'] = prev_za
    data['_prev2_za'] = prev2_za

    # 前一日涨幅
    prev_ret = g['涨幅'].shift(1)
    data['_prev_ret'] = prev_ret

    # 进入主升后的事件
    events = data[data['_enter_main'] == 1].copy()
    events['_za'] = za.loc[events.index].values
    events['_zc'] = zc.loc[events.index].values
    events['_ret'] = ret.loc[events.index].values
    events['_next_hr'] = next_hr.loc[events.index].values
    events['_prev_za'] = prev_za.loc[events.index].values
    events['_prev2_za'] = prev2_za.loc[events.index].values
    events['_prev_ret'] = prev_ret.loc[events.index].values

    print('='*80)
    print('【方法日C冲 6.3】介入点/退出点深入分析')
    print('='*80)

    # ============================================================
    # 介入点分析
    # ============================================================
    print('\n' + '='*80)
    print('【介入点分析】')
    print('='*80)

    def calc_entry(mask, label, events=events):
        sub = events[mask]
        n = len(sub)
        if n == 0:
            print(f"{label:<20} {0:>8}")
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
        # 未来5天内下破DJA（DXZA<0）比率
        neg_za5 = pd.Series(False, index=idx)
        for i in range(1, 6):
            neg_za5 = neg_za5 | (g['日ZA'].shift(-i).loc[idx] < 0)
        print(f"{label:<20} {n:>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {r10.mean():>9.3f}% {hr3:>11.1f}% {neg3:>9.1f}% {neg_za5.mean()*100:>10.1f}%")

    print(f"{'介入点':<20} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'次日冲高≥3%':>12} {'次日跌≥3%':>10} {'5天下破DJA':>10}")

    # 1. DJA之下阳柱（即将上破DJA）
    calc_entry((events['_za'] <= 0) & (events['_ret'] > 0), 'DJA之下阳柱')
    # 2. 首上破DJA（DXZA由<=0转>0）
    calc_entry((events['_za'] > 0) & (events['_prev_za'] <= 0), '首上破DJA')
    # 3. DJA之上阳柱（最佳介入点）
    calc_entry((events['_za'] > 0) & (events['_ret'] > 0), 'DJA之上阳柱')
    # 4. DJA之上阴柱（是否形成日漏）
    calc_entry((events['_za'] > 0) & (events['_ret'] < 0), 'DJA之上阴柱')
    # 5. 即将下破DJA（DJA之上阴柱）
    calc_entry((events['_za'] > 0) & (events['_ret'] < 0), '即将下破DJA')

    # 6. 首先破DJA（DXZA由>0转<0）
    calc_entry((events['_za'] < 0) & (events['_prev_za'] > 0), '首先破DJA')
    # 7. 价下破DJA（DXZA<0）
    calc_entry((events['_za'] < 0), '价下破DJA')

    # 8. 下破DJA两柱（DXZA<0连续2天）
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
        neg_za5 = pd.Series(False, index=idx2)
        for i in range(1, 6):
            neg_za5 = neg_za5 | (g['日ZA'].shift(-i).loc[idx2] < 0)
        print(f"{'下破DJA两柱':<20} {len(idx2):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {r10.mean():>9.3f}% {hr3:>11.1f}% {neg3:>9.1f}% {neg_za5.mean()*100:>10.1f}%")

    # DJA之上阳柱，是否形成启动结构（升连/升吞）
    # 柱型[7]：判断柱排
    print('\n--- DJA之上阳柱，按柱排细分（启动结构 vs 非启动）---')
    # 柱排[7] 是柱型列，需要解析
    # 简化：用涨幅>0且前一日涨幅>0（连阳）作为"启动结构"近似
    events['_prev_ret'] = prev_ret.loc[events.index].values
    calc_entry((events['_za'] > 0) & (events['_ret'] > 0) & (events['_prev_ret'] > 0), 'DJA之上连阳')
    calc_entry((events['_za'] > 0) & (events['_ret'] > 0) & (events['_prev_ret'] <= 0), 'DJA之上单阳')

    # ============================================================
    # 退出点分析
    # ============================================================
    print('\n' + '='*80)
    print('【退出点分析】')
    print('='*80)

    in_main = data['_in_main'].values

    def calc_exit(mask, label):
        idx = data.index[mask]
        n = len(idx)
        if n == 0:
            print(f"{label:<20} {0:>8}")
            return
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        r10 = pd.Series(0.0, index=idx)
        for i in range(1, 11):
            r10 = r10 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        # 未来5天内是否重新站上DJA（DXZA>0）
        pos_za5 = pd.Series(False, index=idx)
        for i in range(1, 6):
            pos_za5 = pos_za5 | (g['日ZA'].shift(-i).loc[idx] > 0)
        print(f"{label:<20} {n:>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {r10.mean():>9.3f}% {hr3:>11.1f}% {neg3:>9.1f}% {pos_za5.mean()*100:>10.1f}%")

    print(f"{'退出点':<20} {'n':>8} {'次日均涨%':>9} {'5日均涨%':>9} {'10日均涨%':>10} {'次日冲高≥3%':>12} {'次日跌≥3%':>10} {'5天重上DJA':>10}")

    # 1. DJA之上止盈（下日冲高思想）：DJA之上时次日冲高≥3%
    # 简化：DJA之上时，次日冲高≥3%的概率
    za_pos = (za > 0) & (in_main == 1)
    idx = data.index[za_pos]
    if len(idx) > 0:
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        print(f"{'DJA之上冲高≥3%':<20} {len(idx):>8} {'':>9} {'':>9} {'':>10} {hr3:>11.1f}% {'':>10}")

    # 2. 下破DJA两柱
    za_neg2 = (za < 0) & (g['日ZA'].shift(1) < 0) & (in_main == 1)
    calc_exit(za_neg2, '下破DJA两柱')

    # 3. 周类止损（WXZC<0或(WXZC>0且虎)）
    is_hu = (wab < 0) & (wzb < 0)
    wzc_stop = (wzc < 0) | ((wzc > 0) & is_hu)
    calc_exit(wzc_stop & (in_main == 1), '周类止损')

    # 4. DJA之上止盈（下日冲高思想）：DJA之上且次日冲高≥3%时止盈
    # 简化：DJA之上时，次日冲高≥3%后，未来5天表现
    za_pos_hr3 = (za > 0) & (next_hr >= 3) & (in_main == 1)
    idx = data.index[za_pos_hr3]
    if len(idx) > 0:
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        print(f"{'DJA之上冲高≥3%后':<20} {len(idx):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {'':>10} {hr3:>11.1f}% {neg3:>9.1f}%")

    # 5. DJA之上阴柱（不提前退出）：DJA之上阴柱后，未来5天表现
    za_pos_yin = (za > 0) & (ret < 0) & (in_main == 1)
    idx = data.index[za_pos_yin]
    if len(idx) > 0:
        nr = g['涨幅'].shift(-1).loc[idx]
        r5 = pd.Series(0.0, index=idx)
        for i in range(1, 6):
            r5 = r5 + g['涨幅'].shift(-i).loc[idx].fillna(0)
        hr3 = (next_hr.loc[idx] >= 3).mean() * 100
        neg3 = (nr <= -3).mean() * 100
        # 未来5天内下破DJA
        neg_za5 = pd.Series(False, index=idx)
        for i in range(1, 6):
            neg_za5 = neg_za5 | (g['日ZA'].shift(-i).loc[idx] < 0)
        print(f"{'DJA之上阴柱后':<20} {len(idx):>8} {nr.mean():>8.3f}% {r5.mean():>8.3f}% {'':>10} {hr3:>11.1f}% {neg3:>9.1f}% {neg_za5.mean()*100:>10.1f}%")

    print('\n完成')

if __name__ == '__main__':
    main()