#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 日赢算法作为周5.1的"提前介入"逻辑
用户观点：
- 周5.1必须在满足条件后介入（周WXZC>0），但介入时机可能错过
- 当 DXCD<0 且 DXZD>0（日赢丘内，但周5.1不满足）时，可先借助日赢算法介入
- 如果日赢能转为周5.1，继续持有并观察
- 如果中途下破DJD，按日赢条件退出，不会造成损失
数据源：谕组日 CSV（131列，GBK编码）
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日赢提前介入.txt'
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
    lines.append('验证 日赢算法作为周5.1的"提前介入"逻辑')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 核心：DXCD<0 且 DXZD>0（日赢丘内，周5.1不满足）时介入 ============
    lines.append('')
    lines.append('【1. 核心：DXCD<0 且 DXZD>0（日赢丘内，周5.1不满足）时介入】')
    lines.append('-' * 100)
    # 用户场景：DXCD<0 且 DXZD>0（日赢丘内，用DJD丘），但周5.1不满足（周ZC≤0）
    m_scene = m_dxcd_neg & m_zd_pos & ~m_zhouzc
    print_block(lines, '1.1 用户场景（DXCD<0且DXZD>0，周ZC≤0）', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('日赢丘内(全)', m_yingqiu),
        ('用户场景(DXCD<0且DXZD>0,周ZC≤0)', m_scene),
        ('用户场景 + 甲乙己', m_scene & m_jiayiji),
        ('用户场景 + 周AB>0', m_scene & m_zhouab),
        ('用户场景 + 周AB>0 + 甲乙己', m_scene & m_zhouab & m_jiayiji),
    ])

    # ============ 2. 用户场景能否转为周5.1 ============
    lines.append('')
    lines.append('【2. 用户场景能否转为周5.1（周ZC>0）】')
    lines.append('-' * 100)
    g_scene = wk[m_scene]
    n_scene = len(g_scene)
    if n_scene > 0:
        # 未来5/10/20天周ZC>0的比例
        for days, col in [('5天', '未来5天周ZC'), ('10天', '未来10天周ZC'), ('20天', '未来20天周ZC')]:
            pct = (g_scene[col] > 0).mean() * 100
            lines.append(f'未来{days}内转为周ZC>0: {pct:.1f}%')
        # 未来5/10/20天周ZC>0且周AB>0（完整周5.1）的比例
        for days, col in [('5天', '未来5天周ZC'), ('10天', '未来10天周ZC'), ('20天', '未来20天周ZC')]:
            # 需要未来周AB，简化用当前周AB
            pct = ((g_scene[col] > 0) & m_zhouab.loc[g_scene.index]).mean() * 100
            lines.append(f'未来{days}内转为周5.1(周ZC>0且周AB>0): {pct:.1f}%')

    # ============ 3. 下破DJD退出是否避免损失 ============
    lines.append('')
    lines.append('【3. 下破DJD（日ZD<0）退出是否避免损失】')
    lines.append('-' * 100)
    # 用户场景中，未来5天下破DJD的样本
    m_break_zd = m_scene & (wk['未来5天日ZD'] < 0)
    m_not_break_zd = m_scene & (wk['未来5天日ZD'] >= 0)
    print_block(lines, '3.1 用户场景中，未来5天下破DJD vs 未下破', [
        ('用户场景(全)', m_scene),
        ('未来5天下破DJD', m_break_zd),
        ('未来5天未下破DJD', m_not_break_zd),
    ])

    # ============ 4. 对比：日赢提前介入 vs 等周5.1确认 ============
    lines.append('')
    lines.append('【4. 对比：日赢提前介入 vs 等周5.1确认】')
    lines.append('-' * 100)
    print_block(lines, '4.1 提前介入 vs 等确认', [
        ('日赢提前介入(用户场景)', m_scene),
        ('周5.1已满足(周ZC>0且周AB>0)', m_zhou51),
        ('日赢丘内 + 周5.1已满足', m_yingqiu & m_zhou51),
        ('日赢丘内 + 周ZC>0(仅周线主升)', m_yingqiu & m_zhouzc),
    ])

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()