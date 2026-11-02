#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证"截损条件"核心命题（逐条数据验证）
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_截损命题.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9,
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

    # DXCD 编码
    wk['DXCD_s'] = wk['DXCD'].astype(str)
    m_cd_pos = wk['DTCD'] > 0  # DXCD>0 多头排列
    m_cd_neg = wk['DTCD'] < 0  # DXCD<0 空头排列

    # DXAB 首字符（甲乙丙丁戊己）
    wk['DXAB_s'] = wk['DXAB'].astype(str)
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])  # 甲乙己
    m_bingdingwu = wk['DXAB_s'].str[0].isin(['c', 'z', 'y'])  # 丙丁戊

    lines = []
    lines.append('=' * 100)
    lines.append('验证"截损条件"核心命题（逐条数据验证）')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ P1.6/P1.7: DXZD>0且DXZC>0 提供上涨机会；DXZD<0且DXZC<0 提供下跌机会 ============
    lines.append('')
    lines.append('【P1.6/P1.7】DXZD>0且DXZC>0 提供上涨机会；DXZD<0且DXZC<0 提供下跌机会')
    lines.append('-' * 100)
    m_up = m_zd_pos & m_zc_pos
    m_down = m_zd_neg & m_zc_neg
    for name, m in [('DXZD>0且DXZC>0', m_up), ('DXZD<0且DXZC<0', m_down), ('基线', pd.Series(True, index=wk.index))]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P1.1: 下破DJA但仍在DJC网内，是否不用考虑下跌 ============
    lines.append('')
    lines.append('【P1.1】下破DJA但仍在DJC网内（DXZA<0且DXZC>0），上升机会要等再次上破DJA')
    lines.append('-' * 100)
    m_za_neg_zc_pos = m_za_neg & m_zc_pos  # 下破DJA但仍在DJC网内
    g = wk[m_za_neg_zc_pos]
    n = len(g)
    avg5 = g['未来5天涨幅'].mean()
    avg10 = g['未来10天涨幅'].mean()
    avg20 = g['未来20天涨幅'].mean()
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    cont = (g['未来5天最低涨幅'] < 0).mean() * 100
    lines.append(f'  下破DJA但DJC网内: 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}% 5天继续跌{cont:>6.2f}%')
    # 对比：下破DJA且下破DJC
    m_za_neg_zc_neg = m_za_neg & m_zc_neg
    g2 = wk[m_za_neg_zc_neg]
    avg5b = g2['未来5天涨幅'].mean()
    avg10b = g2['未来10天涨幅'].mean()
    avg20b = g2['未来20天涨幅'].mean()
    hr5b = (g2['未来5天最高HR'] >= 3).mean() * 100
    lines.append(f'  下破DJA且下破DJC: 样本{len(g2):>10,d} 5天{avg5b:>7.3f}% 10天{avg10b:>7.3f}% 20天{avg20b:>7.3f}% 5天冲高≥3%{hr5b:>6.2f}%')

    # ============ P1.5: DXCD>0时，下破DJD作为下破DJC的确认 ============
    lines.append('')
    lines.append('【P1.5】DXCD>0时，下破DJC但DJD还在 vs 下破DJD（确认）')
    lines.append('-' * 100)
    # DXCD>0 多头排列
    sub = wk[m_cd_pos]
    # 下破DJC但DJD还在：DXZC<0 且 DXZD>0
    m_zc_neg_zd_pos = (sub['日ZC'] < 0) & (sub['DTZD'] > 0)
    # 下破DJD：DXZD<0
    m_zd_neg2 = sub['DTZD'] < 0
    for name, m in [('下破DJC但DJD还在', m_zc_neg_zd_pos), ('下破DJD(确认)', m_zd_neg2)]:
        g = sub[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P4.4: 只有上破DJA才有上涨机会，或放大到站上DJB ============
    lines.append('')
    lines.append('【P4.4】只有上破DJA才有上涨机会（DXZA>0 vs DXZA<0）')
    lines.append('-' * 100)
    for name, m in [('DXZA>0(站上DJA)', m_za_pos), ('DXZA<0(跌破DJA)', m_za_neg)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P4.5: 下破DJB后DXAB丙丁戊不应持有，叠加下破DJC更确认 ============
    lines.append('')
    lines.append('【P4.5】下破DJB后DXAB丙丁戊 vs 甲乙己')
    lines.append('-' * 100)
    # 下破DJB = DXZB<0，但日ZB列未加载，用日ZA<0近似（DJA<DJB，跌破DJA通常也跌破DJB）
    # 这里用 DXAB 丙丁戊 + 下破DJC 来验证
    m_bingdingwu_zc_neg = m_bingdingwu & m_zc_neg
    m_jiayiji_zc_neg = m_jiayiji & m_zc_neg
    for name, m in [('丙丁戊+下破DJC', m_bingdingwu_zc_neg), ('甲乙己+下破DJC', m_jiayiji_zc_neg)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ P1.2: 即使DJC与DJA之上，仍可能是诱多 ============
    lines.append('')
    lines.append('【P1.2】即使DJC与DJA之上（DXZC>0且DXZA>0），仍可能是诱多')
    lines.append('-' * 100)
    m_za_zc_pos = m_za_pos & m_zc_pos
    g = wk[m_za_zc_pos]
    n = len(g)
    avg5 = g['未来5天涨幅'].mean()
    avg10 = g['未来10天涨幅'].mean()
    avg20 = g['未来20天涨幅'].mean()
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    cont = (g['未来5天最低涨幅'] < 0).mean() * 100
    lines.append(f'  DXZC>0且DXZA>0: 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}% 5天继续跌{cont:>6.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()