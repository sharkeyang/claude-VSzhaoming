#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补充验证：堆垒（DJC之上已存在多个柱，对应周级别上周已站上WJA）
P3.1: DXCD<0时，DJD之下DJC之上 + 堆垒 的介入效果
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_堆垒.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, 'DXAB': 9, '柱排': 10,
    '日ZA': 16, '日ZC': 17, '日ZE': 18,
    '次日高幅': 28, 'DTZD': 69, 'DTCD': 71,
    '周ZC': 91, '周AB': 95, '周ZA': 89,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', '次日高幅', 'DTZD', 'DTCD', '周ZC', '周AB', '周ZA']:
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

    m_zc_pos = wk['日ZC'] > 0
    m_zd_pos = wk['DTZD'] > 0
    m_zd_neg = wk['DTZD'] < 0
    m_zhouza = wk['周ZA'] > 0  # 上周站上WJA（堆垒近似）
    m_zhouzc = wk['周ZC'] > 0

    wk['DXCD_s'] = wk['DXCD'].astype(str)
    m_cd_neg = wk['DTCD'] < 0

    # 柱排：升排（升开头）
    wk['柱排_s'] = wk['柱排'].astype(str)
    m_shengpai = wk['柱排_s'].str.startswith('升', na=False)

    lines = []
    lines.append('=' * 100)
    lines.append('补充验证：堆垒（DJC之上已存在多个柱，对应周级别上周已站上WJA）')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ P3.1: DXCD<0时，DJD之下DJC之上 + 堆垒 ============
    lines.append('')
    lines.append('【P3.1】DXCD<0(空头排列)时，DJD之下DJC之上 + 堆垒(周ZA>0) 的介入效果')
    lines.append('-' * 100)
    sub = wk[m_cd_neg]
    m_zd_neg_zc_pos = (sub['DTZD'] < 0) & (sub['日ZC'] > 0)
    m_zd_neg_zc_pos_zhouza = m_zd_neg_zc_pos & sub['周ZA'] > 0
    m_zd_neg_zc_pos_zhouza_sheng = m_zd_neg_zc_pos_zhouza & sub['柱排_s'].str.startswith('升', na=False)
    for name, m in [('DJD之下DJC之上', m_zd_neg_zc_pos),
                    ('+堆垒(周ZA>0)', m_zd_neg_zc_pos_zhouza),
                    ('+堆垒+升排', m_zd_neg_zc_pos_zhouza_sheng)]:
        g = sub[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 对比：上破DJD后介入 ============
    lines.append('')
    lines.append('【对比】上破DJD后介入 vs DJD之下DJC之上+堆垒')
    lines.append('-' * 100)
    m_zd_pos2 = sub['DTZD'] > 0
    g = sub[m_zd_pos2]
    avg5 = g['未来5天涨幅'].mean()
    avg10 = g['未来10天涨幅'].mean()
    avg20 = g['未来20天涨幅'].mean()
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    lines.append(f'  上破DJD后介入: 样本{len(g):>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 堆垒在周线主升中的效果 ============
    lines.append('')
    lines.append('【堆垒在周线主升(5.1)中的效果】')
    lines.append('-' * 100)
    sub_zhou = wk[m_zhouzc]
    m_operable = (sub_zhou['DTZD'] > 0) & (sub_zhou['日ZC'] > 0)
    m_operable_zhouza = m_operable & (sub_zhou['周ZA'] > 0)
    for name, m in [('周主升+两线之上', m_operable),
                    ('+堆垒(周ZA>0)', m_operable_zhouza)]:
        g = sub_zhou[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()