# -*- coding: utf-8 -*-
"""
等高线分析 v5 — 修正镜面映射
上侧: 上1(=1,任意) 上2(=2~4,CDEF) 上3(≥2,AB) 上4(>4,CDEF)
下侧(镜面 A↔F B↔E C↔D): 下1(=-1,任意) 下2(=-4~-2,ABCD) 下3(≤-2,EF) 下4(<-4,ABCD)
"""

import pandas as pd, numpy as np, os, glob, time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')
MAX_FILES = 500; RANDOM_SEED = 42
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_TOP = '顶型'
COL_HR = '高幅'; COL_PR = '涨幅'; COL_NEXT = '次日高幅'
COL_DXEF = 'DXEF'; COL_DXCD = 'DXCD'

def classify(za, mid):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); mid = str(mid) if pd.notna(mid) else ''
    has_abc = any(c in mid for c in ['A','B','C'])
    has_abcd = any(c in mid for c in ['A','B','C','D'])
    has_ef = any(c in mid for c in ['E','F'])
    has_cdef = any(c in mid for c in ['C','D','E','F'])
    has_ab = any(c in mid for c in ['A','B'])

    if za > 0:
        if za == 1: return '上1'
        elif za > 4 and has_cdef: return '上4'
        elif za >= 2 and has_cdef: return '上2'
        elif za >= 2 and has_ab: return '上3'
        elif za >= 2: return '上0'  # 日中符既非AB也非CDEF的罕见情况
        else: return '上0'
    elif za < 0:
        if za == -1: return '下1'
        elif za >= -4 and has_abcd: return '下2'  # -4~-2, ABCD
        elif za <= -2 and has_ef: return '下3'     # ≤-2, EF
        elif za < -4 and has_abcd: return '下4'    # <-4, ABCD
        elif za <= -2: return '下0'  # 不匹配任何分类
        else: return '下0'
    else:
        return '零轴'

def main():
    np.random.seed(RANDOM_SEED); t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    files = list(np.random.choice(files, min(MAX_FILES, len(files)), replace=False))
    print(f"抽样 {len(files)} 个文件")

    frames = []
    for i, f in enumerate(files):
        try:
            df = pd.read_csv(f, encoding='gbk')
            if COL_ZA not in df.columns or len(df) < 5: continue
            df['等高线'] = df.apply(lambda r: classify(r[COL_ZA], r[COL_MID]), axis=1)
            for d in [3,5,7,10,15,20]:
                df[f'fwd_{d}d'] = df[COL_PR].shift(-d).rolling(d).sum().shift(-(d-1))
            frames.append(df)
        except: pass
        if (i+1)%100==0: print(f"  已处理 {i+1}/{len(files)} ({time.time()-t0:.0f}s)")

    data = pd.concat(frames, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行, {time.time()-t0:.0f}s")

    cats = ['上1','上2','上3','上4','下1','下2','下3','下4','零轴','上0','下0']

    # 1. 分布
    print("\n" + "="*80)
    print("一、等高线分类分布（修正镜面映射）")
    print("="*80)
    for c in cats:
        n = data['等高线'].value_counts().get(c, 0)
        if n > 0: print(f"  {c}: {n:>10,} ({n/len(data)*100:>5.1f}%)")

    # 2. 下日DSHR
    print("\n"+"="*80)
    print("二、等高线 × 下日冲高概率")
    print("="*80)
    print(f"{'分类':>6} | {'样本':>8} | {'下日冲高≥1%':>10} | {'下日冲高≥3%':>10} | {'下日冲高≥5%':>10} | {'平均冲高':>8}")
    print("-"*65)
    main_cats = ['上1','上2','上3','上4','下1','下2','下3','下4']
    for c in main_cats:
        sub = data[data['等高线']==c]
        if len(sub)<200: continue
        nh = sub[COL_NEXT]
        print(f"{c:>6} | {len(sub):>8,} | {(nh>1).mean():>9.1%} | {(nh>3).mean():>9.1%} | {(nh>5).mean():>9.1%} | {nh.mean():>7.2f}%")

    # 3. 下2/下3/下4细节
    print("\n"+"="*80)
    print("三、下2/下3/下4 日中符分布细节")
    print("="*80)
    for c in ['下2','下3','下4']:
        sub = data[data['等高线']==c]
        if len(sub)<200: continue
        # 日中符最后一位的分布
        last_chars = sub[COL_MID].str[-1].value_counts()
        print(f"\n  {c} (n={len(sub):,}): 日中符末位分布")
        for ch, cnt in last_chars.items():
            print(f"    {ch}: {cnt:>8,} ({cnt/len(sub)*100:>5.1f}%)")

    # 4. 与上侧对比
    print("\n"+"="*80)
    print("四、上侧 vs 下侧 镜面对比")
    print("="*80)
    mirror_pairs = [('上2','下2'),('上3','下3'),('上4','下4')]
    print(f"{'上侧':>6} | {'下日冲高≥3%':>12} | {'下日冲高≥5%':>12} | {'→ZE>0':>8} | {'下侧':>6} | {'下日冲高≥3%':>12} | {'下日冲高≥5%':>12} | {'→ZE>0':>8}")
    print("-"*90)
    for up, down in mirror_pairs:
        u = data[data['等高线']==up]
        d = data[data['等高线']==down]
        if len(u)<200 or len(d)<200: continue
        print(f"{up:>6} | {(u[COL_NEXT]>3).mean():>11.1%} | {(u[COL_NEXT]>5).mean():>11.1%} | {(u[COL_ZE]>0).mean():>7.1%} | {down:>6} | {(d[COL_NEXT]>3).mean():>11.1%} | {(d[COL_NEXT]>5).mean():>11.1%} | {(d[COL_ZE]>0).mean():>7.1%}")

    # 5. 下3 vs 上3 持有期
    print("\n"+"="*80)
    print("五、上3 vs 下3 持有期对比")
    print("="*80)
    for c in ['上3','下3']:
        sub = data[data['等高线']==c]
        if len(sub)<5000: continue
        if len(sub)>100000: sub = sub.sample(100000, random_state=RANDOM_SEED)
        print(f"\n  {c} (n={len(sub):,}):")
        for d in [3,5,7,10,15]:
            vals = sub[f'fwd_{d}d'].dropna()
            if len(vals)<100: continue
            print(f"    持有{d}天: 中位={np.median(vals):.2f}%  ≥5%={(vals>5).mean():.1%}  ≥10%={(vals>10).mean():.1%}")

    # 6. 下1 × DXCD 交叉
    print("\n"+"="*80)
    print("六、下1 × DXCD 交叉（类比上1）")
    print("="*80)
    for c in ['下1','上1']:
        sub = data[data['等高线']==c]
        if len(sub)<500: continue
        print(f"\n  {c}:")
        for v in ['上','中','下','忐','忠','忑']:
            grp = sub[sub[COL_DXCD].str.contains(v, na=False)]
            if len(grp)<50: continue
            nh = grp[COL_NEXT]
            print(f"    DXCD={v}: n={len(grp):,}  下日冲高≥3%={(nh>3).mean():.1%}  下日冲高≥5%={(nh>5).mean():.1%}  →ZE>0={(grp[COL_ZE]>0).mean():.1%}")

    print(f"\n完成！{time.time()-t0:.0f}s")

if __name__=='__main__': main()