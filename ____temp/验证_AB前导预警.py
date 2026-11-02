#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 A/B 作为 C(DXZE<0) 的前导预警指标
前提：C(DXZE<0) 已确定为强制止损（周线转负94.41%）
问题：A(DXZD<0且DXZC<0) 和 B(DXZD<0或DXZC<0) 触发后，未来N天触发 C 的概率？
      如果 A/B 触发后很快触发 C，则 A/B 可作为 C 的前导预警（提前减仓/准备退出）
数据源：谕组日 CSV（131列，GBK），全量3449文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_AB前导预警.txt'
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
    wk['未来5天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(5, min_periods=1).sum())
    wk['未来10天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(10, min_periods=1).sum())
    wk['未来20天涨幅'] = wk.groupby('fid')['涨幅'].transform(lambda s: s.shift(-1).rolling(20, min_periods=1).sum())
    # 未来N天触发 C(DXZE<0) 概率
    for n in [3, 5, 10, 20]:
        wk[f'未来{n}天DXZE<0'] = wk.groupby('fid')['日ZE'].transform(
            lambda s: s.shift(-1).rolling(n, min_periods=1).min() < 0)
    # 未来N天周ZC<0 概率
    for n in [5, 10, 20]:
        wk[f'未来{n}天周ZC<0'] = wk.groupby('fid')['周ZC'].transform(
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

    # 指标
    A = m_zd_neg & m_zc_neg  # DXZD<0且DXZC<0
    B = m_zd_neg | m_zc_neg  # DXZD<0或DXZC<0
    C = m_ze_neg             # DXZE<0

    # 周线主升
    m_zhouzc = wk['周ZC'] > 0

    lines = []
    lines.append('=' * 100)
    lines.append('验证 A/B 作为 C(DXZE<0) 的前导预警指标')
    lines.append('前提：C(DXZE<0) 已确定为强制止损（周线转负94.41%）')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('=' * 100)

    # ============ 1. A/B 触发后，未来N天触发 C 的概率 ============
    lines.append('')
    lines.append('【1. A/B 触发后，未来N天触发 C(DXZE<0) 的概率】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来3天触发C":>14s} {"未来5天触发C":>14s} {"未来10天触发C":>14s} {"未来20天触发C":>14s}')
    lines.append('-' * 100)
    for name, mask in [('A. DXZD<0且DXZC<0', A), ('B. DXZD<0或DXZC<0', B)]:
        g = wk[mask]
        n = len(g)
        r3 = (g['未来3天DXZE<0']).mean() * 100
        r5 = (g['未来5天DXZE<0']).mean() * 100
        r10 = (g['未来10天DXZE<0']).mean() * 100
        r20 = (g['未来20天DXZE<0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r3:>13.2f}% {r5:>13.2f}% {r10:>13.2f}% {r20:>13.2f}%')

    # ============ 2. 周线主升范围内 A/B 触发后，未来N天触发 C 的概率 ============
    lines.append('')
    lines.append('【2. 周线主升(5.1:WXZC>0)范围内 A/B 触发后，未来N天触发 C 的概率】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来3天触发C":>14s} {"未来5天触发C":>14s} {"未来10天触发C":>14s} {"未来20天触发C":>14s}')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    for name, mask in [('A. DXZD<0且DXZC<0', A), ('B. DXZD<0或DXZC<0', B)]:
        g = sub[mask[m_zhouzc]]
        n = len(g)
        r3 = (g['未来3天DXZE<0']).mean() * 100
        r5 = (g['未来5天DXZE<0']).mean() * 100
        r10 = (g['未来10天DXZE<0']).mean() * 100
        r20 = (g['未来20天DXZE<0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r3:>13.2f}% {r5:>13.2f}% {r10:>13.2f}% {r20:>13.2f}%')

    # ============ 3. A/B 触发后，未来N天周线转负概率（对比 C） ============
    lines.append('')
    lines.append('【3. A/B 触发后，未来N天周线WXZC转负概率（对比 C）】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来5天转负":>12s} {"未来10天转负":>12s} {"未来20天转负":>12s}')
    lines.append('-' * 100)
    for name, mask in [('A. DXZD<0且DXZC<0', A), ('B. DXZD<0或DXZC<0', B), ('C. DXZE<0', C)]:
        g = wk[mask]
        n = len(g)
        r5 = (g['未来5天周ZC<0']).mean() * 100
        r10 = (g['未来10天周ZC<0']).mean() * 100
        r20 = (g['未来20天周ZC<0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r5:>11.2f}% {r10:>11.2f}% {r20:>11.2f}%')

    # ============ 4. 周线主升范围内 A/B 触发后收益（对比 C） ============
    lines.append('')
    lines.append('【4. 周线主升(5.1)范围内 A/B/C 触发后收益】')
    lines.append('-' * 100)
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s}')
    lines.append('-' * 100)
    for name, mask in [('A. DXZD<0且DXZC<0', A), ('B. DXZD<0或DXZC<0', B), ('C. DXZE<0', C)]:
        g = sub[mask[m_zhouzc]]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        lines.append(f'{name:<28s} {n:>10,d} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}%')

    lines.append('')
    lines.append('=' * 100)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()