#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证剩余命题：P3.1/P3.2/P4.6/P4.8
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_截损命题2.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 16, '日ZC': 17, '日ZE': 18,
    '次日高幅': 28, 'DTZD': 69, 'DTCD': 71,
    '周ZC': 91, '周AB': 95,
}

usecols = sorted(set(COL.values()))
colnames = {v: k for k, v in COL.items()}

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk', usecols=usecols)
            if len(df) >= 6:
                df = df.rename(columns=colnames)
                df['fid'] = i
                dfs.append(df)
        except Exception:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', '次日高幅', 'DTZD', 'DTCD', '周ZC', '周AB']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    # 未来收益
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['未来5天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(5, min_periods=1).sum())
    wk['未来10天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(10, min_periods=1).sum())
    wk['未来20天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(20, min_periods=1).sum())
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    wk['未来5天最低涨幅'] = wk.groupby('fid')['涨幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    # 未来N天周ZC<0
    for n in [5, 10, 20]:
        wk[f'未来{n}天周ZC<0'] = wk.groupby('fid')['周ZC'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_za_pos = wk['日ZA'] > 0
    m_za_neg = wk['日ZA'] < 0
    m_zc_pos = wk['日ZC'] > 0
    m_zc_neg = wk['日ZC'] < 0
    m_zd_pos = wk['DTZD'] > 0
    m_zd_neg = wk['DTZD'] < 0
    m_ze_pos = wk['日ZE'] > 0
    m_ze_neg = wk['日ZE'] < 0
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    wk['DXCD_s'] = wk['DXCD'].astype(str)
    m_cd_pos = wk['DTCD'] > 0
    m_cd_neg = wk['DTCD'] < 0

    wk['DXAB_s'] = wk['DXAB'].astype(str)
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    m_bingdingwu = wk['DXAB_s'].str[0].isin(['c', 'z', 'y'])

    # 柱排
    wk['柱排_s'] = wk['柱排'].astype(str)
    m_duilei = wk['柱排_s'].str.contains('对垒', na=False)  # 对垒柱排

    lines = []
    lines.append('=' * 100)
    lines.append('验证剩余命题：P3.1/P3.2/P4.6/P4.8')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ P3.1: DXCD<0时，上破DJD后再介入 vs DJD之下但DJC之上对垒柱排 ============
    lines.append('')
    lines.append('【P3.1】DXCD<0(空头排列)时，上破DJD后再介入 vs DJD之下但DJC之上介入')
    lines.append('-' * 100)
    sub = wk[m_cd_neg]
    # 上破DJD：DXZD>0
    m_zd_pos2 = sub['DTZD'] > 0
    # DJD之下但DJC之上：DXZD<0 且 DXZC>0
    m_zd_neg_zc_pos = (sub['DTZD'] < 0) & (sub['日ZC'] > 0)
    # DJD之下但DJC之上 + 对垒柱排
    m_zd_neg_zc_pos_dui = m_zd_neg_zc_pos & sub['柱排_s'].str.contains('对垒', na=False)
    for name, m in [('上破DJD后介入', m_zd_pos2), ('DJD之下但DJC之上', m_zd_neg_zc_pos),
                    ('DJD之下DJC之上+对垒', m_zd_neg_zc_pos_dui)]:
        g = sub[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P3.2: 下破时，等已下破DJD再退出 vs 已下破DJC即将下破DJD就退出 ============
    lines.append('')
    lines.append('【P3.2】下破时，等已下破DJD再退出 vs 已下破DJC即将下破DJD就退出')
    lines.append('-' * 100)
    # 已下破DJC即将下破DJD：DXZC<0 且 DXZD>0（DJD还在，但已下破DJC）
    m_zc_neg_zd_pos = (wk['日ZC'] < 0) & (wk['DTZD'] > 0)
    # 已下破DJD：DXZD<0
    m_zd_neg2 = wk['DTZD'] < 0
    for name, m in [('已下破DJC但DJD还在(提前退)', m_zc_neg_zd_pos), ('已下破DJD(确认退)', m_zd_neg2)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P4.6/P4.8: 可操作范围 vs 可获利范围 ============
    lines.append('')
    lines.append('【P4.6/P4.8】可操作范围(5.1+5.2+非对称日类)内，再按可获利范围(日级别主升)筛选')
    lines.append('-' * 100)
    # 可操作范围 = 周线主升(WXZC>0) + 日线两线之上(DXZD>0且DXZC>0)
    m_operable = m_zhouzc & m_zd_pos & m_zc_pos  # 可操作范围
    # 可获利范围 = 可操作范围内 + 站上DJA(DXZA>0) 或 甲乙己
    m_profit_za = m_operable & m_za_pos  # 可操作范围 + 站上DJA
    m_profit_jiayiji = m_operable & m_jiayiji  # 可操作范围 + 甲乙己
    m_profit_za_jiayiji = m_operable & m_za_pos & m_jiayiji  # 可操作范围 + 站上DJA + 甲乙己
    for name, m in [('可操作范围(周主升+两线之上)', m_operable),
                    ('+站上DJA', m_profit_za),
                    ('+甲乙己', m_profit_jiayiji),
                    ('+站上DJA+甲乙己', m_profit_za_jiayiji)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<28s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P4.6补充: 可操作范围内，下破DJB/DJA作为止盈条件 ============
    lines.append('')
    lines.append('【P4.6补充】可操作范围内，已有较大涨幅后，下破DJA/DJB作为止盈条件')
    lines.append('-' * 100)
    # 可操作范围内 + 站上DJA（已获利），下破DJA后 vs 继续持有
    g_profit = wk[m_profit_za]
    # 下破DJA（DXZA<0）作为止盈信号
    m_exit_za = m_profit_za & m_za_neg
    g_exit = wk[m_exit_za]
    n_exit = len(g_exit)
    avg5_exit = g_exit['未来5天涨幅'].mean()
    avg10_exit = g_exit['未来10天涨幅'].mean()
    avg20_exit = g_exit['未来20天涨幅'].mean()
    lines.append(f'  可操作范围+站上DJA后下破DJA(止盈): 样本{n_exit:>10,d} 5天{avg5_exit:>7.3f}% 10天{avg10_exit:>7.3f}% 20天{avg20_exit:>7.3f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()