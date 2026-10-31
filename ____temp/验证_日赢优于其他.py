#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用全部数据验证 日赢算法(6.7) 优于其他算法
对比算法：5.1/5.2/6.0/6.1/6.2/6.3/6.4/6.5/6.6/6.7
数据源：谕组日 CSV（131列，GBK编码），全量3449文件
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日赢优于其他.txt'
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

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    wk['DXCD_s'] = wk['DXCD'].astype(str)
    wk['DXAB_s'] = wk['DXAB'].astype(str)
    wk['柱排_s'] = wk['柱排'].astype(str)

    # ============ 基础条件 ============
    # DXCD>0 = BTCD>0（DJC>DJD，多头排列）
    m_dxcd_pos = wk['DTCD'] > 0
    m_dxcd_neg = wk['DTCD'] < 0
    # 日ZC>0 / 日ZD>0 / 日ZA>0 / 日ZE>0
    m_zc_pos = wk['日ZC'] > 0
    m_zd_pos = wk['DTZD'] > 0
    m_za_pos = wk['日ZA'] > 0
    m_ze_pos = wk['日ZE'] > 0
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    # 沃土：DXZE>0 + CD上/忐
    m_wo = m_ze_pos & wk['DXCD_s'].isin(['上', '忐'])
    # 升连：柱排以"升.尾连"开头
    m_shenglian = wk['柱排_s'].str.startswith('升.尾连', na=False)
    # 涨幅≥2%
    m_zhangfu2 = wk['涨幅'] >= 2
    # BSHA5
    m_bsha5 = wk['BSHA'] >= 5
    # 阴柱（涨幅<0）
    m_yin = wk['涨幅'] < 0
    # 周ZC>0 / 周AB>0 / 周ZB>0
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0
    m_zhouzb = wk['周ZB'] > 0

    # ============ 各算法条件 ============
    # 5.1 方法周A趋：周ZC>0
    m_51 = m_zhouzc
    # 5.2 方法周B趋：周ZC>0 + 周AB>0
    m_52 = m_zhouzc & m_zhouab
    # 6.0 方法日A趋：周ZC>0（不看日类，同5.1）
    m_60 = m_zhouzc
    # 6.1 方法日B趋：周ZC>0 + 日ZC>0
    m_61 = m_zhouzc & m_zc_pos
    # 6.2 方法日C冲：周ZC>0 + 日ZA>0
    m_62 = m_zhouzc & m_za_pos
    # 6.3 方法日H冲：沃土+甲乙己+升连≥2%
    m_63 = m_wo & m_jiayiji & m_shenglian & m_zhangfu2
    # 6.4 方法日I冲：沃土+甲乙己+BSHA5
    m_64 = m_wo & m_jiayiji & m_bsha5
    # 6.5 方法日M漏：日ZA>0 + 阴柱
    m_65 = m_za_pos & m_yin
    # 6.6 方法日N漏：跌破DJA/DJB低吸（日ZA<0 或 日ZB<0，此处用日ZA<0近似）
    m_66 = m_za_pos & m_yin  # 简化：日ZA>0阴柱（与6.5类似，但6.6是跌破DJA低吸）
    # 6.7 方法日赢算法：DJD&DJC双丘
    m_67 = (m_dxcd_pos & m_zc_pos) | (m_dxcd_neg & m_zd_pos)

    lines = []
    lines.append('=' * 100)
    lines.append('用全部数据验证 日赢算法(6.7) 优于其他算法')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 各算法收益对比 ============
    lines.append('')
    lines.append('【1. 各算法收益对比（按均涨幅排序）】')
    lines.append('-' * 100)
    lines.append(f'{"算法":<52s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"次日均HR":>8s} {"均涨幅":>8s}')
    lines.append('-' * 100)

    algos = [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('5.1 方法周A趋(周ZC>0)', m_51),
        ('5.2 方法周B趋(周ZC>0+周AB>0)', m_52),
        ('6.0 方法日A趋(周ZC>0不看日类)', m_60),
        ('6.1 方法日B趋(周ZC>0+日ZC>0)', m_61),
        ('6.2 方法日C冲(周ZC>0+日ZA>0)', m_62),
        ('6.3 方法日H冲(沃土+甲乙己+升连≥2%)', m_63),
        ('6.4 方法日I冲(沃土+甲乙己+BSHA5)', m_64),
        ('6.5 方法日M漏(日ZA>0+阴柱)', m_65),
        ('6.7 方法日赢算法(DJD&DJC双丘)', m_67),
        ('6.7 日赢 + 甲乙己', m_67 & m_jiayiji),
        ('6.7 日赢 + 周ZC>0', m_67 & m_zhouzc),
        ('6.7 日赢 + 周ZC>0 + 周AB>0', m_67 & m_zhouzc & m_zhouab),
    ]

    results = []
    for name, mask in algos:
        r = stats_row(wk[mask])
        if r is None:
            results.append((name, None))
            continue
        hr3, hr5, avg_hr, avg_ret, n = r
        results.append((name, (hr3, hr5, avg_hr, avg_ret, n)))

    # 按均涨幅排序
    results_sorted = sorted(results, key=lambda x: x[1][3] if x[1] else -999, reverse=True)
    for name, r in results_sorted:
        if r is None:
            lines.append(f'{name:<52s} {"-":>10s} {"-":>8s} {"-":>8s} {"-":>8s} {"-":>8s}')
            continue
        hr3, hr5, avg_hr, avg_ret, n = r
        lines.append(f'{name:<52s} {n:>10,d} {hr3:>7.2f}% {hr5:>7.2f}% {avg_hr:>7.2f}% {avg_ret:>7.3f}%')

    # ============ 2. 日赢 vs 各算法 的均涨幅对比 ============
    lines.append('')
    lines.append('【2. 日赢算法 vs 各算法 的均涨幅对比】')
    lines.append('-' * 100)
    r_67 = stats_row(wk[m_67])
    r_67_jiayiji = stats_row(wk[m_67 & m_jiayiji])
    if r_67 and r_67_jiayiji:
        avg_67 = r_67[3]
        avg_67_j = r_67_jiayiji[3]
        lines.append(f'6.7 日赢算法均涨幅: {avg_67:.3f}%')
        lines.append(f'6.7 日赢+甲乙己均涨幅: {avg_67_j:.3f}%')
        lines.append('')
        for name, mask in algos:
            if '6.7' in name or '基线' in name:
                continue
            r = stats_row(wk[mask])
            if r is None:
                continue
            avg = r[3]
            diff = avg_67 - avg
            diff_j = avg_67_j - avg
            lines.append(f'{name:<52s} 均涨幅 {avg:>7.3f}% | 日赢领先 {diff:>+7.3f}pp | 日赢+甲乙己领先 {diff_j:>+7.3f}pp')

    # ============ 3. 日赢 vs 各算法 的5天P3对比 ============
    lines.append('')
    lines.append('【3. 日赢算法 vs 各算法 的5天P3对比】')
    lines.append('-' * 100)
    if r_67 and r_67_jiayiji:
        p5_67 = r_67[1]
        p5_67_j = r_67_jiayiji[1]
        lines.append(f'6.7 日赢算法5天P3: {p5_67:.2f}%')
        lines.append(f'6.7 日赢+甲乙己5天P3: {p5_67_j:.2f}%')
        lines.append('')
        for name, mask in algos:
            if '6.7' in name or '基线' in name:
                continue
            r = stats_row(wk[mask])
            if r is None:
                continue
            p5 = r[1]
            diff = p5_67 - p5
            diff_j = p5_67_j - p5
            lines.append(f'{name:<52s} 5天P3 {p5:>7.2f}% | 日赢领先 {diff:>+7.2f}pp | 日赢+甲乙己领先 {diff_j:>+7.2f}pp')

    # ============ 4. 日赢 vs 各算法 的次日P3对比 ============
    lines.append('')
    lines.append('【4. 日赢算法 vs 各算法 的次日P3对比】')
    lines.append('-' * 100)
    if r_67 and r_67_jiayiji:
        p3_67 = r_67[0]
        p3_67_j = r_67_jiayiji[0]
        lines.append(f'6.7 日赢算法次日P3: {p3_67:.2f}%')
        lines.append(f'6.7 日赢+甲乙己次日P3: {p3_67_j:.2f}%')
        lines.append('')
        for name, mask in algos:
            if '6.7' in name or '基线' in name:
                continue
            r = stats_row(wk[mask])
            if r is None:
                continue
            p3 = r[0]
            diff = p3_67 - p3
            diff_j = p3_67_j - p3
            lines.append(f'{name:<52s} 次日P3 {p3:>7.2f}% | 日赢领先 {diff:>+7.2f}pp | 日赢+甲乙己领先 {diff_j:>+7.2f}pp')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()