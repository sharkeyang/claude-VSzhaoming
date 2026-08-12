# -*- coding: utf-8 -*-
"""
DTZA阈值优化分析 — 等2vs等4(DTZA 2~3 vs ≥4) 和 等6vs等8(DTZA -3~-2 vs ≤-4)
核心问题：阈值3（绝对值）是否是最优分割点？
统计方法：按DTZA每个值分组，固定末符条件，穷举所有可能的阈值分割
"""
import sys, time, os, glob, warnings
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800  # 与MC3.3.5抽样一致

# ========== 上侧分析：末符∈CDEF，DTZA>0 ==========
# 目标：找最优阈值 t，让两类（DTZA≤t vs DTZA>t）方向差异最大
# 方向指标：下一柱DTZA>0（继续走）vs <0（反转）

# ========== 下侧分析：末符∈ABCD，DTZA<0 ==========
# 目标：找最优阈值 t（负值），让两类（DTZA≥t vs DTZA<t）方向差异最大
# 方向指标：下一柱DTZA>0（反弹）vs <0（继续跌）

def analyze_threshold(df, side='upper'):
    """分析DTZA每个值的细粒度方向倾向"""
    df = df.copy()
    df['next_za'] = df['日ZA'].shift(-1)
    df['za_val'] = df['日ZA'].astype(float)
    df['last_char'] = df['中符串'].astype(str).str[-1]

    if side == 'upper':
        # 上侧：末符∈CDEF，DTZA>0
        sub = df[(df['za_val'] > 0) & (df['last_char'].isin(['C','D','E','F']))].copy()
        sub['za_int'] = sub['za_val'].astype(int)
        # 按DTZA每个值分组
        stats = []
        for v in sorted(sub['za_int'].unique()):
            s = sub[sub['za_int'] == v]
            next_za = s['next_za'].dropna()
            if len(next_za) == 0: continue
            pos = (next_za > 0).sum()
            neg = (next_za < 0).sum()
            zero = (next_za == 0).sum()
            total = len(next_za)
            # 额外：冲高概率
            nh = s['次日高幅'].dropna()
            stats.append({
                'DTZA': v, '样本': total,
                '继续走>0': pos/total, '反转<0': neg/total, '回归=0': zero/total,
                '冲≥2%': (nh>2).sum()/len(nh) if len(nh)>0 else 0,
                '冲≥3%': (nh>3).sum()/len(nh) if len(nh)>0 else 0,
                '平均冲高': nh.mean() if len(nh)>0 else 0,
            })
        # 穷举所有可能的阈值分割
        if len(stats) > 1:
            za_vals = sorted([s['DTZA'] for s in stats])
            splits = []
            for i in range(1, len(za_vals)):
                low_vals = za_vals[:i]
                high_vals = za_vals[i:]
                low = [s for s in stats if s['DTZA'] in low_vals]
                high = [s for s in stats if s['DTZA'] in high_vals]
                low_n = sum(s['样本'] for s in low)
                high_n = sum(s['样本'] for s in high)
                low_pos = sum(s['继续走>0']*s['样本'] for s in low) / low_n
                high_pos = sum(s['继续走>0']*s['样本'] for s in high) / high_n
                low_neg = sum(s['反转<0']*s['样本'] for s in low) / high_n
                high_neg = sum(s['反转<0']*s['样本'] for s in high) / high_n
                low_3 = sum(s['冲≥3%']*s['样本'] for s in low) / low_n
                high_3 = sum(s['冲≥3%']*s['样本'] for s in high) / high_n
                splits.append({
                    '阈值': f'≤{high_vals[0]-1} vs ≥{high_vals[0]}',
                    '低类': f'DTZA={low_vals[0]}~{low_vals[-1]}',
                    '高类': f'DTZA={high_vals[0]}~{high_vals[-1]}',
                    '低类样本': low_n, '高类样本': high_n,
                    '低类继续走': low_pos, '高类继续走': high_pos,
                    '低类反转': low_neg, '高类反转': high_neg,
                    '继续走差异': low_pos - high_pos,
                    '反转差异': high_neg - low_neg,
                    '低类冲≥3%': low_3, '高类冲≥3%': high_3,
                    '冲≥3%差异': low_3 - high_3,
                })
        return stats, splits

    elif side == 'lower':
        # 下侧：末符∈ABCD，DTZA<0
        sub = df[(df['za_val'] < 0) & (df['last_char'].isin(['A','B','C','D']))].copy()
        sub['za_int'] = sub['za_val'].astype(int)
        stats = []
        for v in sorted(sub['za_int'].unique(), reverse=True):
            s = sub[sub['za_int'] == v]
            next_za = s['next_za'].dropna()
            if len(next_za) == 0: continue
            pos = (next_za > 0).sum()
            neg = (next_za < 0).sum()
            zero = (next_za == 0).sum()
            total = len(next_za)
            nh = s['次日高幅'].dropna()
            stats.append({
                'DTZA': v, '样本': total,
                '反弹>0': pos/total, '继续跌<0': neg/total, '回归=0': zero/total,
                '冲≥2%': (nh>2).sum()/len(nh) if len(nh)>0 else 0,
                '冲≥3%': (nh>3).sum()/len(nh) if len(nh)>0 else 0,
                '平均冲高': nh.mean() if len(nh)>0 else 0,
            })
        if len(stats) > 1:
            za_vals = sorted([s['DTZA'] for s in stats], reverse=True)
            splits = []
            for i in range(1, len(za_vals)):
                # 低DTZA（更负）= 高类，高DTZA（接近0）= 低类
                more_neg_vals = za_vals[:i]  # 更负（DTZA更小）
                less_neg_vals = za_vals[i:]  # 较正（DTZA更大）
                more_neg = [s for s in stats if s['DTZA'] in more_neg_vals]
                less_neg = [s for s in stats if s['DTZA'] in less_neg_vals]
                mn_n = sum(s['样本'] for s in more_neg)
                ln_n = sum(s['样本'] for s in less_neg)
                # 反弹：DTZA>0的比例
                mn_pos = sum(s['反弹>0']*s['样本'] for s in more_neg) / mn_n
                ln_pos = sum(s['反弹>0']*s['样本'] for s in less_neg) / ln_n
                # 继续跌
                mn_neg = sum(s['继续跌<0']*s['样本'] for s in more_neg) / mn_n
                ln_neg = sum(s['继续跌<0']*s['样本'] for s in less_neg) / ln_n
                mn_3 = sum(s['冲≥3%']*s['样本'] for s in more_neg) / mn_n
                ln_3 = sum(s['冲≥3%']*s['样本'] for s in less_neg) / ln_n
                splits.append({
                    '阈值': f'≤{more_neg_vals[-1]} vs ≥{less_neg_vals[0]}',
                    '更负类': f'DTZA={more_neg_vals[0]}~{more_neg_vals[-1]}',
                    '较正类': f'DTZA={less_neg_vals[0]}~{less_neg_vals[-1]}',
                    '更负类样本': mn_n, '较正类样本': ln_n,
                    '更负类反弹': mn_pos, '较正类反弹': ln_pos,
                    '更负类继续跌': mn_neg, '较正类继续跌': ln_neg,
                    '反弹差异': ln_pos - mn_pos,
                    '继续跌差异': mn_neg - ln_neg,
                    '更负类冲≥3%': mn_3, '较正类冲≥3%': ln_3,
                    '冲≥3%差异': ln_3 - mn_3,
                })
        return stats, splits

    return [], []

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    np.random.seed(42)
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}')

    frames = []
    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk')
            if '日ZA' not in df.columns or len(df) < 100: continue
            frames.append(df)
        except:
            continue
        if (i+1) % 200 == 0:
            print(f'  已读 {i+1}/{len(sampled)} ({time.time()-t0:.0f}s)')

    df_all = pd.concat(frames, ignore_index=True)
    print(f'总样本: {len(df_all):,}, 耗时 {time.time()-t0:.0f}s')

    # ========== 上侧分析 ==========
    print('\n' + '='*70)
    print('【上侧】末符∈CDEF, DTZA>0 — 按DTZA每个值统计')
    print('='*70)
    upper_stats, upper_splits = analyze_threshold(df_all, 'upper')
    upper_stats.sort(key=lambda x: x['DTZA'])
    print(f'\n{"DTZA":>5} {"样本":>8} {"继续走>0":>10} {"反转<0":>8} {"回归=0":>8} {"冲≥2%":>8} {"冲≥3%":>8} {"均冲高":>8}')
    print('-'*65)
    for s in upper_stats:
        print(f'{s["DTZA"]:>5} {s["样本"]:>8,} {s["继续走>0"]:>9.1%} {s["反转<0"]:>7.1%} {s["回归=0"]:>7.1%} {s["冲≥2%"]:>7.1%} {s["冲≥3%"]:>7.1%} {s["平均冲高"]:>7.2f}%')

    # 穷举所有阈值分割
    print('\n穷举阈值分割（按"继续走"差异降序 = 方向区分度最大）：')
    upper_splits.sort(key=lambda x: abs(x['继续走差异']), reverse=True)
    print(f'\n{"阈值(分割点)":<20} {"低类":<20} {"高类":<20} {"低类样本":>10} {"高类样本":>10} {"低类继续":>8} {"高类继续":>8} {"继续差异":>8} {"低冲≥3%":>8} {"高冲≥3%":>8}')
    print('-'*120)
    for s in upper_splits:
        print(f'{s["阈值"]:<20} {s["低类"]:<20} {s["高类"]:<20} {s["低类样本"]:>10,} {s["高类样本"]:>10,} {s["低类继续走"]:>7.1%} {s["高类继续走"]:>7.1%} {s["继续走差异"]:>7.1%} {s["低类冲≥3%"]:>7.1%} {s["高类冲≥3%"]:>7.1%}')

    # ========== 下侧分析 ==========
    print('\n' + '='*70)
    print('【下侧】末符∈ABCD, DTZA<0 — 按DTZA每个值统计')
    print('='*70)
    lower_stats, lower_splits = analyze_threshold(df_all, 'lower')
    lower_stats.sort(key=lambda x: x['DTZA'], reverse=True)
    print(f'\n{"DTZA":>5} {"样本":>8} {"反弹>0":>8} {"继续跌<0":>10} {"回归=0":>8} {"冲≥2%":>8} {"冲≥3%":>8} {"均冲高":>8}')
    print('-'*65)
    for s in lower_stats:
        print(f'{s["DTZA"]:>5} {s["样本"]:>8,} {s["反弹>0"]:>7.1%} {s["继续跌<0"]:>9.1%} {s["回归=0"]:>7.1%} {s["冲≥2%"]:>7.1%} {s["冲≥3%"]:>7.1%} {s["平均冲高"]:>7.2f}%')

    # 穷举所有阈值分割
    print('\n穷举阈值分割（按"反弹差异"降序 = 方向区分度最大）：')
    lower_splits.sort(key=lambda x: abs(x['反弹差异']), reverse=True)
    print(f'\n{"阈值(分割点)":<20} {"更负类":<22} {"较正类":<22} {"更负样本":>10} {"较正样本":>10} {"更负反弹":>8} {"较正反弹":>8} {"反弹差异":>8} {"更负冲≥3%":>10} {"较正冲≥3%":>10}')
    print('-'*120)
    for s in lower_splits:
        print(f'{s["阈值"]:<20} {s["更负类"]:<22} {s["较正类"]:<22} {s["更负类样本"]:>10,} {s["较正类样本"]:>10,} {s["更负类反弹"]:>7.1%} {s["较正类反弹"]:>7.1%} {s["反弹差异"]:>7.1%} {s["更负类冲≥3%"]:>9.1%} {s["较正类冲≥3%"]:>9.1%}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()