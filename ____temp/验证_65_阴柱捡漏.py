#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 6.5 方法日M漏（DXZA>0 阴柱捡漏）逻辑
数据源：谕组日 CSV（131列，GBK编码）
列映射依据：_产出物/_工具/元数据_vba数据映射_日类.md
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_65_阴柱捡漏.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 13, '日ZC': 14, '日ZE': 15,
    'BSHA': 19, '次日高幅': 26, '日等型': 43,
    '周ZC': 87,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', 'BSHA', '次日高幅']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    wk['下日HR'] = wk['次日高幅']
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['下日ZA'] = wk.groupby('fid')['日ZA'].shift(-1)
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def stats_row(g):
    n = len(g)
    if n == 0:
        return None
    za_pos = (g['下日ZA'] > 0).mean() * 100
    hr1 = (g['下日HR'] >= 1).mean() * 100
    hr2 = (g['下日HR'] >= 2).mean() * 100
    hr3 = (g['下日HR'] >= 3).mean() * 100
    yang = (g['下日涨幅'] >= 0).mean() * 100
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    return za_pos, hr1, hr2, hr3, yang, hr5, n

def print_block(lines, title, items):
    lines.append('')
    lines.append(f'【{title}】')
    lines.append('-' * 100)
    lines.append(f'{"条件":<44s} {"样本":>10s} {"下日ZA>0":>9s} {"HR≥1%":>7s} {"HR≥2%":>7s} {"HR≥3%":>7s} {"下日阳柱":>9s} {"5天HR≥3%":>10s}')
    lines.append('-' * 100)
    for name, mask in items:
        r = stats_row(wk[mask])
        if r is None:
            lines.append(f'{name:<44s} {"-":>10s} {"-":>9s} {"-":>7s} {"-":>7s} {"-":>7s} {"-":>9s} {"-":>10s}')
            continue
        za_pos, hr1, hr2, hr3, yang, hr5, n = r
        lines.append(f'{name:<44s} {n:>10,d} {za_pos:>8.1f}% {hr1:>6.1f}% {hr2:>6.1f}% {hr3:>6.1f}% {yang:>8.1f}% {hr5:>9.1f}%')

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    wk['柱排_s'] = wk['柱排'].astype(str)
    wk['DXAB_s'] = wk['DXAB'].astype(str)
    wk['DXCD_s'] = wk['DXCD'].astype(str)

    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    m_zc = wk['日ZC'] > 0
    m_wotu = (wk['日ZE'] > 0) & (wk['DXCD_s'].isin(['上', '忐']))
    m_za_pos = wk['日ZA'] > 0
    m_yin = wk['涨幅'] < 0
    m_yang = wk['涨幅'] >= 0
    m_zhouzc = wk['周ZC'] > 0

    lines = []
    lines.append('=' * 100)
    lines.append('验证 6.5 方法日M漏（DXZA>0 阴柱捡漏）逻辑')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    print_block(lines, '核心：DXZA>0 阴柱介入后，能否保持在DJA网内 + 期待下柱冲高/变阳柱', [
        ('基线(全量)', pd.Series(True, index=wk.index)),
        ('DXZA>0 阴柱', m_za_pos & m_yin),
        ('DXZA>0 阳柱', m_za_pos & m_yang),
        ('DXZA>0 阴柱 + 甲乙己ZC>0', m_za_pos & m_yin & m_jiayiji & m_zc),
        ('DXZA>0 阴柱 + 沃土', m_za_pos & m_yin & m_wotu),
        ('DXZA>0 阴柱 + 沃土 + 周ZC>0', m_za_pos & m_yin & m_wotu & m_zhouzc),
        ('DXZA>0 阴柱 + 沃土 + 周ZC≤0', m_za_pos & m_yin & m_wotu & ~m_zhouzc),
    ])

    print_block(lines, '对比：DXZA>0 阴柱 vs DXZA<0 阴柱（DJA网内 vs 网外）', [
        ('DXZA>0 阴柱（DJA网内）', m_za_pos & m_yin),
        ('DXZA<0 阴柱（DJA网外）', ~m_za_pos & m_yin),
        ('DXZA>0 阴柱 + 沃土', m_za_pos & m_yin & m_wotu),
        ('DXZA<0 阴柱 + 沃土', ~m_za_pos & m_yin & m_wotu),
    ])

    print_block(lines, '6.1 范围内（DXZC>0，DJC丘内）DXZA>0 阴柱', [
        ('6.1范围(DXZC>0) 全量', m_zc),
        ('6.1范围 DXZA>0 阴柱', m_zc & m_za_pos & m_yin),
        ('6.1范围 DXZA>0 阳柱', m_zc & m_za_pos & m_yang),
        ('6.1范围 DXZA<0 阴柱', m_zc & ~m_za_pos & m_yin),
        ('6.1范围 DXZA>0 阴柱 + 甲乙己', m_zc & m_za_pos & m_yin & m_jiayiji),
        ('6.1范围 DXZA>0 阴柱 + 沃土', m_zc & m_za_pos & m_yin & m_wotu),
        ('6.1范围 DXZA>0 阴柱 + 沃土 + 周ZC>0', m_zc & m_za_pos & m_yin & m_wotu & m_zhouzc),
        ('6.1范围 DXZA>0 阴柱 + 沃土 + 周ZC≤0', m_zc & m_za_pos & m_yin & m_wotu & ~m_zhouzc),
    ])

    print_block(lines, '6.1 范围 vs 全量：DXZA>0 阴柱 对比', [
        ('全量 DXZA>0 阴柱', m_za_pos & m_yin),
        ('6.1范围 DXZA>0 阴柱', m_zc & m_za_pos & m_yin),
        ('全量 DXZA>0 阴柱 + 沃土', m_za_pos & m_yin & m_wotu),
        ('6.1范围 DXZA>0 阴柱 + 沃土', m_zc & m_za_pos & m_yin & m_wotu),
    ])

    # 阴柱后下柱形态分布
    lines.append('')
    lines.append('【DXZA>0 阴柱后，下柱形态分布】')
    lines.append('-' * 100)
    g = wk[m_za_pos & m_yin]
    n = len(g)
    if n > 0:
        yang_next = (g['下日涨幅'] >= 0).mean() * 100
        yin_next = (g['下日涨幅'] < 0).mean() * 100
        hr1_next = (g['下日HR'] >= 1).mean() * 100
        hr2_next = (g['下日HR'] >= 2).mean() * 100
        hr3_next = (g['下日HR'] >= 3).mean() * 100
        za_pos_next = (g['下日ZA'] > 0).mean() * 100
        lines.append(f'DXZA>0 阴柱介入（样本 {n:,}）：')
        lines.append(f'  下日变阳柱: {yang_next:.1f}%')
        lines.append(f'  下日仍阴柱: {yin_next:.1f}%')
        lines.append(f'  下日冲高≥1%: {hr1_next:.1f}%')
        lines.append(f'  下日冲高≥2%: {hr2_next:.1f}%')
        lines.append(f'  下日冲高≥3%: {hr3_next:.1f}%')
        lines.append(f'  下日仍DXZA>0（保持DJA网内）: {za_pos_next:.1f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()