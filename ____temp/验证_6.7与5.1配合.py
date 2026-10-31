#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研究 6.7日赢算法 与 5.1+5.2（方法周A趋/周B趋）的配合
配合逻辑（不同周期）：
- 周线5.1/5.2定方向（大周期）：周线主升（WXZC>0）时，用5.1/5.2持有
- 日线6.7定时机（小周期）：日线DJD/DJC网内时，用6.7操作
配合场景：
1. 周线主升(5.1/5.2) + 日线DJD/DJC网内(6.7) = 最强持有区
2. 周线主升(5.1/5.2) + 日线DJD/DJC网外(6.7退出) = 日线6.7先退出，避免回撤
3. 周线非主升(5.1/5.2不满足) + 日线DJD/DJC网内(6.7) = 日线6.7独立操作
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_6.7与5.1配合.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 13, '日ZC': 14, '日ZE': 15,
    'BSHA': 19, '次日高幅': 26, '日等型': 43,
    'DTZD': 67, 'DTCD': 69, '周ZC': 87, '周AB': 91, '周ZB': 86, '周ZA': 85,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', 'BSHA', '次日高幅', 'DTZD', 'DTCD', '周ZC', '周AB', '周ZB', '周ZA']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    wk['下日HR'] = wk['次日高幅']
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    # 未来N天周ZC（用于判断周线是否转为5.1）
    wk['未来5天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    wk['未来10天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).max())
    wk['未来20天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(20, min_periods=1).max())
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
    lines.append(f'{"条件":<52s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"次日均HR":>8s} {"均涨幅":>8s}')
    lines.append('-' * 100)
    for name, mask in items:
        r = stats_row(wk[mask])
        if r is None:
            lines.append(f'{name:<52s} {"-":>10s} {"-":>8s} {"-":>8s} {"-":>8s} {"-":>8s}')
            continue
        hr3, hr5, avg_hr, avg_ret, n = r
        lines.append(f'{name:<52s} {n:>10,d} {hr3:>7.2f}% {hr5:>7.2f}% {avg_hr:>7.2f}% {avg_ret:>7.3f}%')

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
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])

    # ============ 5.1/5.2 周线条件 ============
    # 5.1 方法周A趋：周ZC>0（周线站上WJC）持有
    m_zhouzc = wk['周ZC'] > 0
    # 5.1 完整：周ZC>0 + 周AB>0（龙骨正交）
    m_zhouab = wk['周AB'] > 0
    m_zhou51 = m_zhouzc & m_zhouab
    # 5.2 方法周B趋：周ZC>0 时劫后（周ZB<0）以龙骨转正（周AB>0）再次介入
    m_zhouzb = wk['周ZB'] > 0
    m_zhou52 = m_zhouzc & m_zhouab  # 简化：周B趋在周A趋基础上劫后介入，此处用周ZC>0+周AB>0近似

    lines = []
    lines.append('=' * 100)
    lines.append('研究 6.7日赢算法 与 5.1+5.2（方法周A趋/周B趋）的配合')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 单独使用对比 ============
    lines.append('')
    lines.append('【1. 单独使用对比：5.1/5.2 vs 6.7】')
    lines.append('-' * 100)
    print_block(lines, '1.1 单独使用', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('5.1周A趋(周ZC>0+周AB>0)', m_zhou51),
        ('5.1周A趋(仅周ZC>0)', m_zhouzc),
        ('6.7日赢(DJD&DJC双丘)', m_yingqiu),
        ('6.7日赢 + 甲乙己', m_yingqiu & m_jiayiji),
    ])

    # ============ 2. 配合场景 ============
    lines.append('')
    lines.append('【2. 配合场景：周线5.1/5.2定方向 + 日线6.7定时机】')
    lines.append('-' * 100)
    print_block(lines, '2.1 周线主升 + 日线6.7', [
        ('场景A: 周5.1 + 日6.7(最强持有区)', m_zhou51 & m_yingqiu),
        ('场景B: 周5.1 + 日6.7 + 甲乙己', m_zhou51 & m_yingqiu & m_jiayiji),
        ('场景C: 周ZC>0 + 日6.7', m_zhouzc & m_yingqiu),
        ('场景D: 周ZC>0 + 日6.7 + 甲乙己', m_zhouzc & m_yingqiu & m_jiayiji),
    ])

    # ============ 3. 周线主升但日线6.7退出 ============
    lines.append('')
    lines.append('【3. 周线主升(5.1)但日线6.7退出(网外)】')
    lines.append('-' * 100)
    print_block(lines, '3.1 周线主升 + 日线网外', [
        ('周5.1 + 日6.7网外(6.7退出)', m_zhou51 & ~m_yingqiu),
        ('周ZC>0 + 日6.7网外', m_zhouzc & ~m_yingqiu),
        ('对比: 周5.1(全)', m_zhou51),
        ('对比: 周ZC>0(全)', m_zhouzc),
    ])

    # ============ 4. 周线非主升但日线6.7网内 ============
    lines.append('')
    lines.append('【4. 周线非主升(5.1不满足)但日线6.7网内】')
    lines.append('-' * 100)
    print_block(lines, '4.1 周线非主升 + 日线网内', [
        ('周5.1不满足 + 日6.7网内(6.7独立操作)', ~m_zhou51 & m_yingqiu),
        ('周ZC≤0 + 日6.7网内', ~m_zhouzc & m_yingqiu),
        ('周ZC≤0 + 日6.7网内 + 甲乙己', ~m_zhouzc & m_yingqiu & m_jiayiji),
        ('对比: 日6.7(全)', m_yingqiu),
    ])

    # ============ 5. 配合 vs 单独 ============
    lines.append('')
    lines.append('【5. 配合 vs 单独：哪个更优？】')
    lines.append('-' * 100)
    print_block(lines, '5.1 综合对比', [
        ('单独5.1(周ZC>0+周AB>0)', m_zhou51),
        ('单独6.7(日DJD&DJC双丘)', m_yingqiu),
        ('配合: 周5.1 + 日6.7', m_zhou51 & m_yingqiu),
        ('配合: 周5.1 + 日6.7 + 甲乙己', m_zhou51 & m_yingqiu & m_jiayiji),
        ('配合: 周ZC>0 + 日6.7', m_zhouzc & m_yingqiu),
        ('配合: 周ZC>0 + 日6.7 + 甲乙己', m_zhouzc & m_yingqiu & m_jiayiji),
    ])

    # ============ 6. 日线6.7提前介入，周线5.1确认 ============
    lines.append('')
    lines.append('【6. 日线6.7提前介入，周线5.1确认】')
    lines.append('-' * 100)
    # 日线6.7网内但周线5.1不满足（提前介入）
    m_early = m_yingqiu & ~m_zhou51
    # 这些样本未来N天转为周5.1的比例
    g_early = wk[m_early]
    n_early = len(g_early)
    if n_early > 0:
        for days, col in [('5天', '未来5天周ZC'), ('10天', '未来10天周ZC'), ('20天', '未来20天周ZC')]:
            pct = (g_early[col] > 0).mean() * 100
            lines.append(f'日6.7提前介入(周5.1不满足)后，未来{days}内转为周ZC>0: {pct:.1f}%')
        lines.append(f'日6.7提前介入样本: {n_early:,}')
        lines.append(f'日6.7提前介入均涨幅: {g_early["涨幅"].mean():.3f}%')
        lines.append(f'日6.7提前介入次日P3: {(g_early["下日HR"]>=3).mean()*100:.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()