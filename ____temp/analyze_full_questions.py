# -*- coding: utf-8 -*-
"""
全量分析：触顶条件 + BSHA提前介入 + 替换策略精确样本量
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800
np.random.seed(42)

def classify_8(za, last):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); lc = str(last) if pd.notna(last) else ''
    ab = lc in 'AB'; cdef = lc in 'CDEF'; abcd = lc in 'ABCD'; ef = lc in 'EF'
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
            if nhv > 2: s['nh2'] += 1
            if nhv > 3: s['nh3'] += 1
            s['nh_sum'] += nhv

    bsha5_prev = []

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','BSHA','上符串','BT连阳','日ZC','DXCD','DXAB','BT鼎'])
        except: continue
        if len(df) < 100: continue
        za = df['日ZA'].astype(float)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        bsha = df['BSHA'].astype(float)
        sf = df['上符串'].astype(str)
        zc = df['日ZC'].astype(float)
        dxab = df['DXAB'].astype(str)
        dxcd = df['DXCD'].astype(str)
        ly = df['BT连阳'].astype(float)
        btd = df['BT鼎'].astype(float)
        prev_bsha = bsha.shift(1)

        for idx in df.index:
            zval = za[idx]; nhv = nh[idx]; lc = last[idx]; bv = bsha[idx]
            pv = prev_bsha[idx]; sf_str = str(sf[idx])
            zc_p = (zc[idx] > 0); dxcd_up = (dxcd[idx] == '上')
            ab_type = str(dxab[idx])[1] if len(str(dxab[idx]))>1 else ''
            zhoumen = zc_p and dxcd_up
            is_chu = 'v' in sf_str

            c8 = classify_8(zval, lc)
            if c8 == 'NA': continue

            bsha5 = pd.notna(bv) and bv > 5
            bsha4 = pd.notna(bv) and bv > 4
            bsha3 = pd.notna(bv) and bv > 3
            bsha2 = pd.notna(bv) and bv > 2

            # 替换策略精确样本
            if c8 == '等8' and bsha5 and zhoumen:
                add_stat('等8_BSHA5_周门', nhv)
            if c8 == '等6' and bsha5 and zhoumen:
                add_stat('等6_BSHA5_周门', nhv)
            if c8 == '等5' and bsha4 and zhoumen:
                add_stat('等5_BSHA4_周门', nhv)

            # 触顶
            if c8 in ['等1','等4','等3','等8']:
                add_stat(f'{c8}_触顶', nhv) if is_chu else add_stat(f'{c8}_不触顶', nhv)
                if bsha5:
                    add_stat(f'{c8}_触顶_BSHA5', nhv) if is_chu else add_stat(f'{c8}_不触顶_BSHA5', nhv)
                if zhoumen:
                    add_stat(f'{c8}_触顶_周门', nhv) if is_chu else add_stat(f'{c8}_不触顶_周门', nhv)

            # BSHA提前介入: BSHA5前一天的BSHA
            if bsha5 and pd.notna(pv):
                bsha5_prev.append(pv)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'收集完成, 耗时 {time.time()-t0:.0f}s', flush=True)

    # 输出
    print('\n' + '='*90)
    print('【问题1】替换策略精确样本量')
    print('='*90)
    for k in ['等8_BSHA5_周门','等6_BSHA5_周门','等5_BSHA4_周门']:
        if k in stats:
            s = stats[k]
            n2 = s['nh2']/s['n']*100; n3 = s['nh3']/s['n']*100
            avg = s['nh_sum']/s['n']
            print(f'{k}: 样本{s["n"]:,}, 全量~{s["n"]*9:,}')
            print(f'  >=2%={n2:.1f}%, >=3%={n3:.1f}%, 均冲高={avg:.2f}%')

    print('\n' + '='*90)
    print('【问题2】触顶条件(v in 上符串)')
    print('='*90)
    print(f'{"等高线":<6} {"触顶>=2%":>9} {"不触顶>=2%":>11} {"差异":>6} {"触顶样本":>9}')
    for c in ['等1','等4','等3','等8']:
        k1 = f'{c}_触顶'; k2 = f'{c}_不触顶'
        if k1 in stats and k2 in stats:
            n21 = stats[k1]['nh2']/stats[k1]['n']*100
            n22 = stats[k2]['nh2']/stats[k2]['n']*100
            print(f'{c:<6} {n21:>8.1f}% {n22:>10.1f}% {n21-n22:>+5.1f}pp {stats[k1]["n"]:>9,}')

    print(f'\n--- 触顶+BSHA5 ---')
    print(f'{"等高线":<6} {"触顶+BSHA5>=2%":>14} {"不触顶+BSHA5>=2%":>16} {"差异":>6} {"触顶样本":>9}')
    for c in ['等1','等4','等3','等8']:
        k1 = f'{c}_触顶_BSHA5'; k2 = f'{c}_不触顶_BSHA5'
        if k1 in stats and k2 in stats:
            n21 = stats[k1]['nh2']/stats[k1]['n']*100
            n22 = stats[k2]['nh2']/stats[k2]['n']*100
            print(f'{c:<6} {n21:>13.1f}% {n22:>15.1f}% {n21-n22:>+5.1f}pp {stats[k1]["n"]:>9,}')

    print('\n' + '='*90)
    print('【问题3】BSHA提前介入')
    print('='*90)
    arr = np.array(bsha5_prev)
    print(f'BSHA5总样本: {len(arr):,}')
    print(f'前一天BSHA均值: {arr.mean():.2f}%')
    print(f'前一天BSHA中位数: {np.median(arr):.2f}%')
    print(f'前一天BSHA分布:')
    print(f'  >=5(连续两天): {(arr>=5).mean():.1%}')
    print(f'  4~5: {((arr>=4)&(arr<5)).mean():.1%}')
    print(f'  3~4: {((arr>=3)&(arr<4)).mean():.1%}')
    print(f'  2~3: {((arr>=2)&(arr<3)).mean():.1%}')
    print(f'  <2(无信号): {(arr<2).mean():.1%}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()