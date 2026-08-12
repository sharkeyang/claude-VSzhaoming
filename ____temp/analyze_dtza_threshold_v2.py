# -*- coding: utf-8 -*-
"""
DTZA阈值优化分析 v2 — 全量7461文件
核心问题：等高线等2vs等4、等6vs等8的DTZA阈值3是否最优？
重点1：DTZA=-3~3"频繁贯穿积蓄力量区"的完整画像
重点2：末符∈AB vs CDEF 在DTZA=3附近的分布（分流到等3 vs 等2/等4）
重点3：方向倾向的定义 = 下一柱DTZA方向 + 下日冲高幅度
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
np.random.seed(42)

# DTZA值范围（重点看-8~8，外围合并）
ZAS = list(range(-8, 9))  # -8..8

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    # 增量聚合
    # za -> {n, pos, neg, zero, nh2, nh3, nh_sum, ab_n, cdef_n, other_n,
    #        ab_pos, cdef_pos}  (pos=下一柱ZA>0, neg=下一柱ZA<0)
    agg = {}
    for v in ZAS + ['low', 'high']:
        agg[v] = {'n':0, 'pos':0, 'neg':0, 'zero':0,
                  'nh2':0, 'nh3':0, 'nh_sum':0.0,
                  'ab_n':0, 'cdef_n':0, 'other_n':0,
                  'ab_pos':0, 'cdef_pos':0}
    # 全量计数（用于占比）
    total_n = 0

    for i, f in enumerate(files):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅'])
        except: continue
        if len(df) < 50: continue
        total_n += len(df)
        za = df['日ZA'].astype(float)
        next_za = za.shift(-1)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)

        za_int = za.round().astype(int)

        # 末符分组
        is_ab = last.isin(['A','B'])
        is_cdef = last.isin(['C','D','E','F'])

        # 对每个关注的DTZA值聚合
        for v in ZAS + ['low', 'high']:
            if v == 'low':
                m = (za_int < -8)
            elif v == 'high':
                m = (za_int > 8)
            else:
                m = (za_int == v)
            if not m.any(): continue
            s = agg[v]
            n = int(m.sum()); s['n'] += n
            nz = next_za[m].dropna()
            if len(nz) > 0:
                s['pos'] += int((nz>0).sum())
                s['neg'] += int((nz<0).sum())
                s['zero'] += int((nz==0).sum())
            nhn = nh[m].dropna()
            if len(nhn) > 0:
                s['nh2'] += int((nhn>2).sum())
                s['nh3'] += int((nhn>3).sum())
                s['nh_sum'] += float(nhn.sum())
            s['ab_n'] += int((is_ab & m).sum())
            s['cdef_n'] += int((is_cdef & m).sum())
            s['other_n'] += int((~is_ab & ~is_cdef & m).sum())
            # 末符分组下的方向
            abm = (is_ab & m)
            if abm.any():
                nz_ab = next_za[abm].dropna()
                s['ab_pos'] += int((nz_ab>0).sum())
            cdm = (is_cdef & m)
            if cdm.any():
                nz_cd = next_za[cdm].dropna()
                s['cdef_pos'] += int((nz_cd>0).sum())

        if (i+1) % 1000 == 0:
            print(f'  {i+1}/{len(files)} {time.time()-t0:.0f}s', flush=True)

    print(f'完成 {len(files)} 文件, 总样本 {total_n:,}, 耗时 {time.time()-t0:.0f}s', flush=True)

    # ========== 输出 1：DTZA逐值画像 ==========
    print('\n' + '='*80)
    print('【表1】DTZA=-8~8 逐值画像（全量）')
    print('='*80)
    print(f'{"ZA":>4} {"样本":>9} {"占全量":>7} {"下柱>0":>7} {"下柱<0":>7} {"AB%":>6} {"CDEF%":>8} {"AB下柱>0":>9} {"CDEF下柱>0":>10} {"冲≥2%":>7} {"冲≥3%":>7} {"均冲高":>7}')
    print('-'*100)
    for v in ZAS:
        s = agg[v]
        if s['n'] == 0: continue
        pos_r = s['pos']/s['n'] if s['n'] else 0
        neg_r = s['neg']/s['n'] if s['n'] else 0
        ab_r = s['ab_n']/s['n'] if s['n'] else 0
        cd_r = s['cdef_n']/s['n'] if s['n'] else 0
        ab_pos_r = s['ab_pos']/s['ab_n'] if s['ab_n'] else 0
        cd_pos_r = s['cdef_pos']/s['cdef_n'] if s['cdef_n'] else 0
        nh2_r = s['nh2']/s['n'] if s['n'] else 0
        nh3_r = s['nh3']/s['n'] if s['n'] else 0
        avg = s['nh_sum']/s['n'] if s['n'] else 0
        print(f'{v:>4} {s["n"]:>9,} {s["n"]/total_n:>6.1%} {pos_r:>6.1%} {neg_r:>6.1%} {ab_r:>5.1%} {cd_r:>7.1%} {ab_pos_r:>8.1%} {cd_pos_r:>9.1%} {nh2_r:>6.1%} {nh3_r:>6.1%} {avg:>6.2f}%')

    # ========== 输出 2：DTZA=-3~3 频繁贯穿区 vs 稳态区 ==========
    print('\n' + '='*80)
    print('【表2】频繁贯穿区(-3~3) vs 稳态区(|ZA|>3) — 完整方向画像')
    print('='*80)
    regions = {
        '负稳态(Z≤-4)': [v for v in ZAS if v <= -4] + ['low'],
        '负贯穿(-3~-1)': [v for v in ZAS if v >= -3 and v <= -1],
        '零轴(0)': [0],
        '正贯穿(1~3)': [v for v in ZAS if v >= 1 and v <= 3],
        '正稳态(Z≥4)': [v for v in ZAS if v >= 4] + ['high'],
    }

    print(f'{"区域":<18} {"样本":>10} {"下柱>0":>8} {"下柱<0":>8} {"冲≥2%":>8} {"冲≥3%":>8} {"均冲高":>8}')
    print('-'*70)
    for rname, vals in regions.items():
        n = sum(agg[v]['n'] for v in vals)
        pos = sum(agg[v]['pos'] for v in vals)
        neg = sum(agg[v]['neg'] for v in vals)
        nh2 = sum(agg[v]['nh2'] for v in vals)
        nh3 = sum(agg[v]['nh3'] for v in vals)
        nhs = sum(agg[v]['nh_sum'] for v in vals)
        if n == 0: continue
        print(f'{rname:<18} {n:>10,} {pos/n:>7.1%} {neg/n:>7.1%} {nh2/n:>7.1%} {nh3/n:>7.1%} {nhs/n:>7.2f}%')

    # ========== 输出 3a：上侧CDEF末符：不同DTZA阈值的方向区分度 ==========
    print('\n' + '='*80)
    print('【表3a】上侧CDEF末符：不同DTZA阈值的方向区分度')
    print('='*80)
    # 上侧CDEF：等2(近) vs 等4(远)
    def calc_upper(t):
        near_vals = [2,3,4,5,6,7,8]
        near = [v for v in near_vals if v <= t]
        far = [v for v in near_vals if v > t] + ['high']
        nn = sum(agg[v]['cdef_n'] for v in near)
        fn = sum(agg[v]['cdef_n'] for v in far)
        np_ = sum(agg[v]['cdef_pos'] for v in near)
        fp_ = sum(agg[v]['cdef_pos'] for v in far)
        return nn, fn, np_/nn if nn else 0, fp_/fn if fn else 0
    print(f'{"阈值":<16} {"近类样本":>10} {"远类样本":>10} {"近类下柱>0":>10} {"远类下柱>0":>10} {"方向差异":>8}')
    print('-'*70)
    for t in [2,3,4,5,6]:
        nn, fn, np_, fp_ = calc_upper(t)
        print(f'等2=2~{t} vs 等4≥{t+1}{" (当前)" if t==3 else "":<6} {nn:>10,} {fn:>10,} {np_:>9.1%} {fp_:>9.1%} {np_-fp_:>7.1%}')

    # ========== 输出 3b：下侧ABCD末符：不同DTZA阈值的方向区分度 ==========
    print('\n' + '='*80)
    print('【表3b】下侧ABCD末符：不同DTZA阈值的方向区分度')
    print('说明：DTZA<0时AB≈0，ABCD≈CDEF，所以用cdef_n/cdef_pos近似')
    print('='*80)
    def calc_lower(t):
        # 近类 DTZA=-t~-2, 远类 DTZA≤-(t+1)，均末符ABCD(≈CDEF)
        near_vals = [-2,-3,-4,-5,-6,-7,-8]
        near = [v for v in near_vals if v >= -t]
        far = [v for v in near_vals if v < -t] + ['low']
        nn = sum(agg[v]['cdef_n'] for v in near)
        fn = sum(agg[v]['cdef_n'] for v in far)
        np_ = sum(agg[v]['cdef_pos'] for v in near)
        fp_ = sum(agg[v]['cdef_pos'] for v in far)
        return nn, fn, np_/nn if nn else 0, fp_/fn if fn else 0
    print(f'{"阈值":<16} {"近类样本":>10} {"远类样本":>10} {"近类下柱>0":>10} {"远类下柱>0":>10} {"方向差异":>8}')
    print('-'*70)
    for t in [2,3,4,5,6]:
        nn, fn, np_, fp_ = calc_lower(t)
        print(f'等6=-{t}~-2 vs 等8≤-{t+1}{" (当前)" if t==3 else "":<6} {nn:>10,} {fn:>10,} {np_:>9.1%} {fp_:>9.1%} {np_-fp_:>7.1%}')

    # ========== 输出 3c：末符区分度 vs DTZA区分度 ==========
    print('\n' + '='*80)
    print('【表3c】末符区分度 vs DTZA区分度 — 谁对方向贡献更大？')
    print('='*80)
    print(f'{"ZA":>4} {"AB样本":>8} {"CDEF样本":>10} {"AB下柱>0":>9} {"CDEF下柱>0":>10} {"AB-CD差异":>9} {"全量下柱>0":>9}')
    print('-'*65)
    for v in [1,2,3,4,5,6,7,8]:
        s = agg[v]
        if s['ab_n'] == 0 or s['cdef_n'] == 0: continue
        ab_r = s['ab_pos']/s['ab_n']
        cd_r = s['cdef_pos']/s['cdef_n']
        all_r = s['pos']/s['n']
        print(f'{v:>4} {s["ab_n"]:>8,} {s["cdef_n"]:>10,} {ab_r:>8.1%} {cd_r:>9.1%} {ab_r-cd_r:>8.1%} {all_r:>8.1%}')

    # ========== 输出 4：末符AB（等3）的对比 ==========
    print('\n' + '='*80)
    print('【表4】DTZA=3附近：末符AB(归等3) vs CDEF(归等2/等4) 的对比')
    print('='*80)
    print(f'{"ZA":>4} {"样本":>8} {"AB%":>6} {"CDEF%":>8} {"AB下柱>0":>9} {"CDEF下柱>0":>10} {"AB冲≥3%":>9} {"CDEF冲≥3%":>10}')
    print('-'*75)
    for v in [2,3,4,5]:
        s = agg[v]
        if s['n']==0: continue
        ab_r = s['ab_n']/s['n']; cd_r = s['cdef_n']/s['n']
        ab_pos_r = s['ab_pos']/s['ab_n'] if s['ab_n'] else 0
        cd_pos_r = s['cdef_pos']/s['cdef_n'] if s['cdef_n'] else 0
        # 冲高需要按末符分，这里用整体代替示意
        print(f'{v:>4} {s["n"]:>8,} {ab_r:>5.1%} {cd_r:>7.1%} {ab_pos_r:>8.1%} {cd_pos_r:>9.1%}')

    print(f'\n总样本: {total_n:,}, 总耗时 {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()