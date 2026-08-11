# -*- coding: utf-8 -*-
"""
赛马策略 + 增强过滤（操作区域限定 + 前一柱护型）
验证：等4+BSHA5 等策略加上增强过滤后，≥2%是否继续提升
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

    stats = {}
    def add_stat(key, nhv):
        if key not in stats:
            stats[key] = {'n':0, 'nh2':0, 'nh3':0, 'nh_sum':0.0}
        s = stats[key]
        s['n'] += 1
        if not pd.isna(nhv):
            if nhv>2: s['nh2']+=1
            if nhv>3: s['nh3']+=1
            s['nh_sum']+=nhv

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','高幅','日ZC','DXCD','DXAB','柱型'])
        except: continue
        if len(df) < 100: continue
        za = df['日ZA'].astype(float)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        high = df['高幅'].astype(float)
        zc = df['日ZC'].astype(float)
        dxab = df['DXAB'].astype(str)
        dxcd = df['DXCD'].astype(str)
        zhuxing = df['柱型'].astype(str)
        prev_dxab = dxab.shift(1)

        zc_gt0 = zc > 0
        dxcd_up = dxcd == '上'
        zhoumen = zc_gt0 & dxcd_up

        for idx in df.index:
            zval = za[idx]; nhv = nh[idx]; lc = last[idx]; hv = high[idx]
            zc_p = zc_gt0[idx]; zm = zhoumen[idx]
            ab_type = str(dxab[idx])[1] if len(str(dxab[idx]))>1 else ''
            prev_ab = str(prev_dxab[idx])[1] if pd.notna(prev_dxab[idx]) and len(str(prev_dxab[idx]))>1 else ''
            zx = zhuxing[idx]

            c8 = classify_8(zval, lc)
            if c8 == 'NA': continue

            # 操作区域限定
            operable = zc_p or (not zc_p and ab_type in '甲乙己')
            # 前一柱护型好
            prev_good = prev_ab in '甲乙'  # 乙/甲是最优
            # 柱梯
            is_zhuti = '梯' in str(zx)

            # BSHA5近似
            bsha5 = pd.notna(hv) and hv > 5
            bsha3 = pd.notna(hv) and hv > 3

            # 等1 + 前一柱护型过滤
            if c8 in ['等1'] and bsha5:
                add_stat(f'等1_BSHA5', nhv)
                if operable: add_stat(f'等1_BSHA5_可操作', nhv)
                if prev_good: add_stat(f'等1_BSHA5_前甲乙', nhv)
                if operable and prev_good: add_stat(f'等1_BSHA5_可操作_前甲乙', nhv)

            if c8 in ['等1'] and bsha5 and zm:
                add_stat(f'等1_BSHA5_周门', nhv)
                if prev_good: add_stat(f'等1_BSHA5_周门_前甲乙', nhv)

            # 等4 + BSHA5
            if c8 in ['等4'] and bsha5:
                add_stat(f'等4_BSHA5', nhv)
                if operable: add_stat(f'等4_BSHA5_可操作', nhv)
                if prev_good: add_stat(f'等4_BSHA5_前甲乙', nhv)
                if operable and prev_good: add_stat(f'等4_BSHA5_可操作_前甲乙', nhv)

            if c8 in ['等4'] and bsha5 and zm:
                add_stat(f'等4_BSHA5_周门', nhv)
                if prev_good: add_stat(f'等4_BSHA5_周门_前甲乙', nhv)

            # 等4 + 柱梯
            if c8 in ['等4'] and is_zhuti:
                add_stat(f'等4_柱梯', nhv)
                if operable: add_stat(f'等4_柱梯_可操作', nhv)
                if zm: add_stat(f'等4_柱梯_周门', nhv)

            # 等3 + BSHA5
            if c8 in ['等3'] and bsha5:
                add_stat(f'等3_BSHA5', nhv)
                if operable: add_stat(f'等3_BSHA5_可操作', nhv)

            # 等5 + BSHA5
            if c8 in ['等5'] and bsha5:
                add_stat(f'等5_BSHA5', nhv)
                if operable: add_stat(f'等5_BSHA5_可操作', nhv)
                if prev_good: add_stat(f'等5_BSHA5_前甲乙', nhv)

            # 等8 + BSHA5
            if c8 in ['等8'] and bsha5:
                add_stat(f'等8_BSHA5', nhv)
                if operable: add_stat(f'等8_BSHA5_可操作', nhv)
                if prev_good: add_stat(f'等8_BSHA5_前甲乙', nhv)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'处理完成, 耗时 {time.time()-t0:.0f}s', flush=True)

    def show(key, label):
        if key in stats:
            s = stats[key]
            n2 = s['nh2']/s['n']; n3 = s['nh3']/s['n']; avg = s['nh_sum']/s['n']
            print(f'{label:<40} {s["n"]:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>7.2f}%')
        else:
            print(f'{label:<40} {"":>8} {"":>7} {"":>7} {"":>7}')

    # 打印对比表
    print('\n' + '='*85)
    print('赛马策略 + 增强过滤对比 — 下日冲高≥2%')
    print('='*85)
    print(f'{"策略":<40} {"样本":>8} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7}')
    print('-'*85)

    # 等1
    print('\n--- 等1+BSHA5 ---')
    show('等1_BSHA5', '等1+BSHA5')
    show('等1_BSHA5_可操作', '  +操作区域限定')
    show('等1_BSHA5_前甲乙', '  +前一柱甲乙')
    show('等1_BSHA5_可操作_前甲乙', '  +两者都加')
    print()
    show('等1_BSHA5_周门', '等1+BSHA5+周门')
    show('等1_BSHA5_周门_前甲乙', '  +前一柱甲乙')

    # 等4
    print('\n--- 等4+BSHA5 ---')
    show('等4_BSHA5', '等4+BSHA5')
    show('等4_BSHA5_可操作', '  +操作区域限定')
    show('等4_BSHA5_前甲乙', '  +前一柱甲乙')
    show('等4_BSHA5_可操作_前甲乙', '  +两者都加')
    print()
    show('等4_BSHA5_周门', '等4+BSHA5+周门')
    show('等4_BSHA5_周门_前甲乙', '  +前一柱甲乙')

    # 等4+柱梯
    print('\n--- 等4+柱梯 ---')
    show('等4_柱梯', '等4+柱梯')
    show('等4_柱梯_可操作', '  +操作区域限定')
    show('等4_柱梯_周门', '  +周门')

    # 等3
    print('\n--- 等3+BSHA5 ---')
    show('等3_BSHA5', '等3+BSHA5')
    show('等3_BSHA5_可操作', '  +操作区域限定')

    # 下侧
    print('\n--- 等5+BSHA5 ---')
    show('等5_BSHA5', '等5+BSHA5')
    show('等5_BSHA5_可操作', '  +操作区域限定')
    show('等5_BSHA5_前甲乙', '  +前一柱甲乙')

    print('\n--- 等8+BSHA5 ---')
    show('等8_BSHA5', '等8+BSHA5')
    show('等8_BSHA5_可操作', '  +操作区域限定')
    show('等8_BSHA5_前甲乙', '  +前一柱甲乙')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()