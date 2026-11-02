#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证"保持主升定力"：主升中 A(DXZD<0且DXZC<0) 触发后，继续持有 vs 退出的收益对比
核心问题：即使 A 触发（可能已过高点），保持持有能否后续遇到高点？
验证：
  ① 周线主升中 A 触发后，继续持有未来 5/10/20 天收益
  ② 周线主升中 A 触发后，未来 N 天回到高点(HR≥3%)的概率
  ③ 对比：A 触发后立即退出 vs 继续持有到 C(DXZE<0) 再退
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_主升定力.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, '波型': 14,
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
    # 未来N天最高HR（回到高点）
    for n in [5, 10, 20]:
        wk[f'未来{n}天最高HR'] = wk.groupby('fid')['高幅'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).max())
    # 未来N天周ZC<0
    for n in [5, 10, 20]:
        wk[f'未来{n}天周ZC<0'] = wk.groupby('fid')['周ZC'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    # 未来N天DXZE<0（触发C）
    for n in [3, 5, 10]:
        wk[f'未来{n}天DXZE<0'] = wk.groupby('fid')['日ZE'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_zc_neg = wk['日ZC'] < 0
    m_zd_neg = wk['DTZD'] < 0
    m_ze_neg = wk['日ZE'] < 0
    m_A = m_zd_neg & m_zc_neg  # A: DXZD<0 且 DXZC<0
    m_C = m_ze_neg            # C: DXZE<0
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    lines = []
    lines.append('=' * 100)
    lines.append('验证"保持主升定力"：主升中 A(DXZD<0且DXZC<0) 触发后，继续持有 vs 退出的收益对比')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. 周线主升中 A 触发后，继续持有的收益 ============
    lines.append('')
    lines.append('【1. 周线主升(5.1:WXZC>0)中 A 触发后，继续持有的收益】')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    g_A = sub[m_A[m_zhouzc]]
    n_A = len(g_A)
    lines.append(f'A 触发样本: {n_A:,d}')
    lines.append(f'{"指标":<24s} {"5天":>10s} {"10天":>10s} {"20天":>10s}')
    lines.append('-' * 100)
    for name, col in [('未来均涨幅', '未来5天涨幅'), ('未来最高HR≥3%', '未来5天最高HR')]:
        pass
    avg5 = g_A['未来5天涨幅'].mean()
    avg10 = g_A['未来10天涨幅'].mean()
    avg20 = g_A['未来20天涨幅'].mean()
    lines.append(f'{"继续持有均涨幅":<24s} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}%')
    hr5 = (g_A['未来5天最高HR'] >= 3).mean() * 100
    hr10 = (g_A['未来10天最高HR'] >= 3).mean() * 100
    hr20 = (g_A['未来20天最高HR'] >= 3).mean() * 100
    lines.append(f'{"未来N天回到高点(HR≥3%)":<24s} {hr5:>9.2f}% {hr10:>9.2f}% {hr20:>9.2f}%')
    # 未来N天触发C
    c3 = (g_A['未来3天DXZE<0']).mean() * 100
    c5 = (g_A['未来5天DXZE<0']).mean() * 100
    c10 = (g_A['未来10天DXZE<0']).mean() * 100
    lines.append(f'{"未来N天触发C(DXZE<0)":<24s} {c3:>9.2f}% {c5:>9.2f}% {c10:>9.2f}%')

    # ============ 2. 周线主升中 A 触发后，继续持有 vs 立即退出的对比 ============
    lines.append('')
    lines.append('【2. 周线主升中 A 触发后：继续持有 vs 立即退出】')
    lines.append('-' * 100)
    # 继续持有 = A 触发后不退出（未来收益）
    # 立即退出 = A 触发后退出（未来收益为0，即避开后续）
    # 对比：继续持有的未来20天收益 vs 退出的0收益
    lines.append(f'{"策略":<24s} {"未来5天均涨幅":>12s} {"未来10天均涨幅":>12s} {"未来20天均涨幅":>12s}')
    lines.append('-' * 100)
    lines.append(f'{"继续持有(不退出)":<24s} {avg5:>11.3f}% {avg10:>11.3f}% {avg20:>11.3f}%')
    lines.append(f'{"立即退出(避开后续)":<24s} {"0%":>12s} {"0%":>12s} {"0%":>12s}')

    # ============ 3. 周线主升中 A 触发后，按是否触发C分组 ============
    lines.append('')
    lines.append('【3. 周线主升中 A 触发后，按未来是否触发C分组】')
    lines.append('-' * 100)
    # 未来5天触发C vs 未触发C
    g_A_c = g_A[g_A['未来5天DXZE<0']]
    g_A_nc = g_A[~g_A['未来5天DXZE<0']]
    lines.append(f'{"分组":<24s} {"样本":>10s} {"未来5天均涨幅":>12s} {"未来10天均涨幅":>12s} {"未来20天均涨幅":>12s} {"未来5天回高点":>12s}')
    lines.append('-' * 100)
    for name, g in [('未来5天触发C', g_A_c), ('未来5天未触发C', g_A_nc)]:
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        hr5 = (g['未来5天最高HR'] >= 3).mean() * 100
        lines.append(f'{name:<24s} {n:>10,d} {avg5:>11.3f}% {avg10:>11.3f}% {avg20:>11.3f}% {hr5:>11.2f}%')

    # ============ 4. 周线主升中 A 触发后，未来N天周线转负 ============
    lines.append('')
    lines.append('【4. 周线主升中 A 触发后，未来N天周线WXZC转负】')
    lines.append('-' * 100)
    r5 = (g_A['未来5天周ZC<0']).mean() * 100
    r10 = (g_A['未来10天周ZC<0']).mean() * 100
    r20 = (g_A['未来20天周ZC<0']).mean() * 100
    lines.append(f'未来5天周线转负: {r5:.2f}%')
    lines.append(f'未来10天周线转负: {r10:.2f}%')
    lines.append(f'未来20天周线转负: {r20:.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()