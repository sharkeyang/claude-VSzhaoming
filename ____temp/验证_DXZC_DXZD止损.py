#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 (DXZC<0 且 DXZD<0) 作为止损指标是否合适，以及能否作为 5.1/5.2 的提前退出指标
指标含义：价格同时跌破 DJC(EMA26) 和 DJD(EMA60)
验证思路：
  ① 作为止损指标：触发后未来收益如何？是否确实该退出（后续继续跌）？
  ② 作为 5.1/5.2 提前退出：周线主升(WXZC>0)但日线已跌破 DJC+DJD 时，退出是否比继续持有更好？
数据源：谕组日 CSV（131列，GBK），全量3449文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_DXZC_DXZD止损.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, '日ZA': 16, '日ZC': 17, '日ZE': 18,
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
    # 未来5天最高高幅（冲高）
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    # 未来5天最低涨幅（继续下跌）
    wk['未来5天最低涨幅'] = wk.groupby('fid')['涨幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    # 指标：DXZC<0 且 DXZD<0（同时跌破 DJC 和 DJD）
    m_zc_neg = wk['日ZC'] < 0
    m_zd_neg = wk['DTZD'] < 0
    m_trigger = m_zc_neg & m_zd_neg  # 触发止损
    m_hold = ~m_trigger  # 未触发（继续持有）

    # 周线主升：WXZC>0（5.1），WXZC>0 且 WXAB>0（5.2）
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    lines = []
    lines.append('=' * 100)
    lines.append('验证 (DXZC<0 且 DXZD<0) 作为止损指标是否合适，以及能否作为 5.1/5.2 提前退出指标')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. 全量：触发 vs 未触发 ============
    lines.append('')
    lines.append('【1. 全量：触发(DXZC<0且DXZD<0) vs 未触发】')
    lines.append('-' * 100)
    lines.append(f'{"状态":<20s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    for name, mask in [('触发(止损)', m_trigger), ('未触发(持有)', m_hold)]:
        g = wk[mask]
        n = len(g)
        p3 = (g['下日涨幅'] >= 3).mean() * 100
        p5 = (g['未来5天最高HR'] >= 3).mean() * 100
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<20s} {n:>10,d} {p3:>7.2f}% {p5:>7.2f}% {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')

    # ============ 2. 周线主升范围内（5.1：WXZC>0） ============
    lines.append('')
    lines.append('【2. 周线主升范围内（5.1：WXZC>0）触发 vs 未触发】')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    g_trig = sub[m_trigger[m_zhouzc]]
    g_hold = sub[~m_trigger[m_zhouzc]]
    lines.append(f'{"状态":<20s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    for name, g in [('触发(提前退出)', g_trig), ('未触发(继续持有)', g_hold)]:
        n = len(g)
        p3 = (g['下日涨幅'] >= 3).mean() * 100
        p5 = (g['未来5天最高HR'] >= 3).mean() * 100
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<20s} {n:>10,d} {p3:>7.2f}% {p5:>7.2f}% {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')

    # ============ 3. 周线主升范围内（5.2：WXZC>0 且 WXAB>0） ============
    lines.append('')
    lines.append('【3. 周线主升范围内（5.2：WXZC>0 且 WXAB>0）触发 vs 未触发】')
    lines.append('-' * 100)
    sub52 = wk[m_zhouzc & m_zhouab]
    g_trig52 = sub52[m_trigger[m_zhouzc & m_zhouab]]
    g_hold52 = sub52[~m_trigger[m_zhouzc & m_zhouab]]
    lines.append(f'{"状态":<20s} {"样本":>10s} {"次日P3":>8s} {"5天P3":>8s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    for name, g in [('触发(提前退出)', g_trig52), ('未触发(继续持有)', g_hold52)]:
        n = len(g)
        p3 = (g['下日涨幅'] >= 3).mean() * 100
        p5 = (g['未来5天最高HR'] >= 3).mean() * 100
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<20s} {n:>10,d} {p3:>7.2f}% {p5:>7.2f}% {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')

    # ============ 4. 触发后再次满足 5.1/5.2 的时间 ============
    lines.append('')
    lines.append('【4. 触发(DXZC<0且DXZD<0)后，未来N天再次满足 5.1(WXZC>0) 的比例】')
    lines.append('-' * 100)
    # 未来5/10/20天是否再次满足 WXZC>0
    for n_days in [5, 10, 20]:
        col = f'未来{n_days}天周ZC>0'
        wk[col] = wk.groupby('fid')['周ZC'].transform(
            lambda s: s.shift(-1).rolling(n_days, min_periods=1).max() > 0)
    g_trig = wk[m_trigger]
    lines.append(f'{"指标":<20s} {"触发样本":>10s} {"未来5天再满足5.1":>16s} {"未来10天再满足5.1":>16s} {"未来20天再满足5.1":>16s}')
    lines.append('-' * 100)
    r5 = (g_trig['未来5天周ZC>0']).mean() * 100
    r10 = (g_trig['未来10天周ZC>0']).mean() * 100
    r20 = (g_trig['未来20天周ZC>0']).mean() * 100
    lines.append(f'{"DXZC<0且DXZD<0":<20s} {len(g_trig):>10,d} {r5:>15.2f}% {r10:>15.2f}% {r20:>15.2f}%')

    # 对比：仅在周线主升范围内触发
    g_trig_zhou = wk[m_trigger & m_zhouzc]
    lines.append(f'{"(周线主升内触发)":<20s} {len(g_trig_zhou):>10,d} {(g_trig_zhou["未来5天周ZC>0"]).mean()*100:>15.2f}% {(g_trig_zhou["未来10天周ZC>0"]).mean()*100:>15.2f}% {(g_trig_zhou["未来20天周ZC>0"]).mean()*100:>15.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()