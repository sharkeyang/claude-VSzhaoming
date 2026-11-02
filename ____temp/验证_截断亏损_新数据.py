#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 (DXZD<0 且 DXZC<0) 与 DXCD 下/忑 的对应关系，及与四土/四波定义的呼应
并重新跑"截断亏损策略"验证（用新数据 135列）
数据源：谕组日 CSV（135列，GBK），全量3446文件
"""
import pandas as pd, glob, os, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_截断亏损_新数据.txt'
DATADIR = r'昭明算展/谕组日'

COL = {
    '日期': 0, '收': 1, '涨幅': 5, '高幅': 6,
    'DXCD': 8, '柱排': 10, '波型': 14,
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
    wk['未来5天最低涨幅'] = wk.groupby('fid')['涨幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).min())
    # 未来N天周ZC<0
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
    m_trigger = m_zd_neg & m_zc_neg  # DXZD<0 且 DXZC<0

    # DXCD 编码
    wk['DXCD_s'] = wk['DXCD'].astype(str)
    m_cd_xia = wk['DXCD_s'] == '下'
    m_cd_te = wk['DXCD_s'] == '忑'
    m_cd_zhong = wk['DXCD_s'] == '中'
    m_cd_zhong2 = wk['DXCD_s'] == '忠'
    m_cd_shang = wk['DXCD_s'] == '上'
    m_cd_tan = wk['DXCD_s'] == '忐'

    # 四土（日线）
    m_wo = m_ze_neg & (m_cd_shang | m_cd_tan)  # 沃土：DXZE>0 + CD上/忐
    m_jin = m_ze_neg & (m_cd_zhong | m_cd_zhong2)  # 鸡肋土：DXZE>0 + CD中/忠
    m_zhi = ~m_ze_neg & (m_cd_shang | m_cd_tan)  # 执念土：DXZE<0 + CD上/忐
    m_jin2 = ~m_ze_neg & (m_cd_zhong | m_cd_zhong2)  # 鸡肋土：DXZE<0 + CD中/忠
    m_jin3 = ~m_ze_neg & (m_cd_xia | m_cd_te)  # 禁土：DXZE<0 + CD下/忑

    # 四波（波型）
    wk['波型_s'] = wk['波型'].astype(str)
    m_shengzhu = wk['波型_s'].str.contains('升主', na=False)  # 龙
    m_jiangzhuan = wk['波型_s'].str.contains('降转', na=False)  # 武
    m_jiangzhu = wk['波型_s'].str.contains('降主', na=False)  # 虎
    m_shengzhuan = wk['波型_s'].str.contains('升转', na=False)  # 雀

    lines = []
    lines.append('=' * 100)
    lines.append('验证 (DXZD<0 且 DXZC<0) 与 DXCD 下/忑 的对应关系，及与四土/四波呼应')
    lines.append('数据源：谕组日 CSV（135列，GBK），全量3446文件')
    lines.append('=' * 100)

    # ============ 1. DXZD<0且DXZC<0 与 DXCD 编码的对应 ============
    lines.append('')
    lines.append('【1. 触发(DXZD<0且DXZC<0)时，DXCD 编码分布】')
    lines.append('-' * 100)
    g_trig = wk[m_trigger]
    n_trig = len(g_trig)
    lines.append(f'触发样本: {n_trig:,d}')
    for cd, name in [('上','上'),('中','中'),('下','下'),('忐','忐'),('忠','忠'),('忑','忑')]:
        cnt = (g_trig['DXCD_s'] == cd).sum()
        pct = cnt / n_trig * 100
        lines.append(f'  DXCD={name}: {cnt:,d} ({pct:.2f}%)')

    # ============ 2. DXCD=下 时，DXZD 的分布 ============
    lines.append('')
    lines.append('【2. DXCD=下 时，DXZD/DXZC 的分布（验证"下"是否=DXZD<0且DXZC<0）】')
    lines.append('-' * 100)
    g_xia = wk[m_cd_xia]
    n_xia = len(g_xia)
    lines.append(f'DXCD=下 样本: {n_xia:,d}')
    zd_neg = (g_xia['DTZD'] < 0).mean() * 100
    zc_neg = (g_xia['日ZC'] < 0).mean() * 100
    both_neg = (g_xia['DTZD'] < 0).mean() * 100
    lines.append(f'  DXZD<0: {zd_neg:.2f}%')
    lines.append(f'  DXZC<0: {zc_neg:.2f}%')
    lines.append(f'  DXZD<0且DXZC<0: {both_neg:.2f}%')

    # ============ 3. DXCD=忑 时，DXZD/DXZC 的分布 ============
    lines.append('')
    lines.append('【3. DXCD=忑 时，DXZD/DXZC 的分布（验证"忑"是否=DXZD<0且DXZC<0）】')
    lines.append('-' * 100)
    g_te = wk[m_cd_te]
    n_te = len(g_te)
    lines.append(f'DXCD=忑 样本: {n_te:,d}')
    zd_neg = (g_te['DTZD'] < 0).mean() * 100
    zc_neg = (g_te['日ZC'] < 0).mean() * 100
    both_neg = (g_te['DTZD'] < 0).mean() * 100
    lines.append(f'  DXZD<0: {zd_neg:.2f}%')
    lines.append(f'  DXZC<0: {zc_neg:.2f}%')
    lines.append(f'  DXZD<0且DXZC<0: {both_neg:.2f}%')

    # ============ 4. 触发(DXZD<0且DXZC<0) 落在哪个四土 ============
    lines.append('')
    lines.append('【4. 触发(DXZD<0且DXZC<0) 落在哪个四土】')
    lines.append('-' * 100)
    for name, m in [('沃土(DXZE>0+CD上/忐)', m_wo), ('鸡肋土(DXZE>0+CD中/忠)', m_jin),
                    ('执念土(DXZE<0+CD上/忐)', m_zhi), ('鸡肋土(DXZE<0+CD中/忠)', m_jin2),
                    ('禁土(DXZE<0+CD下/忑)', m_jin3)]:
        cnt = (m_trigger & m).sum()
        pct = cnt / n_trig * 100
        lines.append(f'  {name}: {cnt:,d} ({pct:.2f}%)')

    # ============ 5. 触发(DXZD<0且DXZC<0) 落在哪个四波 ============
    lines.append('')
    lines.append('【5. 触发(DXZD<0且DXZC<0) 落在哪个四波】')
    lines.append('-' * 100)
    for name, m in [('龙(升主)', m_shengzhu), ('武(降转)', m_jiangzhuan),
                    ('虎(降主)', m_jiangzhu), ('雀(升转)', m_shengzhuan)]:
        cnt = (m_trigger & m).sum()
        pct = cnt / n_trig * 100
        lines.append(f'  {name}: {cnt:,d} ({pct:.2f}%)')

    # ============ 6. 重新验证截断亏损策略 ============
    lines.append('')
    lines.append('【6. 截断亏损策略重新验证（新数据）】')
    lines.append('-' * 100)
    m_zhouzc = wk['周ZC'] > 0
    m_zhouab = wk['周AB'] > 0

    # 各止损指标
    indicators = {
        'A. DXZD<0且DXZC<0': m_trigger,
        'B. DXZD<0或DXZC<0': m_zd_neg | m_zc_neg,
        'C. DXZE<0': m_ze_neg,
        'D. DXZD<0且DXZC<0且DXZE<0': m_trigger & m_ze_neg,
    }

    lines.append('【6.1 各指标触发后收益（全量）】')
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s} {"5天继续跌":>10s}')
    lines.append('-' * 100)
    for name, mask in indicators.items():
        g = wk[mask]
        n = len(g)
        avg5 = g['未来5天涨幅'].mean()
        avg10 = g['未来10天涨幅'].mean()
        avg20 = g['未来20天涨幅'].mean()
        cont = (g['未来5天最低涨幅'] < 0).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {avg5:>9.3f}% {avg10:>9.3f}% {avg20:>9.3f}% {cont:>9.2f}%')

    lines.append('')
    lines.append('【6.2 各指标触发后，未来N天周线WXZC转负概率】')
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"未来5天转负":>12s} {"未来10天转负":>12s} {"未来20天转负":>12s}')
    lines.append('-' * 100)
    for name, mask in indicators.items():
        g = wk[mask]
        n = len(g)
        r5 = (g['未来5天周ZC<0']).mean() * 100
        r10 = (g['未来10天周ZC<0']).mean() * 100
        r20 = (g['未来20天周ZC<0']).mean() * 100
        lines.append(f'{name:<28s} {n:>10,d} {r5:>11.2f}% {r10:>11.2f}% {r20:>11.2f}%')

    lines.append('')
    lines.append('【6.3 周线主升(5.1:WXZC>0)范围内各指标触发后收益】')
    lines.append(f'{"指标":<28s} {"触发样本":>10s} {"5天均涨幅":>10s} {"10天均涨幅":>10s} {"20天均涨幅":>10s}')
    lines.append('-' * 100)
    sub = wk[m_zhouzc]
    for name, mask in indicators.items():
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