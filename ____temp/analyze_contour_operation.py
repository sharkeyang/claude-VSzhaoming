# -*- coding: utf-8 -*-
"""
验证：等高线+操作区域限定 + 前一柱护型对等1/等4/等5的影响
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800
np.random.seed(42)

def classify_8(za, last):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); lc = str(last) if pd.notna(last) else ''
    ab = lc in 'AB'; cdef = lc in 'CDEF'
    abcd = lc in 'ABCD'; ef = lc in 'EF'
    if za > 0:
        if za == 1: return '等1'
        elif za >= 2 and ab: return '等3'
        elif za >= 2 and cdef and za <= 3: return '等2'
        elif za > 3 and cdef: return '等4'
    elif za < 0:
        if za == -1: return '等5'
        elif za >= -3 and za <= -2 and abcd: return '等6'
        elif za <= -2 and ef: return '等7'
        elif za < -3 and abcd: return '等8'
    return 'NA'

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    # 聚合统计
    stats = {}
    def add_stat(key, nhv, nz_val):
        if key not in stats:
            stats[key] = {'n':0, 'nh1':0, 'nh2':0, 'nh3':0, 'nh5':0, 'nh_sum':0.0, 'pos':0, 'neg':0}
        s = stats[key]
        s['n'] += 1
        if not pd.isna(nhv):
            if nhv>1: s['nh1']+=1
            if nhv>2: s['nh2']+=1
            if nhv>3: s['nh3']+=1
            if nhv>5: s['nh5']+=1
            s['nh_sum']+=nhv
        if not pd.isna(nz_val):
            if nz_val>0: s['pos']+=1
            elif nz_val<0: s['neg']+=1

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','柱型','日ZC','DXCD','DXAB','高幅'])
        except: continue
        if len(df) < 100: continue
        za = df['日ZA'].astype(float)
        next_za = za.shift(-1)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        zc = df['日ZC'].astype(float)
        dxab = df['DXAB'].astype(str)
        zc_gt0 = zc > 0
        zc_le0 = zc <= 0

        # 前一柱的DXAB护型
        prev_dxab = dxab.shift(1)

        for idx in df.index:
            zval = za[idx]; nz = next_za[idx]; nhv = nh[idx]; lc = last[idx]
            zc_p = zc_gt0[idx]; zc_n = zc_le0[idx]
            ab_val = dxab[idx]
            prev_ab = prev_dxab[idx] if pd.notna(prev_dxab[idx]) else ''

            c8 = classify_8(zval, lc)
            if c8 == 'NA': continue

            # 提取护型第二个字（甲乙丙丁戊己）
            ab_type = str(ab_val)[1] if len(str(ab_val)) > 1 else ''
            prev_ab_type = str(prev_ab)[1] if len(str(prev_ab)) > 1 else ''
            ab_ok = ab_type in '甲乙己'
            prev_ab_ok = prev_ab_type in '甲乙己'

            # 操作区域：ZC>0 或 (ZC≤0 且 AB∈甲乙己)
            operable = zc_p or (zc_n and ab_ok)

            # === 想法1：等高线 × 操作区域限定 ===
            add_stat(f'1_{c8}_全量', nhv, nz)
            add_stat(f'1_{c8}_可操作', nhv, nz) if operable else None
            add_stat(f'1_{c8}_ZC>0', nhv, nz) if zc_p else None
            add_stat(f'1_{c8}_ZC≤0', nhv, nz) if zc_n else None

            # === 想法2：等1 前一柱护型 ===
            if c8 == '等1' and prev_ab_type in '甲乙丙丁戊己':
                add_stat(f'2_等1_prev_{prev_ab_type}', nhv, nz)
                add_stat(f'2_等1_prev_{prev_ab_type}_可操作', nhv, nz) if operable else None

            # === 想法3：等4/等5/等8 前一柱护型 ===
            if c8 in ['等4','等5','等8'] and prev_ab_type in '甲乙丙丁戊己':
                add_stat(f'3_{c8}_prev_{prev_ab_type}', nhv, nz)
                # 对等4：前一柱护型为甲乙己时的效果
                if prev_ab_ok:
                    add_stat(f'3_{c8}_prev_甲乙己', nhv, nz)
                else:
                    add_stat(f'3_{c8}_prev_丙丁戊', nhv, nz)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'处理完成, 耗时 {time.time()-t0:.0f}s', flush=True)

    def pct(s):
        n2 = s['nh2']/s['n'] if s['n'] else 0
        n3 = s['nh3']/s['n'] if s['n'] else 0
        avg = s['nh_sum']/s['n'] if s['n'] else 0
        dr = s['pos']/s['n'] if s['n'] else 0
        return n2, n3, avg, dr

    # ========== 表1：操作区域限定 ==========
    print('\n' + '='*90)
    print('【表1】等高线 × 操作区域限定 — 下日冲高≥2%')
    print('='*90)
    print(f'{"等高线":<6} {"全量样本":>8} {"全量≥2%":>8} {"可操作样本":>10} {"可操作≥2%":>10} {"ZC>0样本":>8} {"ZC>0≥2%":>8}')
    print('-'*70)
    for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
        k_all = f'1_{c}_全量'
        k_ok = f'1_{c}_可操作'
        k_zc = f'1_{c}_ZC>0'
        if k_all in stats:
            s_all = stats[k_all]
            n2_all, _, _, _ = pct(s_all)
            n2_ok = pct(stats[k_ok])[0] if k_ok in stats else 0
            n_ok_n = stats[k_ok]['n'] if k_ok in stats else 0
            n2_zc = pct(stats[k_zc])[0] if k_zc in stats else 0
            n_zc_n = stats[k_zc]['n'] if k_zc in stats else 0
            print(f'{c:<6} {s_all["n"]:>8,} {n2_all:>7.1%} {n_ok_n:>10,} {n2_ok:>9.1%} {n_zc_n:>8,} {n2_zc:>7.1%}')

    # ========== 表2：等1 前一柱护型 ==========
    print('\n' + '='*90)
    print('【表2】等1(DTZA=1) 按前一柱DXAB护型分组 — 下日冲高')
    print('='*90)
    print(f'{"前一柱护型":<12} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8} {"下柱>0":>8}')
    print('-'*55)
    for ab in '甲乙丙丁戊己':
        k = f'2_等1_prev_{ab}'
        if k in stats:
            s = stats[k]
            n2, n3, avg, dr = pct(s)
            print(f'{ab:<12} {s["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}% {dr:>7.1%}')

    # 等1 前一柱护型 + 操作区域限定
    print(f'\n{"等1 前一柱护型+可操作":<12} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8}')
    print('-'*55)
    for ab in '甲乙丙丁戊己':
        k = f'2_等1_prev_{ab}_可操作'
        if k in stats:
            s = stats[k]
            n2, n3, avg, _ = pct(s)
            print(f'{ab:<12} {s["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}%')

    # ========== 表3：等4/等5/等8 前一柱护型 ==========
    print('\n' + '='*90)
    print('【表3】等4/等5/等8 按前一柱DXAB护型分组 — 下日冲高≥2%')
    print('='*90)
    for c in ['等4','等5','等8']:
        print(f'\n--- {c} 前一柱护型分组 ---')
        print(f'{"前一柱护型":<12} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8} {"下柱>0":>8}')
        print('-'*55)
        for ab in '甲乙丙丁戊己':
            k = f'3_{c}_prev_{ab}'
            if k in stats:
                s = stats[k]
                n2, n3, avg, dr = pct(s)
                print(f'{ab:<12} {s["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}% {dr:>7.1%}')
        # 合并甲乙己 vs 丙丁戊
        k_ok = f'3_{c}_prev_甲乙己'
        k_bad = f'3_{c}_prev_丙丁戊'
        if k_ok in stats:
            s_ok = stats[k_ok]
            n2, n3, avg, dr = pct(s_ok)
            print(f'{"甲乙己(优)":<12} {s_ok["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}% {dr:>7.1%}')
        if k_bad in stats:
            s_bad = stats[k_bad]
            n2, n3, avg, dr = pct(s_bad)
            print(f'{"丙丁戊(弱)":<12} {s_bad["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}% {dr:>7.1%}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()