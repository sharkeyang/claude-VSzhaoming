#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用VBA正确术语重新验证 日层赢算法
VBA日层赢（IQQQ跨码_D据擎2神谕.bas）：
- 日层土型（四土）：沃/禁/念/肋，基于 DXZE × DXCD护级
  - 禁土：DXZE<0 + DXCD∈{下,忑}
  - 念土：DXCD∈{中,下,忑}（排除禁土）
  - 沃土：DXZE>0 + DXCD∈{上,忐}
  - 肋土：CD∈{忠} + DXZE<0+{上,忐}
- 日层赢 = 日层土型 × DXAB：
  - 介A/持A = 沃土 + 甲乙己 → 第二层必赢
  - _介A/_持B = 肋土 + 甲乙己 → 第一层必赢
  - __禁/__念/__错 = 非操作区
DXCD护级与DJC/DJD关系：
- DXCD>0（BTCD>0，DJC>DJD，多头排列）：上=日ZC>0，中=日ZD>0，下=日ZD<0
- DXCD<0（BTCD<0，DJC<DJD，空头排列）：忐=日ZD>0，忠=日ZC>0，忑=日ZC<0
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日层赢VBA术语.txt'
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
    # 未来N天日ZD（用于判断下破DJD）
    wk['未来5天日ZD'] = wk.groupby('fid')['DTZD'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    wk['未来10天日ZD'] = wk.groupby('fid')['DTZD'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).min())
    # 未来N天日ZC
    wk['未来5天日ZC'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    wk['未来10天日ZC'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).min())
    # 未来N天日ZD最大值（未来N天内是否至少有一天回到DJD之上）
    wk['未来5天日ZD_max'] = wk.groupby('fid')['DTZD'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    wk['未来10天日ZD_max'] = wk.groupby('fid')['DTZD'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).max())
    # 未来N天日ZC最大值（未来N天内是否至少有一天回到DJC之上）
    wk['未来5天日ZC_max'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    wk['未来10天日ZC_max'] = wk.groupby('fid')['日ZC'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).max())
    # 未来N天内是否有一天同时满足DXZD>0且DXZC>0（逐日判断，省内存）
    # 用 shift 构造未来5天/10天的 DXZD 和 DXZC，判断是否存在同一天同时>0
    # 先构造未来5天
    m_same5 = pd.Series(False, index=wk.index)
    for d in range(1, 6):
        zd = wk.groupby('fid')['DTZD'].shift(-d)
        zc = wk.groupby('fid')['日ZC'].shift(-d)
        m_same5 = m_same5 | ((zd > 0) & (zc > 0))
    wk['未来5天同日满足'] = m_same5
    # 未来10天
    m_same10 = pd.Series(False, index=wk.index)
    for d in range(1, 11):
        zd = wk.groupby('fid')['DTZD'].shift(-d)
        zc = wk.groupby('fid')['日ZC'].shift(-d)
        m_same10 = m_same10 | ((zd > 0) & (zc > 0))
    wk['未来10天同日满足'] = m_same10
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

    # DXCD护级
    m_cd_shang = wk['DXCD_s'] == '上'
    m_cd_zhong = wk['DXCD_s'] == '中'
    m_cd_xia = wk['DXCD_s'] == '下'
    m_cd_tan = wk['DXCD_s'] == '忐'
    m_cd_zhong2 = wk['DXCD_s'] == '忠'
    m_cd_te = wk['DXCD_s'] == '忑'
    # DXZE>0 / <0
    m_ze_pos = wk['日ZE'] > 0
    m_ze_neg = wk['日ZE'] < 0
    # 日ZC>0 / <0
    m_zc_pos = wk['日ZC'] > 0
    m_zc_neg = wk['日ZC'] < 0
    # 日ZD>0 / <0
    m_zd_pos = wk['DTZD'] > 0
    m_zd_neg = wk['DTZD'] < 0
    # 甲乙己
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    # 周ZC>0
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    # ============ VBA日层土型（四土） ============
    # 禁土：DXZE<0 + DXCD∈{下,忑}
    m_jin = m_ze_neg & (m_cd_xia | m_cd_te)
    # 念土：DXCD∈{中,下,忑}（排除禁土）
    m_nian = (m_cd_zhong | m_cd_xia | m_cd_te) & ~m_jin
    # 沃土：DXZE>0 + DXCD∈{上,忐}
    m_wo = m_ze_pos & (m_cd_shang | m_cd_tan)
    # 肋土：CD∈{忠} + DXZE<0+{上,忐}
    m_lei = m_cd_zhong2 | (m_ze_neg & (m_cd_shang | m_cd_tan))

    # ============ VBA日层赢 ============
    # 介A/持A = 沃土 + 甲乙己（第二层必赢）
    m_jieA = m_wo & m_jiayiji
    # _介A/_持B = 肋土 + 甲乙己（第一层必赢）
    m_jieB = m_lei & m_jiayiji
    # 介/持（可介入/可持有）= 沃土或肋土 + 甲乙己
    m_jiechi = (m_wo | m_lei) & m_jiayiji

    lines = []
    lines.append('=' * 100)
    lines.append('用VBA正确术语验证 日层赢算法')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. VBA日层土型（四土） ============
    lines.append('')
    lines.append('【1. VBA日层土型（四土：沃/禁/念/肋）】')
    lines.append('-' * 100)
    print_block(lines, '1.1 四土收益', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('沃土(DXZE>0+CD上/忐)', m_wo),
        ('肋土(CD忠+DXZE<0+上/忐)', m_lei),
        ('念土(CD中/下/忑排除禁)', m_nian),
        ('禁土(DXZE<0+CD下/忑)', m_jin),
        ('沃土 + 甲乙己', m_wo & m_jiayiji),
        ('肋土 + 甲乙己', m_lei & m_jiayiji),
    ])

    # ============ 2. VBA日层赢（介/持） ============
    lines.append('')
    lines.append('【2. VBA日层赢（介/持 = 可介入/可持有）】')
    lines.append('-' * 100)
    print_block(lines, '2.1 介/持收益', [
        ('介A/持A(沃土+甲乙己,第二层必赢)', m_jieA),
        ('_介A/_持B(肋土+甲乙己,第一层必赢)', m_jieB),
        ('介/持(沃土或肋土+甲乙己)', m_jiechi),
        ('介/持 + 周ZC>0', m_jiechi & m_zhouzc),
        ('介/持 + 周ZC≤0', m_jiechi & ~m_zhouzc),
    ])

    # ============ 3. 用户问的"DXZD>0且DXZC>0"介入条件 ============
    lines.append('')
    lines.append('【3. 用户问的"DXZD>0且DXZC>0"介入条件】')
    lines.append('-' * 100)
    m_zdzc = m_zd_pos & m_zc_pos  # 价格同时在DJD和DJC之上
    print_block(lines, '3.1 DXZD>0且DXZC>0 收益', [
        ('DXZD>0且DXZC>0(价格在DJD和DJC之上)', m_zdzc),
        ('DXZD>0且DXZC>0 + 甲乙己', m_zdzc & m_jiayiji),
        ('DXZD>0且DXZC>0 + 周ZC>0', m_zdzc & m_zhouzc),
        ('DXZD>0且DXZC>0 + 周ZC≤0', m_zdzc & ~m_zhouzc),
        ('对比: DXZD>0(仅DJD之上)', m_zd_pos),
        ('对比: DXZC>0(仅DJC之上)', m_zc_pos),
    ])

    # ============ 4. 对比：VBA介/持 vs 用户条件 ============
    lines.append('')
    lines.append('【4. 对比：VBA介/持 vs 用户条件(DXZD>0且DXZC>0)】')
    lines.append('-' * 100)
    print_block(lines, '4.1 各条件对比', [
        ('VBA介/持(沃土或肋土+甲乙己)', m_jiechi),
        ('用户条件(DXZD>0且DXZC>0)', m_zdzc),
        ('用户条件 + 甲乙己', m_zdzc & m_jiayiji),
        ('VBA介/持 + 周ZC>0', m_jiechi & m_zhouzc),
        ('用户条件 + 周ZC>0', m_zdzc & m_zhouzc),
    ])

    # ============ 5. 下破DJD后再次介入 ============
    lines.append('')
    lines.append('【5. 下破DJD退出后，未来N天内再次满足(DXZD>0且DXZC>0)】')
    lines.append('-' * 100)
    # 下破DJD后的时点：当前DXZD<0（已在DJD之下），且前一日DXZD>0（刚下破）
    wk['前日ZD'] = wk.groupby('fid')['DTZD'].shift(1)
    m_break_after = (wk['DTZD'] < 0) & (wk['前日ZD'] > 0)
    g_break = wk[m_break_after]
    n_break = len(g_break)
    lines.append(f'下破DJD后时点样本(当前已在DJD之下): {n_break:,}')
    if n_break > 0:
        # 从下破后的时点开始，未来N天内同一天再次满足DXZD>0且DXZC>0
        m_re5 = m_break_after & wk['未来5天同日满足']
        m_re10 = m_break_after & wk['未来10天同日满足']
        pct5 = m_re5.sum() / n_break * 100
        pct10 = m_re10.sum() / n_break * 100
        lines.append(f'下破DJD后未来5天内同一天再次满足(DXZD>0且DXZC>0): {pct5:.1f}%')
        lines.append(f'下破DJD后未来10天内同一天再次满足(DXZD>0且DXZC>0): {pct10:.1f}%')
        # 下破DJD后，未来N天内至少一天回到DJD之上(DXZD>0)
        pct_back5 = (wk.loc[m_break_after.index, '未来5天日ZD_max'] > 0).mean() * 100
        pct_back10 = (wk.loc[m_break_after.index, '未来10天日ZD_max'] > 0).mean() * 100
        lines.append(f'下破DJD后未来5天内至少一天回到DJD之上: {pct_back5:.1f}%')
        lines.append(f'下破DJD后未来10天内至少一天回到DJD之上: {pct_back10:.1f}%')
        # 下破DJD后，未来N天内至少一天回到DJC之上(DXZC>0)
        pct_zc5 = (wk.loc[m_break_after.index, '未来5天日ZC_max'] > 0).mean() * 100
        pct_zc10 = (wk.loc[m_break_after.index, '未来10天日ZC_max'] > 0).mean() * 100
        lines.append(f'下破DJD后未来5天内至少一天回到DJC之上: {pct_zc5:.1f}%')
        lines.append(f'下破DJD后未来10天内至少一天回到DJC之上: {pct_zc10:.1f}%')
        # 下破DJD后时点的收益
        g_break_ret = wk.loc[m_break_after.index]
        lines.append(f'下破DJD后时点均涨幅: {g_break_ret["涨幅"].mean():.3f}%')
        lines.append(f'下破DJD后时点次日P3: {(g_break_ret["下日HR"]>=3).mean()*100:.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()