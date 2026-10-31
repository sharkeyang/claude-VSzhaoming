# -*- coding: utf-8 -*-
"""
周A趋/周B趋 进入主升路径分析
=============================
验证：层界从"初/储"进入"主"（周A趋路径）vs 层界从"再"进入"主"（周B趋路径），
两种路径进入主升后的表现是否有差别。

层界值格式（列[11]）：
- 主Ga顶 / _主Ga顶（JC线上/线下主升）
- 初Aa顶 / _初Aa顶（WJC首次突破）
- 再Bd芽 / _再Bd芽（WJC上劫后）
- 储...（WJC线下蓄势）
- 破局6v（下破WJC）

列索引（元数据权威，0-based）：
- 周涨[1]、PR[2]、HR[3]
- 层界[11]、WXZC[18]、WXAB[22]
"""
import pandas as pd
import numpy as np
import glob
import os

DATA_DIR = '昭明算展/谕组周'
COL_WEEK_RET = 1   # 周涨
COL_HR = 3         # 临高幅
COL_JIE = 11       # 层界
COL_WXZC = 18      # WXZC
COL_WXAB = 22      # WXAB

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

def jie_first(jie):
    """层界首位：主/初/再/储/破（去掉 _ 前缀）"""
    s = str(jie)
    if s.startswith('_'):
        s = s[1:]
    return s[0] if s else ''

def main():
    data = load_all()
    data = data.sort_values(['fid', data.columns[0]]).reset_index(drop=True)

    jie = data.iloc[:, COL_JIE].astype(str)
    ret = data.iloc[:, COL_WEEK_RET].astype(float)
    hr = data.iloc[:, COL_HR].astype(float)
    g = data.groupby('fid')
    # 列名（GBK 中文，用位置取列名）
    COL_RET_NAME = data.columns[COL_WEEK_RET]
    COL_HR_NAME = data.columns[COL_HR]
    COL_ZC_NAME = data.columns[COL_WXZC]

    # 层界首位
    data['_jie_first'] = jie.apply(jie_first)
    # 前一周层界首位
    prev_jie_first = g['_jie_first'].shift(1)
    data['_prev_jie_first'] = prev_jie_first

    # 进入主升事件：前一周首位 != 主，本周首位 = 主
    data['_enter_main'] = ((data['_jie_first'] == '主') & (prev_jie_first != '主')).astype(int)

    # 进入路径：
    # 从"初/储"进入 → 周A趋路径
    # 从"再"进入 → 周B趋路径
    data['_path'] = ''
    data.loc[(data['_enter_main'] == 1) & (prev_jie_first.isin(['初', '储'])), '_path'] = 'A'
    data.loc[(data['_enter_main'] == 1) & (prev_jie_first == '再'), '_path'] = 'B'

    # 未来 4 周/8 周收益
    def future_sum(col_name, k):
        result = pd.Series(0.0, index=data.index)
        for i in range(1, k + 1):
            result = result + g[col_name].shift(-i).fillna(0)
        return result
    data['_ret_4w'] = future_sum(COL_RET_NAME, 4)
    data['_ret_8w'] = future_sum(COL_RET_NAME, 8)

    # 未来 4 周最高 HR（冲高率）
    def future_max(col_name, k):
        result = pd.Series(0.0, index=data.index)
        for i in range(1, k + 1):
            result = result.combine(g[col_name].shift(-i).fillna(0), np.maximum)
        return result
    data['_hr_4w_max'] = future_max(COL_HR_NAME, 4)

    # 未来 4 周内是否跌破 WXZC<0（维持率）
    def future_neg_any(col_name, k):
        result = pd.Series(False, index=data.index)
        for i in range(1, k + 1):
            shifted = g[col_name].shift(-i)
            result = result | (shifted < 0)
        return result
    data['_zc_neg_4w'] = future_neg_any(COL_ZC_NAME, 4)

    # 进入主升事件
    events = data[data['_enter_main'] == 1].copy()
    print(f'\n总进入主升事件数: {len(events)}')

    print('\n=== 进入主升路径分布 ===')
    print(f"{'路径':<8} {'事件数':>8} {'占比%':>8}")
    for path in ['A', 'B']:
        n = (events['_path'] == path).sum()
        print(f"{path:<8} {n:>8} {n/len(events)*100:>8.2f}")

    print('\n=== 两种路径进入主升后的表现 ===')
    print(f"{'路径':<8} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}")
    for path in ['A', 'B']:
        sub = events[events['_path'] == path]
        n = len(sub)
        if n == 0:
            continue
        ret4 = sub['_ret_4w'].mean()
        ret8 = sub['_ret_8w'].mean()
        hr4 = sub['_hr_4w_max'].mean()
        zc_neg = sub['_zc_neg_4w'].mean() * 100
        print(f"{path:<8} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}")

    # 细分：从"初"进入 vs 从"储"进入（周A趋内部）
    print('\n=== 周A趋路径细分（初 vs 储）===')
    print(f"{'来源':<8} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}")
    for src in ['初', '储']:
        sub = events[(events['_path'] == 'A') & (events['_prev_jie_first'] == src)]
        n = len(sub)
        if n == 0:
            continue
        ret4 = sub['_ret_4w'].mean()
        ret8 = sub['_ret_8w'].mean()
        hr4 = sub['_hr_4w_max'].mean()
        zc_neg = sub['_zc_neg_4w'].mean() * 100
        print(f"{src:<8} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}")

    # 周B趋路径细分：进入主升时是否升连周边
    print('\n=== 周B趋路径细分（进入主升时柱排）===')
    # 需要柱排列，但这里简化：用 WXAB 状态
    ab = data.iloc[:, COL_WXAB].astype(int)
    data['_ab_pos'] = (ab > 0).astype(int)
    events['_ab_pos'] = data.loc[events.index, '_ab_pos'].values
    print(f"{'WXAB状态':<10} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}")
    for ab_state, label in [(1, 'WXAB>0'), (0, 'WXAB<=0')]:
        sub = events[(events['_path'] == 'B') & (events['_ab_pos'] == ab_state)]
        n = len(sub)
        if n == 0:
            continue
        ret4 = sub['_ret_4w'].mean()
        ret8 = sub['_ret_8w'].mean()
        hr4 = sub['_hr_4w_max'].mean()
        zc_neg = sub['_zc_neg_4w'].mean() * 100
        print(f"{label:<10} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}")

    # 保存结果
    out = '____temp/_周A趋B进入主升路径结果.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('=== 进入主升路径分布 ===\n')
        f.write(f"{'路径':<8} {'事件数':>8} {'占比%':>8}\n")
        for path in ['A', 'B']:
            n = (events['_path'] == path).sum()
            f.write(f"{path:<8} {n:>8} {n/len(events)*100:>8.2f}\n")
        f.write('\n=== 两种路径进入主升后的表现 ===\n')
        f.write(f"{'路径':<8} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}\n")
        for path in ['A', 'B']:
            sub = events[events['_path'] == path]
            n = len(sub)
            if n == 0:
                continue
            ret4 = sub['_ret_4w'].mean()
            ret8 = sub['_ret_8w'].mean()
            hr4 = sub['_hr_4w_max'].mean()
            zc_neg = sub['_zc_neg_4w'].mean() * 100
            f.write(f"{path:<8} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}\n")
        f.write('\n=== 周A趋路径细分（初 vs 储）===\n')
        f.write(f"{'来源':<8} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}\n")
        for src in ['初', '储']:
            sub = events[(events['_path'] == 'A') & (events['_prev_jie_first'] == src)]
            n = len(sub)
            if n == 0:
                continue
            ret4 = sub['_ret_4w'].mean()
            ret8 = sub['_ret_8w'].mean()
            hr4 = sub['_hr_4w_max'].mean()
            zc_neg = sub['_zc_neg_4w'].mean() * 100
            f.write(f"{src:<8} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}\n")
        f.write('\n=== 周B趋路径细分（进入主升时 WXAB 状态）===\n')
        f.write(f"{'WXAB状态':<10} {'事件数':>8} {'4周均收益%':>10} {'8周均收益%':>10} {'4周最高HR%':>10} {'4周内跌破ZC%':>12}\n")
        for ab_state, label in [(1, 'WXAB>0'), (0, 'WXAB<=0')]:
            sub = events[(events['_path'] == 'B') & (events['_ab_pos'] == ab_state)]
            n = len(sub)
            if n == 0:
                continue
            ret4 = sub['_ret_4w'].mean()
            ret8 = sub['_ret_8w'].mean()
            hr4 = sub['_hr_4w_max'].mean()
            zc_neg = sub['_zc_neg_4w'].mean() * 100
            f.write(f"{label:<10} {n:>8} {ret4:>10.3f} {ret8:>10.3f} {hr4:>10.3f} {zc_neg:>12.2f}\n")
    print(f'\n结果已保存到 {out}')

if __name__ == '__main__':
    main()