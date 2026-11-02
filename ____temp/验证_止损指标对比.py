#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比多个止损指标，寻找"必须退出"的确定性标准
备选指标：
  A. DXZD<0 且 DXZC<0（同时跌破 DJC+DJD）
  B. DXZD<0 或 DXZC<0（跌破 DJC 或 DJD 任一）
  C. DXZE<0（跌破 DJE=EMA120）
  D. DXZD<0 且 DXZC<0 且 DXZE<0（三者全跌破，用户认为必须退出）
核心目标：找到"必须退出的确定性标准"，即把周类 WXZC<0（必须退出）或日级别映射 DXZE<0，
          进行优化或提前退出。
验证维度：
  ① 各指标触发后收益（5/10/20天均涨幅）+ 继续下跌概率 + 触发频率
  ② 各指标在周线主升(5.1/5.2)范围内的提前退出效果
  ③ 关键：各指标触发后，未来N天周线 WXZC 转负(<0)的概率——哪个指标最能提前捕捉周线转弱
  ④ 各指标触发后，未来N天再次满足5.1(WXZC>0)的比例（退出后能否再进）
数据源：谕组日 CSV（131列，GBK），全量3449文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_止损指标对比.txt'
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
    # 未来5天最低涨幅（继续下跌）
    wk['未来5天最低涨幅'] = wk.groupby('fid')['涨幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    # 未来N天周ZC<0（周线转负）概率
    for n in [5, 10, 20]:
        wk[f'未来{n}天周ZC<0'] = wk.groupby('fid')['周ZC'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    # 未来N天周ZC>0（再次满足5.1）概率
    for n in [5, 10, 20]:
        wk[f'未来{n}天周ZC>0'] = wk.groupby('fid')['周ZC'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).max() > 0)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def main():
    global wk
    print('加载数据...', flush=True)
    wk = load_all()

    m_zc_neg = wk['日ZC'] < 0
    m_zd_neg = wk['DTZD'] < 0
    m_ze_neg = wk['日ZE'] < 0

    # 备选止损指标
    indicators = {
        'A. DXZD<0且DXZC<0': m_zd_neg & m_zc_neg,
        'B. DXZD<0或DXZC<0': m_zd_neg | m_zc_neg,
        'C. DXZE<0': m_ze_neg,
        'D. DXZD<0且DXZC<0且DXZE<0': m_zd_neg & m_zc_neg & m_ze_neg,
    }

    # 周线主升
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    lines = []
    lines.append('=' * 100)
    lines.append('对比多个止损指标，寻找"必须退出"的确定性标准')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ ① 各指标触发后收益（全量） ============
    lines.append('')
    lines.append('【① 各指标触发后收益（全量）】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"触发占比":>8s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    for name, mask in indicators.items():
        g = wk[mask]
        n = len(g)
        pct = n / len(wk) * 100
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {pct:>7.2f}% {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')

    # 基线（全量）
    g_all = wk
    lines.append(f'{"基线(全量)":<28s} {len(g_all):>10,d} {"100.00%":>8s} {g_all["未来5天涨幅"].mean():>9.3f}% {g_all["未来10天涨幅"].mean():>9.3f}% {g_all["未来20天涨幅"].mean():>9.3f}% {(g_all["未来5天最低涨幅"]<0).mean()*100:>9.2f}%')

    # ============ ② 各指标在周线主升(5.1)范围内 ============
    lines.append('')
    lines.append('【② 各指标在周线主升(5.1:WXZC>0)范围内触发后收益】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    for name, mask in indicators.items():
        g = sub[mask[m_zhouzc]]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')
    g_hold = sub[~((m_zd_neg & m_zc_neg)[m_zhouzc])]
    lines.append(f'{"未触发A(继续持有)":<28s} {len(g_hold):>10,d} {g_hold["未来5天涨幅"].mean():>9.3f}% {g_hold["未来10天涨幅"].mean():>9.3f}% {g_hold["未来20天涨幅"].mean():>9.3f}% {(g_hold["未来5天最低涨幅"]<0).mean()*100:>9.2f}%')

    # ============ ③ 各指标在周线主升(5.2)范围内 ============
    lines.append('')
    lines.append('【③ 各指标在周线主升(5.2:WXZC>0且WXAB>0)范围内触发后收益】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    sub52 = wk[m_zhouzc & m_zhouab]
    for name, mask in indicators.items():
        g = sub52[mask[m_zhouzc & m_zhouab]]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')
    g_hold52 = sub52[~((m_zd_neg & m_zc_neg)[m_zhouzc & m_zhouab])]
    lines.append(f'{"未触发A(继续持有)":<28s} {len(g_hold52):>10,d} {g_hold52["未来5天涨幅"].mean():>9.3f}% {g_hold52["未来10天涨幅"].mean():>9.3f}% {g_hold52["未来20天涨幅"].mean():>9.3f}% {(g_hold52["未来5天最低涨幅"]<0).mean()*100:>9.2f}%')

    # ============ ④ 关键：各指标触发后，未来N天周线WXZC转负概率 ============
    lines.append('')
    lines.append('【④ 关键：各指标触发后，未来N天周线WXZC转负(<0)概率——能否提前捕捉周线转弱】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来5天转负":>12s} {"未来10天转负":>12s} {"未来20天转负":>12s}')
    lines.append('-' * 100)
    for name, mask in indicators.items():
        g = wk[mask]
        n = len(g)
        r5 = (g['未来5天周ZC<0']).mean() * 100
        r10 = (g['未来10天周ZC<0']).mean() * 100
        r20 = (g['未来20天周ZC<0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r5:>11.2f}% {r10:>11.2f}% {r20:>11.2f}%')

    # ============ ⑤ 各指标触发后，未来N天再次满足5.1(WXZC>0)概率 ============
    lines.append('')
    lines.append('【⑤ 各指标触发后，未来N天再次满足5.1(WXZC>0)概率——退出后能否再进】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来5天再满足":>14s} {"未来10天再满足":>14s} {"未来20天再满足":>14s}')
    lines.append('-' * 100)
    for name, mask in indicators.items():
        g = wk[mask]
        n = len(g)
        r5 = (g['未来5天周ZC>0']).mean() * 100
        r10 = (g['未来10天周ZC>0']).mean() * 100
        r20 = (g['未来20天周ZC>0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r5:>13.2f}% {r10:>13.2f}% {r20:>13.2f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()