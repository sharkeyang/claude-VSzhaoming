# -*- coding: utf-8 -*-
"""
等2 vs 等4 赛马机会深度分析
核心问题：合并CDEF类(等2+等4)是否丢失赛马机会？
重点：等2 vs 等4 在叠加 BSHA5/BSHA3/柱型/周门 后的冲高差异
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

def classify_zhuxing(ct_str):
    if pd.isna(ct_str): return 'NA'
    ct = str(ct_str)
    if '根' in ct: return '柱根'
    elif '枝' in ct: return '柱枝'
    elif '干' in ct: return '柱干'
    elif '冠' in ct: return '柱冠'
    elif '梯' in ct: return '柱梯'
    elif '栅' in ct: return '柱栅'
    elif '蛀' in ct: return '柱蛀'
    elif '暂' in ct: return '柱暂'
    else: return '柱其他'

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    # 聚合：{key: {n, nh1, nh2, nh3, nh5, nh_sum, pos, neg}}
    stats = {}

    def add_stat(key, nhv, nz):
        if key not in stats:
            stats[key] = {'n':0,'nh1':0,'nh2':0,'nh3':0,'nh5':0,'nh_sum':0.0,'pos':0,'neg':0,'zero':0}
        s = stats[key]
        s['n'] += 1
        if not pd.isna(nhv):
            if nhv>1: s['nh1']+=1
            if nhv>2: s['nh2']+=1
            if nhv>3: s['nh3']+=1
            if nhv>5: s['nh5']+=1
            s['nh_sum']+=nhv
        if not pd.isna(nz):
            if nz>0: s['pos']+=1
            elif nz<0: s['neg']+=1
            else: s['zero']+=1

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','柱型','日ZC','DXCD','高幅'])
        except: continue
        if len(df) < 100: continue
        za = df['日ZA'].astype(float)
        next_za = za.shift(-1)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        high = df['高幅'].astype(float)  # 当日高幅，用于BSHA近似
        zhuxing = df['柱型']
        zc_gt0 = df['日ZC'].astype(float) > 0
        dxcd_up = df['DXCD'].astype(str) == '上'
        zhoumen = zc_gt0 & dxcd_up

        for idx in df.index:
            zval = za[idx]; nz = next_za[idx]; nhv = nh[idx]; lc = last[idx]
            zx = zhuxing[idx]; zm = zhoumen[idx]
            hv = high[idx]  # 当日高幅

            c8 = classify_8(zval, lc)
            if c8 not in ['等2','等4']: continue
            zx_cat = classify_zhuxing(zx)

            # 基础（无信号）
            add_stat(f'{c8}_基准', nhv, nz)
            # 周门
            if zm:
                add_stat(f'{c8}_周门', nhv, nz)
            # BSHA5（当日高幅>5近似）
            if pd.notna(hv) and hv > 5:
                add_stat(f'{c8}_BSHA5', nhv, nz)
                if zm:
                    add_stat(f'{c8}_BSHA5_周门', nhv, nz)
            # BSHA3
            if pd.notna(hv) and hv > 3:
                add_stat(f'{c8}_BSHA3', nhv, nz)
                if zm:
                    add_stat(f'{c8}_BSHA3_周门', nhv, nz)
            # 柱梯
            if zx_cat == '柱梯':
                add_stat(f'{c8}_柱梯', nhv, nz)
                if zm:
                    add_stat(f'{c8}_柱梯_周门', nhv, nz)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'处理完成, 耗时 {time.time()-t0:.0f}s', flush=True)

    # 输出对比
    def show(label, s2, s4dict):
        if s2['n'] < 50 or s4dict['n'] < 50: return
        print(f'{label:<28} 等2:{s2["n"]:>7,} 等4:{s4dict["n"]:>8,} | 等2≥2%:{s2["nh2"]/s2["n"]:>5.1%} 等4≥2%:{s4dict["nh2"]/s4dict["n"]:>5.1%} | 等2≥3%:{s2["nh3"]/s2["n"]:>5.1%} 等4≥3%:{s4dict["nh3"]/s4dict["n"]:>5.1%} | 等2均:{s2["nh_sum"]/s2["n"]:>5.2f} 等4均:{s4dict["nh_sum"]/s4dict["n"]:>5.2f} | 方向差:{s2["pos"]/s2["n"]-s4dict["pos"]/s4dict["n"]:>5.1%}')

    print('\n' + '='*100)
    print('等2 vs 等4 赛马信号叠加对比')
    print('='*100)
    print(f'{"信号":<28} {"样本(等2/等4)":>20} {"≥2%":>20} {"≥3%":>20} {"均冲高":>16} {"方向差":>8}')
    print('-'*100)

    combos = ['基准','周门','BSHA5','BSHA5_周门','BSHA3','BSHA3_周门','柱梯','柱梯_周门']
    for cmb in combos:
        k2 = f'等2_{cmb}'
        k4 = f'等4_{cmb}'
        if k2 in stats and k4 in stats:
            s2 = stats[k2]; s4 = stats[k4]
            if s2['n']<50 or s4['n']<50: continue
            d2 = s2['nh2']/s2['n'] - s4['nh2']/s4['n']
            d3 = s2['nh3']/s2['n'] - s4['nh3']/s4['n']
            print(f'{cmb:<28} {s2["n"]:>8,}/{s4["n"]:>10,} | ≥2%差:{d2:+.1%} | ≥3%差:{d3:+.1%} | 等2均:{s2["nh_sum"]/s2["n"]:.2f} 等4均:{s4["nh_sum"]/s4["n"]:.2f} | {s2["pos"]/s2["n"]-s4["pos"]/s4["n"]:+.1%}')

    # 合并CDEF vs 分开
    print('\n' + '='*100)
    print('合并CDEF类(等2+等4) vs 分开(等2/等4) — 赛马效果')
    print('='*100)
    for cmb in combos:
        k2 = f'等2_{cmb}'; k4 = f'等4_{cmb}'
        if k2 not in stats or k4 not in stats: continue
        s2 = stats[k2]; s4 = stats[k4]
        mn = s2['n']+s4['n']
        if mn < 50: continue
        m = {'n':mn,
             'nh1':s2['nh1']+s4['nh1'], 'nh2':s2['nh2']+s4['nh2'],
             'nh3':s2['nh3']+s4['nh3'], 'nh5':s2['nh5']+s4['nh5'],
             'nh_sum':s2['nh_sum']+s4['nh_sum'], 'pos':s2['pos']+s4['pos']}
        # 合并后 vs 等3(AB) 对比
        k3 = f'等3_{cmb}'
        if k3 in stats:
            s3v = stats[k3]
            print(f'{cmb:<20} 合并CDEF:{m["n"]:>7,} ≥2%:{m["nh2"]/m["n"]:>5.1%} ≥3%:{m["nh3"]/m["n"]:>5.1%} | 等3(AB):{s3v["n"]:>7,} ≥2%:{s3v["nh2"]/s3v["n"]:>5.1%} ≥3%:{s3v["nh3"]/s3v["n"]:>5.1%} | 末符方向差:{s3v["pos"]/s3v["n"]-m["pos"]/m["n"]:+.1%}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()