#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证用户观点：当DXCD>0（多头排列）时，日赢算法与5.1/5.2相比，只是提高了止损阈值
- 5.1/5.2（周线）：周ZC>0 持有，周ZC<0 退出（止损阈值=周线EMA26）
- 6.7日赢（当DXCD>0时）：日ZC>0 持有，日ZC<0 退出（止损阈值=日线EMA26）
- 日线EMA26比周线EMA26更敏感（更短周期），所以日赢算法止损更早
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日赢止损阈值.txt'
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
    # 未来N天日ZC（用于判断日线止损触发）
    wk['未来5天日ZC'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    wk['未来10天日ZC'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).min())
    # 未来N天周ZC（用于判断周线止损触发）
    wk['未来5天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    wk['未来10天周ZC'] = wk.groupby('fid')['周ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).min())
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
    # 日ZC>0 = 价格在日线DJC(EMA26)之上
    m_zc_pos = wk['日ZC'] > 0
    # 周ZC>0 = 价格在周线WJC(EMA26)之上
    m_zhouzc = wk['周ZC'] > 0
    # 周AB>0（周线正交）
    m_zhouab = wk['周AB'] > 0
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])

    lines = []
    lines.append('=' * 100)
    lines.append('验证用户观点：当DXCD>0时，日赢算法与5.1/5.2相比只是提高了止损阈值')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 当DXCD>0（多头排列）时，日赢 vs 5.1/5.2 ============
    lines.append('')
    lines.append('【1. 当DXCD>0（多头排列）时，日赢算法 vs 5.1/5.2】')
    lines.append('-' * 100)
    print_block(lines, '1.1 多头排列下的对比', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('DXCD>0(多头排列)全', m_dxcd_pos),
        ('5.1/5.2(周ZC>0+周AB>0)', m_zhouzc & m_zhouab),
        ('日赢(DXCD>0且日ZC>0)', m_dxcd_pos & m_zc_pos),
        ('日赢(DXCD>0且日ZC>0)+甲乙己', m_dxcd_pos & m_zc_pos & m_jiayiji),
        ('5.1/5.2 + 日赢(DXCD>0且日ZC>0)', m_zhouzc & m_zhouab & m_dxcd_pos & m_zc_pos),
    ])

    # ============ 2. 止损阈值对比：日ZC<0 vs 周ZC<0 ============
    lines.append('')
    lines.append('【2. 止损阈值对比：日线EMA26(日ZC<0) vs 周线EMA26(周ZC<0)】')
    lines.append('-' * 100)
    # 当DXCD>0且日ZC>0（日赢持有）时，未来N天日ZC<0（日线止损）vs 周ZC<0（周线止损）的触发比例
    m_hold = m_dxcd_pos & m_zc_pos
    g_hold = wk[m_hold]
    n_hold = len(g_hold)
    if n_hold > 0:
        # 未来5/10天日ZC<0（日线止损触发）
        pct_zc5 = (g_hold['未来5天日ZC'] < 0).mean() * 100
        pct_zc10 = (g_hold['未来10天日ZC'] < 0).mean() * 100
        # 未来5/10天周ZC<0（周线止损触发）
        pct_zhou5 = (g_hold['未来5天周ZC'] < 0).mean() * 100
        pct_zhou10 = (g_hold['未来10天周ZC'] < 0).mean() * 100
        lines.append(f'日赢持有(DXCD>0且日ZC>0)样本: {n_hold:,}')
        lines.append(f'未来5天日ZC<0(日线止损): {pct_zc5:.1f}%')
        lines.append(f'未来10天日ZC<0(日线止损): {pct_zc10:.1f}%')
        lines.append(f'未来5天周ZC<0(周线止损): {pct_zhou5:.1f}%')
        lines.append(f'未来10天周ZC<0(周线止损): {pct_zhou10:.1f}%')
        lines.append(f'日线止损比周线止损更早触发(5天): {pct_zc5 - pct_zhou5:.1f}pp')
        lines.append(f'日线止损比周线止损更早触发(10天): {pct_zc10 - pct_zhou10:.1f}pp')

    # ============ 3. 日线止损 vs 周线止损的收益 ============
    lines.append('')
    lines.append('【3. 日线止损 vs 周线止损的收益（未来5天）】')
    lines.append('-' * 100)
    # 日赢持有中，未来5天日ZC<0（日线止损触发）的样本
    m_zc_stop = m_hold & (wk['未来5天日ZC'] < 0)
    # 日赢持有中，未来5天周ZC<0（周线止损触发）的样本
    m_zhou_stop = m_hold & (wk['未来5天周ZC'] < 0)
    # 日赢持有中，未来5天日ZC≥0且周ZC≥0（都未止损）的样本
    m_no_stop = m_hold & (wk['未来5天日ZC'] >= 0) & (wk['未来5天周ZC'] >= 0)
    print_block(lines, '3.1 止损触发后的收益', [
        ('日赢持有(全)', m_hold),
        ('未来5天日ZC<0(日线止损)', m_zc_stop),
        ('未来5天周ZC<0(周线止损)', m_zhou_stop),
        ('未来5天都未止损', m_no_stop),
    ])

    # ============ 4. 日线止损 vs 周线止损：哪个更优？ ============
    lines.append('')
    lines.append('【4. 日线止损 vs 周线止损：哪个更优？】')
    lines.append('-' * 100)
    # 日线止损触发但周线未止损（日线先止损，周线还持有）
    m_zc_only = m_hold & (wk['未来5天日ZC'] < 0) & (wk['未来5天周ZC'] >= 0)
    # 周线止损触发但日线未止损（周线先止损，日线还持有）
    m_zhou_only = m_hold & (wk['未来5天日ZC'] >= 0) & (wk['未来5天周ZC'] < 0)
    print_block(lines, '4.1 止损先后对比', [
        ('日线先止损(日ZC<0但周ZC≥0)', m_zc_only),
        ('周线先止损(周ZC<0但日ZC≥0)', m_zhou_only),
        ('两者同时止损', m_hold & (wk['未来5天日ZC'] < 0) & (wk['未来5天周ZC'] < 0)),
        ('两者都未止损', m_no_stop),
    ])

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()