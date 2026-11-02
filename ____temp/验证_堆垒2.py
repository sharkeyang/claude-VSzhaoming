#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新验证堆垒：用升连数（柱排Q后面的数字）判定 DJC 之上已存在的柱数
堆垒 = DJC 之上已存在多个柱（5-10柱）
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings, re
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_堆垒2.txt'
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
    # 升连数：从柱排提取 Q 后面的数字
    wk['柱排_s'] = wk['柱排'].astype(str)
    wk['升连数'] = wk['柱排_s'].str.extract(r'Q(\d+)').astype(float)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_zc_pos = wk['日ZC'] > 0
    m_zd_pos = wk['DTZD'] > 0
    m_zd_neg = wk['DTZD'] < 0
    m_zhouzc = wk['周ZC'] > 0
    m_cd_neg = wk['DTCD'] < 0

    # 堆垒：升连数>=5（DJC之上已存在5柱以上）
    m_duilei = wk['升连数'] >= 5
    m_duilei_3 = wk['升连数'] >= 3

    lines = []
    lines.append('=' * 100)
    lines.append('重新验证堆垒：用升连数（柱排Q后面的数字）判定 DJC 之上已存在的柱数')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. DXCD<0时，DJD之下DJC之上 + 堆垒 ============
    lines.append('')
    lines.append('【1】DXCD<0(空头排列)时，DJD之下DJC之上 + 堆垒(升连数) 的介入效果')
    lines.append('-' * 100)
    sub = wk[m_cd_neg]
    m_zd_neg_zc_pos = (sub['DTZD'] < 0) & (sub['日ZC'] > 0)
    m_zd_neg_zc_pos_dui5 = m_zd_neg_zc_pos & (sub['升连数'] >= 5)
    m_zd_neg_zc_pos_dui3 = m_zd_neg_zc_pos & (sub['升连数'] >= 3)
    for name, m in [('DJD之下DJC之上', m_zd_neg_zc_pos),
                    ('+堆垒(升连≥5)', m_zd_neg_zc_pos_dui5),
                    ('+堆垒(升连≥3)', m_zd_neg_zc_pos_dui3)]:
        g = sub[m]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'  {name:<24s} 样本{n:>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 2. 对比：上破DJD后介入 ============
    lines.append('')
    lines.append('【2】对比：上破DJD后介入')
    lines.append('-' * 100)
    m_zd_pos2 = sub['DTZD'] > 0
    g = sub[m_zd_pos2]
    avg5 = g['未来5天涨幅'].mean()
    avg10 = g['未来10天涨幅'].mean()
    avg20 = g['未来20天涨幅'].mean()
    hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
    lines.append(f'  上破DJD后介入: 样本{len(g):>10,d} 5天{avg5:>7.3f}% 10天{avg10:>7.3f}% 20天{avg20:>7.3f}% 5天冲高≥3%{hr5:>6.2f}%')

    # ============ 3. 周线主升中，堆垒的效果 ============
    lines.append('')
    lines.append('【3】周线主升(5.1)中，堆垒(升连数)的效果')
    lines.append('-' * 100)
    sub_zhou = wk[m_zhouzc]
    m_operable = (sub_zhou['DTZD'] > 0) & (sub_zhou['日ZC'] > 0)
    m_operable_dui5 = m_operable & (sub_zhou['升连数'] >= 5)
    m_operable_dui3 = m_operable & (sub_zhou['升连数'] >= 3)
    for name, m in [('周主升+两线之上', m_operable),
                    ('+堆垒(升连≥5)', m_operable_dui5),
                    ('+堆垒(升连≥3)', m_operable_dui3)]:
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