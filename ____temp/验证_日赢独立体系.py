#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新验证 日赢算法作为独立操作体系
用户观点（2026-10-29）：
1. 日赢算法是一个独立的、完整的操作体系，不依赖周5.1/5.2
2. 当周线不满足5.1/5.2时，日线仍在DJD网与DJC网内，可用日赢算法操作
3. 日赢算法满足时，可能转为5.1/5.2（锦上添花）
4. 日赢算法失效时（下破DJD），退出（退出后可再进），不会造成损失
5. "下破DJD退出可能过早"不是理由——退出后如果再次满足(DXZD>0且DXZC>0)可再次介入
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日赢独立体系.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 13, '日ZC': 14, '日ZE': 15,
    'BSHA': 19, '次日高幅': 26, '日等型': 43,
    'DTZD': 67, 'DTCD': 69, '周ZC': 87, '周AB': 91, '周ZA': 85,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', 'BSHA', '次日高幅', 'DTZD', 'DTCD', '周ZC', '周AB', '周ZA']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    wk['下日HR'] = wk['次日高幅']
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    # 未来N天周ZC（用于判断是否转为周5.1）
    wk['未来5天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    wk['未来10天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).max())
    wk['未来20天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(20, min_periods=1).max())
    # 未来N天日ZD（用于判断下破DJD）
    wk['未来5天日ZD'] = wk.groupby('fid')['DTZD'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    # 未来N天日ZC（用于判断下破DJC）
    wk['未来5天日ZC'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def stats_row(g):
    n = len(g)
    if n == 0:
        return None
    hr3 = (g['下日HR'] >= 3).mean() * 100
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    avg_hr = g['下日HR'].mean()
    avg_ret = g['涨幅'].mean()
    return hr3, hr5, avg_hr, avg_ret, n

def print_block(lines, title, items):
    lines.append('')
    lines.append(f'【{title}】')
    lines.append('-' * 100)
    lines.append(f'{"条件":<50s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"次日均HR":>8s} {"均涨幅":>8s}')
    lines.append('-' * 100)
    for name, mask in items:
        r = stats_row(wk[mask])
        if r is None:
            lines.append(f'{name:<50s} {"-":>10s} {"-":>8s} {"-":>8s} {"-":>8s} {"-":>8s}')
            continue
        hr3, hr5, avg_hr, avg_ret, n = r
        lines.append(f'{name:<50s} {n:>10,d} {hr3:>7.2f}% {hr5:>7.2f}% {avg_hr:>7.2f}% {avg_ret:>7.3f}%')

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    wk['DXCD_s'] = wk['DXCD'].astype(str)
    wk['DXAB_s'] = wk['DXAB'].astype(str)

    # DXCD>0 = BTCD>0（DJC>DJD，多头排列）
    m_dxcd_pos = wk['DTCD'] > 0
    # DXCD<0 = BTCD<0（DJC<DJD，空头排列）
    m_dxcd_neg = wk['DTCD'] < 0
    # 日ZC>0 = 价格在 DJC 之上
    m_zc_pos = wk['日ZC'] > 0
    # 日ZD>0 = 价格在 DJD 之上
    m_zd_pos = wk['DTZD'] > 0
    # 日赢丘内 = (DXCD>0 且 日ZC>0) 或 (DXCD<0 且 日ZD>0)
    m_yingqiu = (m_dxcd_pos & m_zc_pos) | (m_dxcd_neg & m_zd_pos)
    # 周5.1条件：周ZC>0（周线主升）
    m_zhouzc = wk['周ZC'] > 0
    # 周5.1完整条件：周ZC>0 + 周AB>0
    m_zhouab = wk['周AB'] > 0
    m_zhou51 = m_zhouzc & m_zhouab
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])

    lines = []
    lines.append('=' * 100)
    lines.append('重新验证 日赢算法作为独立操作体系')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 日赢算法完整体系 ============
    lines.append('')
    lines.append('【1. 日赢算法完整体系（DJD网与DJC网内持有）】')
    lines.append('-' * 100)
    # 日赢丘内 = DJD网与DJC网内
    # 细分：DXCD>0且日ZC>0（DJC网内）、DXCD<0且日ZD>0（DJD网内）
    m_djc_net = m_dxcd_pos & m_zc_pos  # DJC网内（多头排列+DJC之上）
    m_djd_net = m_dxcd_neg & m_zd_pos  # DJD网内（空头排列+DJD之上）
    print_block(lines, '1.1 日赢丘内细分（DJC网 vs DJD网）', [
        ('日赢丘内(全)', m_yingqiu),
        ('DJC网内(DXCD>0且日ZC>0)', m_djc_net),
        ('DJD网内(DXCD<0且日ZD>0)', m_djd_net),
        ('DJC网内 + 甲乙己', m_djc_net & m_jiayiji),
        ('DJD网内 + 甲乙己', m_djd_net & m_jiayiji),
    ])

    # ============ 2. 日赢算法 vs 周5.1/5.2 ============
    lines.append('')
    lines.append('【2. 日赢算法 vs 周5.1/5.2】')
    lines.append('-' * 100)
    print_block(lines, '2.1 日赢算法 vs 周5.1', [
        ('日赢丘内(全)', m_yingqiu),
        ('日赢丘内 + 周ZC>0', m_yingqiu & m_zhouzc),
        ('日赢丘内 + 周ZC≤0', m_yingqiu & ~m_zhouzc),
        ('周5.1已满足(周ZC>0且周AB>0)', m_zhou51),
        ('日赢丘内 + 周5.1已满足', m_yingqiu & m_zhou51),
        ('日赢丘内 + 周5.1不满足', m_yingqiu & ~m_zhou51),
    ])

    # ============ 3. 日赢算法在"不能转为5.1/5.2但仍在DJD/DJC网内"的价值 ============
    lines.append('')
    lines.append('【3. 日赢算法在"不能转为5.1/5.2但仍在DJD/DJC网内"的价值】')
    lines.append('-' * 100)
    # 用户场景：日赢丘内，但周5.1不满足（周ZC≤0 或 周AB≤0）
    m_scene = m_yingqiu & ~m_zhou51
    print_block(lines, '3.1 日赢丘内但周5.1不满足', [
        ('日赢丘内 + 周5.1不满足', m_scene),
        ('  其中 DJC网内', m_scene & m_djc_net),
        ('  其中 DJD网内', m_scene & m_djd_net),
        ('  其中 DJC网内 + 甲乙己', m_scene & m_djc_net & m_jiayiji),
        ('  其中 DJD网内 + 甲乙己', m_scene & m_djd_net & m_jiayiji),
    ])

    # ============ 4. 下破DJD退出后再次介入 ============
    lines.append('')
    lines.append('【4. 下破DJD退出后，再次满足(DXZD>0且DXZC>0)可再次介入】')
    lines.append('-' * 100)
    # 用户场景中，未来5天下破DJD的样本
    m_break_zd = m_scene & (wk['未来5天日ZD'] < 0)
    # 下破DJD后，未来5天再次满足(DXZD>0且DXZC>0)的比例
    g_break = wk[m_break_zd]
    n_break = len(g_break)
    if n_break > 0:
        # 未来5天日ZD>0且日ZC>0（再次满足）的比例
        m_reenter = m_break_zd & (wk['未来5天日ZD'] > 0) & (wk['未来5天日ZC'] > 0)
        pct_reenter = (m_reenter).sum() / n_break * 100
        lines.append(f'下破DJD后未来5天再次满足(DXZD>0且DXZC>0): {pct_reenter:.1f}%')
        # 下破DJD后未来5天日ZD>0（回到DJD之上）的比例
        pct_back = (wk.loc[m_break_zd.index, '未来5天日ZD'] > 0).mean() * 100
        lines.append(f'下破DJD后未来5天回到DJD之上: {pct_back:.1f}%')

    # ============ 5. 日赢算法完整策略模拟 ============
    lines.append('')
    lines.append('【5. 日赢算法完整策略模拟（丘内持有、丘外空仓）】')
    lines.append('-' * 100)
    g_in = wk[m_yingqiu]
    g_out = wk[~m_yingqiu]
    avg_in = g_in['涨幅'].mean()
    avg_out = g_out['涨幅'].mean()
    pct_in = len(g_in) / len(wk) * 100
    lines.append(f'日赢丘内持有: 平均涨幅 {avg_in:.3f}% (覆盖 {pct_in:.1f}% 时间)')
    lines.append(f'日赢丘外(空仓): 平均涨幅 {avg_out:.3f}%')
    lines.append(f'策略(丘内持有): 平均涨幅 {avg_in:.3f}% × 覆盖 {pct_in:.1f}% = {avg_in*pct_in/100:.3f}%')
    lines.append(f'始终持有: 平均涨幅 {wk["涨幅"].mean():.3f}%')
    lines.append(f'策略/始终持有: {avg_in*pct_in/100/wk["涨幅"].mean():.2f}x')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()