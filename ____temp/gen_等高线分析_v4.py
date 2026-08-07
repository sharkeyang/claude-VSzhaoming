# -*- coding: utf-8 -*-
"""
等高线分析 v4 — 简化DSHR阈值：0, 1, 3, 5
"""

import pandas as pd
import numpy as np
import os, glob, time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')
MAX_FILES = 500
RANDOM_SEED = 42

COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID_SYM = '中符串'; COL_TOP = '顶型'
COL_HR = '高幅'; COL_PR = '涨幅'; COL_NEXT_HR = '次日高幅'
COL_DXEF = 'DXEF'; COL_DXCD = 'DXCD'

def classify_za(za, mid_sym):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); mid_sym = str(mid_sym) if pd.notna(mid_sym) else ''
    has_cdef = any(c in mid_sym for c in ['C','D','E','F'])
    if za > 0:
        if za == 1: return '上1'
        elif za <= 4 and has_cdef: return '上2'
        elif za > 4 and has_cdef: return '上4'
        elif za >= 2: return '上3'
        else: return '上0'
    elif za < 0:
        za_abs = abs(za)
        if za == -1: return '下1'
        elif za_abs <= 4 and has_cdef: return '下2'
        elif za_abs > 4 and has_cdef: return '下4'
        elif za_abs >= 2: return '下3'
        else: return '下0'
    else: return '零轴'

def main():
    np.random.seed(RANDOM_SEED); t0 = time.time()
    pattern = os.path.join(DATA_DIR, '谕组日_*.csv')
    all_files = sorted(glob.glob(pattern))
    files = list(np.random.choice(all_files, min(MAX_FILES, len(all_files)), replace=False))
    print(f"抽样 {len(files)}/{len(all_files)} 个文件")

    frames = []
    for i, fpath in enumerate(files):
        try:
            df = pd.read_csv(fpath, encoding='gbk')
            if COL_ZA not in df.columns or len(df) < 5: continue
            df['等高线'] = df.apply(lambda r: classify_za(r[COL_ZA], r[COL_MID_SYM]), axis=1)
            for d in [3,5,7,10,15,20]:
                df[f'fwd_{d}d'] = df[COL_PR].shift(-d).rolling(d).sum().shift(-(d-1))
            frames.append(df)
        except: pass
        if (i+1)%100==0: print(f"  已处理 {i+1}/{len(files)} ({time.time()-t0:.0f}s)")

    data = pd.concat(frames, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行, {time.time()-t0:.0f}s")
    cats = ['上1','上2','上3','上4','下1','下2','下4']

    # 1. 分布
    print("\n" + "="*80)
    print("一、等高线分类分布")
    print("="*80)
    for c in cats: print(f"  {c}: {data['等高线'].value_counts().get(c,0):>10,}")

    # 2. 下日DSHR 简化阈值
    print("\n" + "="*80)
    print("二、等高线 × 下日盘中冲高概率（DSHR）")
    print("="*80)
    print(f"{'分类':>6} | {'样本':>8} | {'冲高≥0%':>8} | {'冲高≥1%':>8} | {'冲高≥3%':>8} | {'冲高≥5%':>8} | {'平均冲高':>8}")
    print("-"*65)
    for c in cats:
        sub = data[data['等高线']==c]
        if len(sub)<200: continue
        nh = sub[COL_NEXT_HR]
        print(f"{c:>6} | {len(sub):>8,} | {(nh>0).mean():>7.1%} | {(nh>1).mean():>7.1%} | {(nh>3).mean():>7.1%} | {(nh>5).mean():>7.1%} | {nh.mean():>7.2f}%")

    # 3. 等高线 × 日ZE 交叉
    print("\n"+"="*80)
    print("三、等高线 × 日ZE 交叉（ZE>0时DSHR更高）")
    print("="*80)
    print(f"{'分类':>6} | {'ZE>0样本':>8} | {'冲高≥3%':>8} | {'冲高≥5%':>8} | {'平均冲高':>8} | {'ZE≤0样本':>8} | {'冲高≥3%':>8} | {'冲高≥5%':>8} | {'平均冲高':>8}")
    print("-"*95)
    for c in cats:
        sub = data[data['等高线']==c]
        if len(sub)<200: continue
        ze_p = sub[sub[COL_ZE]>0]; ze_n = sub[sub[COL_ZE]<=0]
        print(f"{c:>6} | {len(ze_p):>8,} | {(ze_p[COL_NEXT_HR]>3).mean():>7.1%} | {(ze_p[COL_NEXT_HR]>5).mean():>7.1%} | {ze_p[COL_NEXT_HR].mean():>7.2f}% | {len(ze_n):>8,} | {(ze_n[COL_NEXT_HR]>3).mean():>7.1%} | {(ze_n[COL_NEXT_HR]>5).mean():>7.1%} | {ze_n[COL_NEXT_HR].mean():>7.2f}%")

    # 4. 等高线 × DXCD 交叉
    print("\n"+"="*80)
    print("四、等高线 × DXCD 交叉（上1/上2中DXCD=上时最强）")
    print("="*80)
    for c in ['上1','上2','上3','上4']:
        sub = data[data['等高线']==c]
        if len(sub)<500: continue
        print(f"\n  {c}:")
        for v in ['上','中','下','忐','忠','忑']:
            grp = sub[sub[COL_DXCD].str.contains(v, na=False)]
            if len(grp)<50: continue
            nh = grp[COL_NEXT_HR]
            print(f"    DXCD={v}: n={len(grp):,}  冲高≥3%={(nh>3).mean():.1%}  冲高≥5%={(nh>5).mean():.1%}  平均={nh.mean():.2f}%")

    # 5. 持有期
    print("\n"+"="*80)
    print("五、等高线 × 持有期DSHR（涨幅累加）")
    print("="*80)
    for c in cats:
        sub = data[data['等高线']==c]
        if len(sub)<5000: continue
        if len(sub)>100000: sub = sub.sample(100000, random_state=RANDOM_SEED)
        print(f"\n  {c} (n={len(sub):,}):")
        for d in [3,5,7,10,15,20]:
            vals = sub[f'fwd_{d}d'].dropna()
            if len(vals)<100: continue
            print(f"    持有{d}天: 中位={np.median(vals):.2f}%  平均={np.mean(vals):.2f}%  ≥5%={(vals>5).mean():.1%}  ≥10%={(vals>10).mean():.1%}")

    print(f"\n完成！{time.time()-t0:.0f}s")

if __name__=='__main__': main()