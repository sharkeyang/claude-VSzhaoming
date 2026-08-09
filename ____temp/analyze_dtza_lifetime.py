# -*- coding: utf-8 -*-
"""
DTZA寿命分析 + 末符2类vs8类 + 柱型交叉
1. DTZA正数/负数持续天数分布
2. 末符2类(AB vs CDEF) vs 等高线8类的方向区分度对比
3. DTZA区域 × 柱型 交叉
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800
np.random.seed(42)

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    # ========== 1. DTZA寿命统计 ==========
    # 每个文件（每只股票）独立统计DTZA正数/负数连续运行长度
    pos_runs = []  # 正数持续天数列表
    neg_runs = []  # 负数持续天数列表
    # 柱型 × DTZA区域 交叉表
    # 柱型列: 根,枝,干,冠,其他
    # DTZA区域: 负稳态(≤-4), 负贯穿(-3~-1), 零轴(0), 正贯穿(1~3), 正稳态(≥4)
    col_types = ['根','枝','干','冠','梯','栅','蛀','暂','其他']
    za_zones = ['负稳态','负贯穿','零轴','正贯穿','正稳态']
    cross = {z:{c:0 for c in col_types} for z in za_zones}
    cross_n = {z:{c:0 for c in col_types} for z in za_zones}
    total_n = 0

    # 末符2类 vs 8类 方向统计
    # 2类: AB, CDEF
    # 8类: 等1~等8
    mo2 = {'AB':{'n':0,'pos':0}, 'CDEF':{'n':0,'pos':0}}
    mo8 = {f'等{i}':{'n':0,'pos':0} for i in range(1,9)}

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','柱型'])
        except: continue
        if len(df) < 100: continue
        total_n += len(df)
        za = df['日ZA'].astype(float)
        za_int = za.round().astype(int)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        next_za = za.shift(-1)

        # === 末符2类方向 ===
        is_ab = last.isin(['A','B'])
        is_cdef = last.isin(['C','D','E','F'])
        # AB末符：DTZA≥2（等3范围）
        abm = is_ab & (za_int >= 2)
        nz_ab = next_za[abm].dropna()
        mo2['AB']['n'] += len(nz_ab)
        mo2['AB']['pos'] += int((nz_ab>0).sum())
        # CDEF末符：DTZA≥2（等2+等4范围）
        cdm = is_cdef & (za_int >= 2)
        nz_cd = next_za[cdm].dropna()
        mo2['CDEF']['n'] += len(nz_cd)
        mo2['CDEF']['pos'] += int((nz_cd>0).sum())

        # === 等高线8类方向 ===
        def classify(za_val, last_char):
            if pd.isna(za_val) or za_val == '': return None
            za_val = float(za_val); lc = str(last_char) if pd.notna(last_char) else ''
            ab = lc in 'AB'; cdef = lc in 'CDEF'
            abcd = lc in 'ABCD'; ef = lc in 'EF'
            if za_val > 0:
                if za_val == 1: return '等1'
                elif za_val >= 2 and ab: return '等3'
                elif za_val >= 2 and cdef and za_val <= 3: return '等2'
                elif za_val > 3 and cdef: return '等4'
            elif za_val < 0:
                if za_val == -1: return '等5'
                elif za_val >= -3 and za_val <= -2 and abcd: return '等6'
                elif za_val <= -2 and ef: return '等7'
                elif za_val < -3 and abcd: return '等8'
            return None
        for idx in df.index:
            cls = classify(za_int[idx], last[idx])
            if cls is None: continue
            nz = next_za[idx]
            if pd.isna(nz): continue
            mo8[cls]['n'] += 1
            if nz > 0: mo8[cls]['pos'] += 1

        # === DTZA寿命分析：找正数/负数连续段 ===
        # 用sign表示方向：1=正, -1=负, 0=零
        za_sign = np.sign(za_int.values)
        # 找正数连续段
        j = 0
        while j < len(za_sign):
            if za_sign[j] == 1:
                run_len = 0
                while j < len(za_sign) and za_sign[j] == 1:
                    run_len += 1
                    j += 1
                if run_len >= 1:
                    pos_runs.append(run_len)
            elif za_sign[j] == -1:
                run_len = 0
                while j < len(za_sign) and za_sign[j] == -1:
                    run_len += 1
                    j += 1
                if run_len >= 1:
                    neg_runs.append(run_len)
            else:
                j += 1

        # === 柱型 × DTZA区域 交叉 ===
        # 柱型格式如 .44枝贯单待A，类别在字符串中（根/枝/干/冠/梯/栅/蛀等）
        col_type = df['柱型'].astype(str)
        za_z = za_int.values
        for idx in df.index:
            zval = za_z[idx]
            if zval <= -4: zone = '负稳态'
            elif zval <= -1: zone = '负贯穿'
            elif zval == 0: zone = '零轴'
            elif zval <= 3: zone = '正贯穿'
            else: zone = '正稳态'

            ct_str = col_type[idx]
            if '根' in ct_str: ct_label = '根'
            elif '枝' in ct_str: ct_label = '枝'
            elif '干' in ct_str: ct_label = '干'
            elif '冠' in ct_str: ct_label = '冠'
            elif '梯' in ct_str: ct_label = '梯'
            elif '栅' in ct_str: ct_label = '栅'
            elif '蛀' in ct_str: ct_label = '蛀'
            elif '暂' in ct_str: ct_label = '暂'
            else: ct_label = '其他'

            try:
                nhv = nh[idx]
            except: nhv = 0
            if not pd.isna(nhv):
                cross[zone][ct_label] += 1
                if nhv > 3:
                    cross_n[zone][ct_label] += 1

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'处理完成 {len(sampled)} 文件, {total_n:,} 行, 耗时 {time.time()-t0:.0f}s', flush=True)

    # ========== 输出1：DTZA寿命分布 ==========
    print('\n' + '='*80)
    print('【表1】DTZA正数运行长度分布（JZ在JA之上持续天数）')
    print('='*80)
    pos_arr = np.array(pos_runs)
    print(f'正数运行次数: {len(pos_arr):,}')
    print(f'均值: {pos_arr.mean():.2f} 天, 中位数: {np.median(pos_arr):.1f} 天')
    print(f'标准差: {pos_arr.std():.2f}, 最大值: {pos_arr.max():.0f}')
    # 分布
    max_show = min(30, int(pos_arr.max()))
    hist, edges = np.histogram(pos_arr, bins=np.arange(0.5, max_show+1.5, 1))
    print(f'\n{"天数":>4} {"次数":>8} {"占比":>8} {"累计":>8}')
    print('-'*35)
    cum = 0
    for j in range(min(max_show, len(hist))):
        cum += hist[j]
        print(f'{j+1:>4} {hist[j]:>8,} {hist[j]/len(pos_arr):>7.1%} {cum/len(pos_arr):>7.1%}')
    if len(hist) > max_show:
        rest = hist[max_show:].sum()
        print(f'>{max_show} {rest:>8,} {rest/len(pos_arr):>7.1%}')

    print('\n' + '='*80)
    print('【表2】DTZA负数运行长度分布（JZ在JA之下持续天数）')
    print('='*80)
    neg_arr = np.array(neg_runs)
    print(f'负数运行次数: {len(neg_arr):,}')
    print(f'均值: {neg_arr.mean():.2f} 天, 中位数: {np.median(neg_arr):.1f} 天')
    print(f'标准差: {neg_arr.std():.2f}, 最大值: {neg_arr.max():.0f}')
    max_show = min(30, int(neg_arr.max()))
    hist, edges = np.histogram(neg_arr, bins=np.arange(0.5, max_show+1.5, 1))
    print(f'\n{"天数":>4} {"次数":>8} {"占比":>8} {"累计":>8}')
    print('-'*35)
    cum = 0
    for j in range(min(max_show, len(hist))):
        cum += hist[j]
        print(f'{j+1:>4} {hist[j]:>8,} {hist[j]/len(neg_arr):>7.1%} {cum/len(neg_arr):>7.1%}')
    if len(hist) > max_show:
        rest = hist[max_show:].sum()
        print(f'>{max_show} {rest:>8,} {rest/len(neg_arr):>7.1%}')

    # 关键：DTZA≥4的概率 = 运行长度≥4的概率
    print(f'\n关键阈值概率：')
    print(f'  DTZA≥2（运行≥2天）: {(pos_arr>=2).mean():.1%}')
    print(f'  DTZA≥3（运行≥3天）: {(pos_arr>=3).mean():.1%}')
    print(f'  DTZA≥4（运行≥4天）: {(pos_arr>=4).mean():.1%}')
    print(f'  DTZA≥5（运行≥5天）: {(pos_arr>=5).mean():.1%}')
    print(f'  DTZA≥7（运行≥7天）: {(pos_arr>=7).mean():.1%}')
    print(f'  DTZA≥10（运行≥10天）: {(pos_arr>=10).mean():.1%}')

    # ========== 输出2：末符2类 vs 8类 ==========
    print('\n' + '='*80)
    print('【表3】末符2类(AB vs CDEF) vs 等高线8类的方向区分度')
    print('='*80)
    print(f'\n--- 末符2类 ---')
    print(f'{"类别":<10} {"样本":>8} {"下柱>0":>8}')
    print('-'*30)
    for k in ['AB','CDEF']:
        s = mo2[k]
        print(f'{k:<10} {s["n"]:>8,} {s["pos"]/s["n"]:>7.1%}')
    print(f'方向差异: {mo2["AB"]["pos"]/mo2["AB"]["n"] - mo2["CDEF"]["pos"]/mo2["CDEF"]["n"]:.1%}')

    print(f'\n--- 等高线8类 ---')
    print(f'{"类别":<10} {"样本":>8} {"下柱>0":>8}')
    print('-'*30)
    for k in [f'等{i}' for i in range(1,9)]:
        s = mo8[k]
        if s['n'] == 0: continue
        print(f'{k:<10} {s["n"]:>8,} {s["pos"]/s["n"]:>7.1%}')

    # 8类中上侧合并AB vs CDEF
    print(f'\n--- 8类中上侧合并 ---')
    ab_8 = sum(mo8[f'等{i}']['n'] for i in [1,3])  # 等1和等3是AB末符主导
    ab_pos = sum(mo8[f'等{i}']['pos'] for i in [1,3])
    cd_8 = sum(mo8[f'等{i}']['n'] for i in [2,4])
    cd_pos = sum(mo8[f'等{i}']['pos'] for i in [2,4])
    print(f'等1+等3(AB主导): {ab_8:>8,}, 下柱>0: {ab_pos/ab_8:.1%}')
    print(f'等2+等4(CDEF主导): {cd_8:>8,}, 下柱>0: {cd_pos/cd_8:.1%}')
    print(f'方向差异: {ab_pos/ab_8 - cd_pos/cd_8:.1%}')

    # ========== 输出3：柱型 × DTZA区域 交叉 ==========
    print('\n' + '='*80)
    print('【表4】柱型 × DTZA区域 交叉表（样本量）')
    print('='*80)
    print(f'{"DTZA区域":<12} {"根":>8} {"枝":>8} {"干":>8} {"冠":>8} {"其他":>8} {"合计":>8}')
    print('-'*60)
    for z in za_zones:
        row = cross[z]
        tot = sum(row.values())
        print(f'{z:<12} {row["根"]:>8,} {row["枝"]:>8,} {row["干"]:>8,} {row["冠"]:>8,} {row["其他"]:>8,} {tot:>8,}')

    print(f'\n【表5】柱型 × DTZA区域 交叉表（冲≥3%概率）')
    print('='*80)
    print(f'{"DTZA区域":<12} {"根":>8} {"枝":>8} {"干":>8} {"冠":>8} {"其他":>8} {"合计":>8}')
    print('-'*60)
    for z in za_zones:
        row_tot = cross[z]
        row_hit = cross_n[z]
        print(f'{z:<12} ', end='')
        for c in col_types:
            if row_tot[c] == 0:
                print(f'{"-":>8} ', end='')
            else:
                print(f'{row_hit[c]/row_tot[c]:>7.1%} ', end='')
        tot = sum(row_tot.values())
        hit = sum(row_hit.values())
        print(f'{hit/tot:>7.1%} ' if tot else ' -')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()