#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证可获利范围的"确定化"方案
可操作范围 = 周线主升(WXZC>0) + 日线两线之上(DXZD>0且DXZC>0)
候选确定化条件：站上DJA / 站上DJA+甲乙己 / 堆垒 / 站上DJA+DXCD>0 等
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings, re
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_可获利确定化.txt'
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
    # 升连数
    wk['柱排_s'] = wk['柱排'].astype(str)
    wk['升连数'] = wk['柱排_s'].str.extract(r'Q(\d+)').astype(float)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_za_pos = wk['日ZA'] > 0
    m_zc_pos = wk['日ZC'] > 0
    m_zd_pos = wk['DTZD'] > 0
    m_zhouzc = wk['周ZC'] > 0
    m_cd_pos = wk['DTCD'] > 0
    wk['DXAB_s'] = wk['DXAB'].astype(str)
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    m_shenglian5 = wk['升连数'] >= 5

    # 可操作范围
    m_operable = m_zhouzc & m_zd_pos & m_zc_pos

    lines = []
    lines.append('=' * 100)
    lines.append('验证可获利范围的"确定化"方案')
    lines.append('可操作范围 = 周线主升(WXZC>0) + 日线两线之上(DXZD>0且DXZC>0)')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. 各确定化方案对比 ============
    lines.append('')
    lines.append('【1】可操作范围内，各"确定化"方案对比')
    lines.append('-' * 100)
    candidates = {
        '可操作范围(基准)': m_operable,
        '+站上DJA': m_operable & m_za_pos,
        '+站上DJA+甲乙己': m_operable & m_za_pos & m_jiayiji,
        '+站上DJA+DXCD>0': m_operable & m_za_pos & m_cd_pos,
        '+站上DJA+甲乙己+DXCD>0': m_operable & m_za_pos & m_jiayiji & m_cd_pos,
        '+堆垒(升连≥5)': m_operable & m_shenglian5,
        '+站上DJA+堆垒': m_operable & m_za_pos & m_shenglian5,
    }
    lines.append(f'{"方案":<28s} {"样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天冲高≥3%":>10s}')
    lines.append('-' * 100)
    for name, m in candidates.items():
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {hr5:>9.2f}%')

    # ============ 2. 可操作范围内，站上DJA vs 未站上DJA ============
    lines.append('')
    lines.append('【2】可操作范围内，站上DJA vs 未站上DJA')
    lines.append('-' * 100)
    g_za = wk[m_operable & m_za_pos]
    g_nza = wk[m_operable & ~m_za_pos]
    for name, g in [('站上DJA', g_za), ('未站上DJA', g_nza)]:
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 3. 可操作范围内，DXCD>0 vs DXCD<0 ============
    lines.append('')
    lines.append('【3】可操作范围内，DXCD>0 vs DXCD<0')
    lines.append('-' * 100)
    g_cdpos = wk[m_operable & m_cd_pos]
    g_cdneg = wk[m_operable & ~m_cd_pos]
    for name, g in [('DXCD>0(多头)', g_cdpos), ('DXCD<0(空头)', g_cdneg)]:
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()