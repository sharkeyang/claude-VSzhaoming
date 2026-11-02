#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：DTZC≥5 近似堆垒 + 下破DJC的延续性
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings, re
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_堆垒DTZC.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, '柱排': 10,
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
    # 未来N天DXZD<0（下破DJD）
    for n in [3, 5, 10]:
        wk[f'未来{n}天DXZD<0'] = wk.groupby('fid')['DTZD'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    # 升连数
    wk['柱排_s'] = wk['柱排'].astype(str)
    wk['升连数'] = wk['柱排_s'].str.extract(r'Q(\d+)').astype(float)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_zc_pos = wk['日ZC'] > 0
    m_zc_neg = wk['日ZC'] < 0
    m_zd_pos = wk['DTZD'] > 0
    m_zd_neg = wk['DTZD'] < 0
    m_zhouzc = wk['周ZC'] > 0
    m_cd_pos = wk['DTCD'] > 0
    m_cd_neg = wk['DTCD'] < 0

    # DTZC≥5 = 日ZC≥5（站上DJC已5天以上）
    m_dtzc5 = wk['日ZC'] >= 5
    m_dtzc3 = wk['日ZC'] >= 3
    # 升连数≥5
    m_shenglian5 = wk['升连数'] >= 5

    lines = []
    lines.append('=' * 100)
    lines.append('验证：DTZC≥5 近似堆垒 + 下破DJC的延续性')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. DTZC≥5 vs 升连数≥5 的一致性 ============
    lines.append('')
    lines.append('【1】DTZC≥5 vs 升连数≥5 的一致性')
    lines.append('-' * 100)
    n_dtzc5 = m_dtzc5.sum()
    n_shenglian5 = m_shenglian5.sum()
    both = (m_dtzc5 & m_shenglian5).sum()
    lines.append(f'  DTZC≥5 样本: {n_dtzc5:,d}')
    lines.append(f'  升连数≥5 样本: {n_shenglian5:,d}')
    lines.append(f'  两者交集: {both:,d}')
    if n_dtzc5 > 0:
        lines.append(f'  DTZC≥5 中升连数≥5 占比: {both/n_dtzc5*100:.2f}%')
    if n_shenglian5 > 0:
        lines.append(f'  升连数≥5 中DTZC≥5 占比: {both/n_shenglian5*100:.2f}%')

    # ============ 2. 周线主升中，DTZC≥5 的堆垒效果 ============
    lines.append('')
    lines.append('【2】周线主升(5.1)中，DTZC≥5 的堆垒效果（对比升连数≥5）')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    m_operable = (sub['DTZD'] > 0) & (sub['日ZC'] > 0)
    m_operable_dtzc5 = m_operable & (sub['日ZC'] >= 5)
    m_operable_dtzc3 = m_operable & (sub['日ZC'] >= 3)
    m_operable_shenglian5 = m_operable & (sub['升连数'] >= 5)
    for name, m in [('周主升+两线之上', m_operable),
                    ('+DTZC≥5', m_operable_dtzc5),
                    ('+DTZC≥3', m_operable_dtzc3),
                    ('+升连数≥5', m_operable_shenglian5)]:
        g = sub[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 3. 下破DJC的延续性：下破DJC后，未来N天下破DJD的概率 ============
    lines.append('')
    lines.append('【3】下破DJC(DXZC<0)后，未来N天下破DJD(DXZD<0)的概率——下破DJC是否具有延续性')
    lines.append('-' * 100)
    g_zc_neg = wk[m_zc_neg]
    n = len(g_zc_neg)
    r3 = (g_zc_neg['未来3天DXZD<0']).mean() * 100
    r5 = (g_zc_neg['未来5天DXZD<0']).mean() * 100
    r10 = (g_zc_neg['未来10天DXZD<0']).mean() * 100
    lines.append(f'  下破DJC样本: {n:,d}')
    lines.append(f'  未来3天下破DJD: {r3:.2f}%')
    lines.append(f'  未来5天下破DJD: {r5:.2f}%')
    lines.append(f'  未来10天下破DJD: {r10:.2f}%')

    # ============ 4. 周线主升中，下破DJC的延续性 ============
    lines.append('')
    lines.append('【4】周线主升(5.1)中，下破DJC后未来N天下破DJD的概率')
    lines.append('-' * 100)
    sub_zhou = wk[m_zhouzc]
    g_zc_neg_zhou = sub_zhou[m_zc_neg[m_zhouzc]]
    n2 = len(g_zc_neg_zhou)
    r3b = (g_zc_neg_zhou['未来3天DXZD<0']).mean() * 100
    r5b = (g_zc_neg_zhou['未来5天DXZD<0']).mean() * 100
    r10b = (g_zc_neg_zhou['未来10天DXZD<0']).mean() * 100
    lines.append(f'  周线主升中下破DJC样本: {n2:,d}')
    lines.append(f'  未来3天下破DJD: {r3b:.2f}%')
    lines.append(f'  未来5天下破DJD: {r5b:.2f}%')
    lines.append(f'  未来10天下破DJD: {r10b:.2f}%')

    # ============ 5. 下破DJC但DJD还在，后续收益 ============
    lines.append('')
    lines.append('【5】下破DJC但DJD还在(DXZC<0且DXZD>0)，后续收益')
    lines.append('-' * 100)
    m_zc_neg_zd_pos = m_zc_neg & m_zd_pos
    g = wk[m_zc_neg_zd_pos]
    n3 = len(g)
    avg5 = g['未来5天涨幅'].mean()
    avg10 = g['未来10天涨幅'].mean()
    avg20 = g['未来20天涨幅'].mean()
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    lines.append(f'  下破DJC但DJD还在: 样本{n3:,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()