#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 DJA/DJC/DJD 三个网哪个可以用作止损
止损定义：跌破均线（网）就退出
验证思路：对每个网，看"跌破网"信号是否有效——
  ① 跌破后继续下跌概率（止损能避开后续下跌）
  ② 跌破后恢复概率（恢复率高=止损过早/无效）
  ③ 跌破 vs 未跌破 的后续收益对比（差距越大，止损信号越有效）
数据源：谕组日 CSV（131列，GBK），全量3449文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_三网止损.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, '日ZA': 16, '日ZC': 17, '日ZE': 18,
    '次日高幅': 28, 'DTZD': 69, 'DTCD': 71,
    '周ZC': 91,
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
    for c in ['收', '涨幅', '高幅', '日ZA', '日ZC', '日ZE', '次日高幅', 'DTZD', 'DTCD', '周ZC']:
        wk[c] = pd.to_numeric(wk[c], errors='coerce')
    # 未来收益
    wk['下日涨幅'] = wk.groupby('fid')['涨幅'].shift(-1)
    wk['未来3天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(3, min_periods=1).sum())
    wk['未来5天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(5, min_periods=1).sum())
    wk['未来10天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(10, min_periods=1).sum())
    # 未来5天最高高幅（恢复/冲高）
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    # 未来10天最高高幅（恢复/冲高）
    wk['未来10天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(10, min_periods=1).max())
    # 未来5天最低涨幅（继续下跌）
    wk['未来5天最低涨幅'] = wk.groupby('fid')['涨幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    # 三个网的"跌破"信号
    # DJA 网：日ZA<0（价格跌破 EMA5）
    # DJC 网：日ZC<0（价格跌破 EMA26）
    # DJD 网：日ZD<0（DTZD<0，价格跌破 EMA60）
    nets = {
        'DJA网(EMA5)': wk['日ZA'] < 0,
        'DJC网(EMA26)': wk['日ZC'] < 0,
        'DJD网(EMA60)': wk['DTZD'] < 0,
    }

    lines = []
    lines.append('=' * 100)
    lines.append('验证 DJA/DJC/DJD 三个网哪个可以用作止损')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 各网跌破信号的有效性 ============
    lines.append('')
    lines.append('【1. 各网"跌破"信号的有效性（全量）】')
    lines.append('-' * 100)
    lines.append(f'{"网":<16s} {"跌破样本":>10s} {"跌破后5天均涨幅":>14s} {"跌破后5天最低均":>14s} {"跌破后5天恢复率":>14s} {"未跌破5天均涨幅":>14s} {"信号差(跌破-未跌破)":>16s}')
    lines.append('-' * 100)

    for name, mask in nets.items():
        g_break = wk[mask]
        g_hold = wk[~mask]
        n_break = len(g_break)
        n_hold = len(g_hold)
        if n_break == 0 or n_hold == 0:
            continue
        avg5_break = g_break['未来5天涨幅'].mean()
        avg5_hold = g_hold['未来5天涨幅'].mean()
        min5_break = g_break['未来5天最低涨幅'].mean()
        # 恢复率 = 未来5天最高HR>=3% 的比例（跌破后还能冲高3%）
        recover = (g_break['未来5天最高HR'] >= 3).mean() * 100
        diff = avg5_break - avg5_hold
        lines.append(f'{name:<16s} {n_break:>10,d} {avg5_break:>13.3f}% {min5_break:>13.3f}% {recover:>13.2f}% {avg5_hold:>13.3f}% {diff:>+15.3f}pp')
        lines.append(f'  └ 跌破后5天均涨幅 {avg5_break:+.3f}% | 未跌破 {avg5_hold:+.3f}% | 信号差 {diff:+.3f}pp')

    # ============ 2. 跌破后继续下跌 vs 恢复 ============
    lines.append('')
    lines.append('【2. 跌破后继续下跌 vs 恢复（判断止损是否有效）】')
    lines.append('-' * 100)
    lines.append(f'{"网":<16s} {"跌破后5天继续跌":>14s} {"跌破后5天恢复≥3%":>16s} {"跌破后10天均涨幅":>14s} {"跌破后10天恢复≥3%":>16s}')
    lines.append('-' * 100)

    for name, mask in nets.items():
        g_break = wk[mask]
        n_break = len(g_break)
        if n_break == 0:
            continue
        # 继续跌 = 未来5天最低涨幅<0（跌破后还有下跌）
        cont_drop = (g_break['未来5天最低涨幅'] < 0).mean() * 100
        # 恢复 = 未来5天最高HR>=3%
        recover5 = (g_break['未来5天最高HR'] >= 3).mean() * 100
        avg10 = g_break['未来10天涨幅'].mean()
        recover10 = (g_break['未来10天最高HR'] >= 3).mean() * 100
        lines.append(f'{name:<16s} {cont_drop:>13.2f}% {recover5:>15.2f}% {avg10:>13.3f}% {recover10:>15.2f}%')

    # ============ 3. 周线主升范围内（先周后日） ============
    lines.append('')
    lines.append('【3. 周线主升范围内（周ZC>0，先周后日）各网跌破信号】')
    lines.append('-' * 100)
    m_zhouzc = wk['周ZC'] > 0
    lines.append(f'{"网":<16s} {"跌破样本":>10s} {"跌破后5天均涨幅":>14s} {"跌破后5天恢复率":>14s} {"未跌破5天均涨幅":>14s} {"信号差":>10s}')
    lines.append('-' * 100)

    for name, mask in nets.items():
        sub = wk[m_zhouzc]
        g_break = sub[mask[m_zhouzc]]
        g_hold = sub[~mask[m_zhouzc]]
        n_break = len(g_break)
        if n_break == 0:
            continue
        avg5_break = g_break['未来5天涨幅'].mean()
        avg5_hold = g_hold['未来5天涨幅'].mean()
        recover = (g_break['未来5天最高HR'] >= 3).mean() * 100
        diff = avg5_break - avg5_hold
        lines.append(f'{name:<16s} {n_break:>10,d} {avg5_break:>13.3f}% {recover:>13.2f}% {avg5_hold:>13.3f}% {diff:>+9.3f}pp')

    # ============ 4. 多头排列（DXCD>0）范围内 ============
    lines.append('')
    lines.append('【4. 多头排列（DXCD>0）范围内各网跌破信号】')
    lines.append('-' * 100)
    m_dxcd_pos = wk['DTCD'] > 0
    lines.append(f'{"网":<16s} {"跌破样本":>10s} {"跌破后5天均涨幅":>14s} {"跌破后5天恢复率":>14s} {"未跌破5天均涨幅":>14s} {"信号差":>10s}')
    lines.append('-' * 100)

    for name, mask in nets.items():
        sub = wk[m_dxcd_pos]
        g_break = sub[mask[m_dxcd_pos]]
        g_hold = sub[~mask[m_dxcd_pos]]
        n_break = len(g_break)
        if n_break == 0:
            continue
        avg5_break = g_break['未来5天涨幅'].mean()
        avg5_hold = g_hold['未来5天涨幅'].mean()
        recover = (g_break['未来5天最高HR'] >= 3).mean() * 100
        diff = avg5_break - avg5_hold
        lines.append(f'{name:<16s} {n_break:>10,d} {avg5_break:>13.3f}% {recover:>13.2f}% {avg5_hold:>13.3f}% {diff:>+9.3f}pp')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()