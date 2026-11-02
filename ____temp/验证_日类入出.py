#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：日类只按DXZE/DXZD入出是否必赢 + 先周后日日线跌势分析
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_日类入出.txt'
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

    wk['DXAB_s'] = wk['DXAB'].astype(str)
    m_ab_neg = wk['DXAB_s'].str[0].isin(['c', 'z', 'y'])  # 丙丁戊（DXAB<0）

    lines = []
    lines.append('=' * 100)
    lines.append('验证：日类只按DXZE/DXZD入出是否必赢 + 先周后日日线跌势分析')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. 日类只按DXZE入出 ============
    lines.append('')
    lines.append('【1】日类只按DXZE入出（DXZE>0持有，DXZE<0退出）')
    lines.append('-' * 100)
    for name, m in [('DXZE>0(持有)', m_ze_pos), ('DXZE<0(退出)', m_ze_neg)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 2. 日类只按DXZD入出 ============
    lines.append('')
    lines.append('【2】日类只按DXZD入出（DXZD>0持有，DXZD<0退出）')
    lines.append('-' * 100)
    for name, m in [('DXZD>0(持有)', m_zd_pos), ('DXZD<0(退出)', m_zd_neg)]:
        g = wk[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<20s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 3. 周线主升中，日线跌势迹象后是否尽快结束 ============
    lines.append('')
    lines.append('【3】周线主升(5.1)中，日线跌势迹象后，未来5/10天累计收益（是否尽快结束）')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    indicators = {
        '下破DXZC(DXZC<0)': m_zc_neg,
        'DXAB丙丁戊': m_ab_neg,
        '下破DXZA(DXZA<0)': m_za_neg,
    }
    lines.append(f'{"日线跌势迹象":<20s} {"样本":>10s} {"未来5天累计":>12s} {"未来10天累计":>12s} {"未来20天累计":>12s}')
    lines.append('-' * 100)
    for name, m in indicators.items():
        g = sub[m[m_zhouzc]]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        lines.append(f'  {name:<20s} {n:>10,d} {avg5:>11.3f}% {avg10:>11.3f}% {avg20:>11.3f}%')

    # ============ 4. 周线主升中，日线跌势迹象后，未来N天恢复（再次满足DXZD>0且DXZC>0） ============
    lines.append('')
    lines.append('【4】周线主升中，日线跌势迹象后，未来N天恢复(再次满足DXZD>0且DXZC>0)')
    lines.append('-' * 100)
    # 在 wk 上计算恢复列（用 reset_index 保证索引对齐）
    wk = wk.reset_index(drop=True)
    for n_days in [5, 10, 20]:
        col = f'未来{n_days}天恢复'
        wk[col] = (wk.groupby('fid')['DTZD'].transform(
            lambda s: s.shift(-1).rolling(n_days, min_periods=1).max() > 0)) & \
                  (wk.groupby('fid')['日ZC'].transform(
            lambda s: s.shift(-1).rolling(n_days, min_periods=1).max() > 0))
    # 重新计算周线主升掩码（reset后索引变了）
    m_zhouzc2 = wk['周ZC'] > 0
    sub2 = wk[m_zhouzc2]
    lines.append(f'{"日线跌势迹象":<20s} {"未来5天恢复":>12s} {"未来10天恢复":>12s} {"未来20天恢复":>12s}')
    lines.append('-' * 100)
    for name, m in indicators.items():
        g = sub2[m[m_zhouzc2]]
        r5 = (g['未来5天恢复']).mean() * 100
        r10 = (g['未来10天恢复']).mean() * 100
        r20 = (g['未来20天恢复']).mean() * 100
        lines.append(f'  {name:<20s} {r5:>11.2f}% {r10:>11.2f}% {r20:>11.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()