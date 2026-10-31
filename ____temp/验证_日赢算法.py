#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 日层赢算法（DJD&DJC 双丘）的必赢性
算法逻辑：
- DXCD>0（价格在 DJC 之上，DXCD∈{上,忐,忠}）时，以 DJC 丘为准（DXZC>0 持有，DXZC<0 退出）
- DXCD<0（价格在 DJC 之下，DXCD∈{下,忑}）时，以 DJD 丘为准（DXZD>0 持有，DXZD<0 退出）
- 若后续转为 DXCD>0，则改为以 DJC 为准
本质：以 DJC&DJD 双丘捕捉上升趋势
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日赢算法.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 13, '日ZC': 14, '日ZE': 15,
    'BSHA': 19, '次日高幅': 26, '日等型': 43,
    'DTZD': 67, 'DTCD': 69, '周ZC': 87, '周AB': 91,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', 'BSHA', '次日高幅', 'DTZD', 'DTCD', '周ZC', '周AB']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    wk['下日HR'] = wk['次日高幅']
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def stats_row(g):
    n = len(g)
    if n == 0:
        return None
    hr3 = (g['下日HR'] >= 3).mean() * 100
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    avg_hr = g['下日HR'].mean()
    return hr3, hr5, avg_hr, n

def print_block(lines, title, items):
    lines.append('')
    lines.append(f'【{title}】')
    lines.append('-' * 90)
    lines.append(f'{"条件":<46s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"次日均HR":>8s}')
    lines.append('-' * 90)
    for name, mask in items:
        r = stats_row(wk[mask])
        if r is None:
            lines.append(f'{name:<46s} {"-":>10s} {"-":>8s} {"-":>8s} {"-":>8s}')
            continue
        hr3, hr5, avg_hr, n = r
        lines.append(f'{name:<46s} {n:>10,d} {hr3:>7.2f}% {hr5:>7.2f}% {avg_hr:>7.2f}%')

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    wk['DXCD_s'] = wk['DXCD'].astype(str)
    wk['DXAB_s'] = wk['DXAB'].astype(str)

    # DXCD>0 = BTCD>0（DJC>DJD，多头排列），此时 DXCD∈{上,中,下}
    m_dxcd_pos = wk['DTCD'] > 0
    # DXCD<0 = BTCD<0（DJC<DJD，空头排列），此时 DXCD∈{忐,忠,忑}
    m_dxcd_neg = wk['DTCD'] < 0
    # 日ZC>0 = 价格在 DJC 之上
    m_zc_pos = wk['日ZC'] > 0
    # 日ZD>0 = 价格在 DJD 之上
    m_zd_pos = wk['DTZD'] > 0
    # 日ZE>0 = 价格在 DJE 之上
    m_ze_pos = wk['日ZE'] > 0
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    # 周ZC>0（周线主升）
    m_zhouzc = wk['周ZC'] > 0
    # 周AB>0（周线正交）
    m_zhouab = wk['周AB'] > 0

    lines = []
    lines.append('=' * 90)
    lines.append('验证 日层赢算法（DJD&DJC 双丘）的必赢性')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 90)

    # ============ 1. 日赢丘 = DJC&DJD 双丘 ============
    lines.append('')
    lines.append('【1. 日赢丘 = DJC&DJD 双丘（DXCD>0 用 DJC，DXCD<0 用 DJD）】')
    lines.append('-' * 90)
    # 日赢丘内 = (DXCD>0 且 日ZC>0) 或 (DXCD<0 且 日ZD>0)
    # DXCD>0 = DJC>DJD（多头排列），用 DJC 丘（日ZC>0）
    # DXCD<0 = DJC<DJD（空头排列），用 DJD 丘（日ZD>0）
    m_yingqiu = (m_dxcd_pos & m_zc_pos) | (m_dxcd_neg & m_zd_pos)
    # 日赢丘外 = 其他
    m_not_yingqiu = ~m_yingqiu

    print_block(lines, '1.1 日赢丘内 vs 丘外', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('日赢丘内(DJC&DJD双丘)', m_yingqiu),
        ('日赢丘外', m_not_yingqiu),
        ('日赢丘内 + 甲乙己', m_yingqiu & m_jiayiji),
        ('日赢丘内 + 周ZC>0', m_yingqiu & m_zhouzc),
        ('日赢丘内 + 周ZC>0 + 周AB>0', m_yingqiu & m_zhouzc & m_zhouab),
    ])

    # ============ 2. 对比：DJC丘 vs DJD丘 vs 双丘 ============
    lines.append('')
    lines.append('【2. 对比：DJC丘 vs DJD丘 vs 双丘】')
    lines.append('-' * 90)
    print_block(lines, '2.1 各丘对比', [
        ('DJC丘(日ZC>0)', m_zc_pos),
        ('DJD丘(日ZD>0)', m_zd_pos),
        ('DJE丘(日ZE>0)', m_ze_pos),
        ('日赢双丘(DJC&DJD)', m_yingqiu),
        ('DJC丘 + 甲乙己', m_zc_pos & m_jiayiji),
        ('DJD丘 + 甲乙己', m_zd_pos & m_jiayiji),
        ('日赢双丘 + 甲乙己', m_yingqiu & m_jiayiji),
    ])

    # ============ 3. 日赢丘内 vs 周类算法（5.1/5.2） ============
    lines.append('')
    lines.append('【3. 日赢丘 vs 周类算法（5.1/5.2）】')
    lines.append('-' * 90)
    print_block(lines, '3.1 日赢丘 vs 周线主升', [
        ('日赢双丘', m_yingqiu),
        ('日赢双丘 + 周ZC>0', m_yingqiu & m_zhouzc),
        ('周ZC>0(周线主升)', m_zhouzc),
        ('周ZC>0 + 周AB>0(5.1选股)', m_zhouzc & m_zhouab),
        ('日赢双丘 + 周ZC>0 + 周AB>0', m_yingqiu & m_zhouzc & m_zhouab),
    ])

    # ============ 4. 日赢丘内 vs 丘外 的收益贡献 ============
    lines.append('')
    lines.append('【4. 日赢丘内 vs 丘外 的收益贡献】')
    lines.append('-' * 90)
    # 计算日赢丘内外的平均涨幅
    g_in = wk[m_yingqiu]
    g_out = wk[m_not_yingqiu]
    lines.append(f'日赢丘内: 样本 {len(g_in):,}, 平均涨幅 {g_in["涨幅"].mean():.3f}%, 平均高幅 {g_in["高幅"].mean():.3f}%')
    lines.append(f'日赢丘外: 样本 {len(g_out):,}, 平均涨幅 {g_out["涨幅"].mean():.3f}%, 平均高幅 {g_out["高幅"].mean():.3f}%')
    lines.append(f'日赢丘内涨幅贡献占比: {g_in["涨幅"].sum()/(g_in["涨幅"].sum()+g_out["涨幅"].sum())*100:.1f}%')

    # ============ 5. 日赢丘内 持有 vs 不持有 ============
    lines.append('')
    lines.append('【5. 日赢丘内 持有 vs 不持有（模拟策略）】')
    lines.append('-' * 90)
    # 简化模拟：日赢丘内持有（吃平均涨幅），丘外空仓
    # 对比：始终持有
    avg_all = wk['涨幅'].mean()
    avg_in = g_in['涨幅'].mean()
    avg_out = g_out['涨幅'].mean()
    pct_in = len(g_in) / len(wk) * 100
    lines.append(f'始终持有: 平均涨幅 {avg_all:.3f}%')
    lines.append(f'日赢丘内持有: 平均涨幅 {avg_in:.3f}% (覆盖 {pct_in:.1f}% 时间)')
    lines.append(f'日赢丘外(空仓): 平均涨幅 {avg_out:.3f}%')
    lines.append(f'策略(丘内持有): 平均涨幅 {avg_in:.3f}% × 覆盖 {pct_in:.1f}% = {avg_in*pct_in/100:.3f}%')

    lines.append('')
    lines.append('=' * 90)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()