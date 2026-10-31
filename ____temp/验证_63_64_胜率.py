#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 6.3 方法日H冲（升连≥2%）和 6.4 方法日I冲（BSHA5）的胜率数据
数据源：谕组日 CSV（131列，GBK编码）
列映射依据：_产出物/_工具/元数据_vba数据映射_日类.md

口径对齐 C7 §5.3.8：
- 6.3 前提 = 甲乙己 + ZC>0（文档基线），首升连+涨幅≥2%
- "5天≥3%" = 未来5天最高盘中涨幅(HR)≥3%
- 6.4 前提 = 甲乙己 + ZC>0，等1/等3 + BSHA5
- "次日P3" = 次日高幅(HR)≥3%
"""
import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

OUT = r'____temp/_验证_63_64_胜率.txt'
DATADIR = r'昭明算展/谕组日'

# 关键列（0-based，依据元数据映射表）
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
    # 未来5天最高盘中涨幅(HR)：未来5天每天的HR最大值
    wk['未来5天最高HR'] = wk.groupby('fid')['高幅'].transform(
        lambda s: s.shift(-1).rolling(5, min_periods=1).max())
    # 次日高幅
    wk['下日HR'] = wk['次日高幅']
    # 前一日柱排（用于判定首升连）
    wk['前柱排'] = wk.groupby('fid')['柱排'].shift(1)
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def stats_hr(g, col='下日HR', thresh=3):
    n = len(g)
    if n == 0:
        return None, None, n
    p3 = (g[col] >= thresh).mean() * 100
    avg = g[col].mean()
    return p3, avg, n

def stats5(g):
    n = len(g)
    if n == 0:
        return None, None, n
    p3 = (g['未来5天最高HR'] >= 3).mean() * 100
    avg = g['未来5天最高HR'].mean()
    return p3, avg, n

def main():
    print('加载数据...', flush=True)
    wk = load_all()

    wk['柱排_s'] = wk['柱排'].astype(str)
    wk['前柱排_s'] = wk['前柱排'].astype(str)
    wk['DXAB_s'] = wk['DXAB'].astype(str)
    wk['DXCD_s'] = wk['DXCD'].astype(str)
    wk['日等型_s'] = wk['日等型'].astype(str)

    # 甲乙己：DXAB首字符 ∈ {a,b,r}
    m_jiayiji = wk['DXAB_s'].str[0].isin(['a', 'b', 'r'])
    # ZC>0
    m_zc = wk['日ZC'] > 0
    # 沃土：DXZE>0 + DXCD∈{上,忐}
    m_wotu = (wk['日ZE'] > 0) & (wk['DXCD_s'].isin(['上', '忐']))
    # 升连：柱排以"升.尾连"开头
    m_shenglian = wk['柱排_s'].str.startswith('升.尾连', na=False)
    # 首升连：当前是升连 且 前一日非升连
    m_qian_shenglian = wk['前柱排_s'].str.startswith('升.尾连', na=False)
    m_shou_shenglian = m_shenglian & ~m_qian_shenglian
    # 涨幅≥2%
    m_zhangfu2 = wk['涨幅'] >= 2
    # BSHA5
    m_bsha5 = wk['BSHA'] >= 5
    # 等1/等3
    m_deng1 = wk['日等型_s'] == '等1'
    m_deng3 = wk['日等型_s'] == '等3'

    lines = []
    lines.append('=' * 84)
    lines.append('验证 6.3 方法日H冲（升连≥2%）和 6.4 方法日I冲（BSHA5）胜率')
    lines.append('数据源：谕组日 CSV（131列，GBK），全量3449文件')
    lines.append('口径：5天≥3% = 未来5天最高盘中涨幅(HR)≥3%；次日P3 = 次日高幅≥3%')
    lines.append('=' * 84)

    # ============ 6.3 方法日H冲 ============
    lines.append('')
    lines.append('【6.3 方法日H冲：升连≥2%】')
    lines.append('-' * 84)
    lines.append(f'{"条件":<46s} {"样本":>10s} {"5天≥3%":>8s} {"5天均HR":>8s}')
    lines.append('-' * 84)

    items_63 = [
        ('基线(甲乙己ZC>0)', m_jiayiji & m_zc),
        ('  首升连(无限制)', m_jiayiji & m_zc & m_shou_shenglian),
        ('  首升连+涨幅≥2%', m_jiayiji & m_zc & m_shou_shenglian & m_zhangfu2),
        ('  首升连+涨幅<2%', m_jiayiji & m_zc & m_shou_shenglian & ~m_zhangfu2),
        ('  首升连+涨幅≥2.5%', m_jiayiji & m_zc & m_shou_shenglian & (wk['涨幅'] >= 2.5)),
        ('  首升连+涨幅≥3%', m_jiayiji & m_zc & m_shou_shenglian & (wk['涨幅'] >= 3)),
        ('  升连链中后段', m_jiayiji & m_zc & m_shenglian & ~m_shou_shenglian),
    ]
    for name, mask in items_63:
        p3, avg, n = stats5(wk[mask])
        if p3 is None:
            lines.append(f'{name:<46s} {n:>10,d} {"-":>8s} {"-":>8s}')
        else:
            lines.append(f'{name:<46s} {n:>10,d} {p3:>7.2f}% {avg:>7.2f}%')

    # 6.3 增强因子
    lines.append('')
    lines.append('【6.3 增强因子（首升连+涨幅≥2% 基础上）】')
    lines.append('-' * 84)
    base_63 = m_jiayiji & m_zc & m_shou_shenglian & m_zhangfu2
    items_63b = [
        ('  +BSHA≥5', base_63 & m_bsha5),
        ('  +BSHA<2', base_63 & (wk['BSHA'] < 2)),
        ('  +等3', base_63 & m_deng3),
        ('  +等1', base_63 & m_deng1),
        ('  +沃土', base_63 & m_wotu),
    ]
    for name, mask in items_63b:
        p3, avg, n = stats5(wk[mask])
        if p3 is None:
            lines.append(f'{name:<46s} {n:>10,d} {"-":>8s} {"-":>8s}')
        else:
            lines.append(f'{name:<46s} {n:>10,d} {p3:>7.2f}% {avg:>7.2f}%')

    # ============ 6.4 方法日I冲 ============
    lines.append('')
    lines.append('【6.4 方法日I冲：BSHA5 触发器】')
    lines.append('-' * 84)
    lines.append(f'{"条件":<46s} {"样本":>10s} {"次日P3":>8s} {"次日均高":>8s}')
    lines.append('-' * 84)

    items_64 = [
        ('基线(甲乙己ZC>0)', m_jiayiji & m_zc),
        ('  等1_当天介入', m_jiayiji & m_zc & m_deng1),
        ('  等1_BSHA5', m_jiayiji & m_zc & m_deng1 & m_bsha5),
        ('  等3_BSHA5', m_jiayiji & m_zc & m_deng3 & m_bsha5),
        ('  等3_当天介入', m_jiayiji & m_zc & m_deng3),
        ('  等5_首下破', m_jiayiji & m_zc & (wk['日等型_s'] == '等5')),
    ]
    for name, mask in items_64:
        p3, avg, n = stats_hr(wk[mask])
        if p3 is None:
            lines.append(f'{name:<46s} {n:>10,d} {"-":>8s} {"-":>8s}')
        else:
            lines.append(f'{name:<46s} {n:>10,d} {p3:>7.2f}% {avg:>7.2f}%')

    # ============ 前提验证：脱离周线主升 ============
    lines.append('')
    lines.append('【前提验证：脱离周线主升（周ZC>0）时 6.3/6.4 是否仍有效】')
    lines.append('-' * 84)
    m_zhouzc = wk['周ZC'] > 0
    items_premise = [
        ('首升连+涨幅≥2% + 周ZC>0', base_63 & m_zhouzc),
        ('首升连+涨幅≥2% + 周ZC≤0', base_63 & ~m_zhouzc),
        ('等1_BSHA5 + 周ZC>0', m_jiayiji & m_zc & m_deng1 & m_bsha5 & m_zhouzc),
        ('等1_BSHA5 + 周ZC≤0', m_jiayiji & m_zc & m_deng1 & m_bsha5 & ~m_zhouzc),
    ]
    for name, mask in items_premise:
        if '首升连' in name:
            p3, avg, n = stats5(wk[mask])
            if p3 is None:
                lines.append(f'{name:<46s} {n:>10,d} {"-":>8s} {"-":>8s}')
            else:
                lines.append(f'{name:<46s} {n:>10,d} {p3:>7.2f}% {avg:>7.2f}%')
        else:
            p3, avg, n = stats_hr(wk[mask])
            if p3 is None:
                lines.append(f'{name:<46s} {n:>10,d} {"-":>8s} {"-":>8s}')
            else:
                lines.append(f'{name:<46s} {n:>10,d} {p3:>7.2f}% {avg:>7.2f}%')

    lines.append('')
    lines.append('=' * 84)
    lines.append('完成')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {OUT}')

if __name__ == '__main__':
    main()