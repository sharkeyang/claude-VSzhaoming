# -*- coding: utf-8 -*-
"""
日冲22态 vs 日层等高线(等1-8) 同数据对比
- 简化版：100文件，只做关键维度对比
- 不逐行计算日冲22态（太慢），改为直接分析等高线内部子维度
"""
import sys, time, os, glob, warnings
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

DATA_DIR = os.path.join('昭明算展', '谕组日')
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_NEXT = '次日高幅'
COL_柱排 = '柱排'; COL_护型 = 'DXAB'

def classify_dg(za, mid):
    """等高线8类 — 末位逻辑，阈值3"""
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); mid = str(mid) if pd.notna(mid) else ''
    lc = mid[-1] if len(mid) > 0 else ''
    ab = lc in 'AB'; cdef = lc in 'CDEF'
    if za > 0:
        if za == 1: return '等1'
        elif za >= 2 and ab: return '等3'
        elif za >= 2 and cdef and za <= 3: return '等2'
        elif za > 3 and cdef: return '等4'
        else: return '等0'
    elif za < 0:
        if za == -1: return '等5'
        elif za >= -3 and ab: return '等6'
        elif za <= -2 and cdef: return '等7'
        elif za < -3 and ab: return '等8'
        else: return '等0'
    else: return '零轴'

def get_冲高等级(za):
    """日冲22的H/T等级骨架：用ZA符号+柱排近似"""
    if pd.isna(za): return 'NA'
    za = float(za)
    if za > 0: return 'H'
    elif za < 0: return 'T'
    else: return 'I'

# ========== 主处理 ==========
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
files = files[:100]
print(f"处理 {len(files)} 个文件...", flush=True)

frames = []
t0 = time.time()

for fi, f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if COL_ZA not in df.columns or len(df) < 50: continue

        # 等高线
        df['等高线'] = df.apply(lambda r: classify_dg(r[COL_ZA], r[COL_MID]), axis=1)

        # 柱排首字：升/跌/人
        df['柱排类别'] = df[COL_柱排].fillna('').str[0]
        df['柱排类别'] = df['柱排类别'].apply(lambda x: '升' if x == '升' else ('跌' if x == '跌' else '人'))

        # 护型第二字：强(甲乙己) vs 弱(丙丁戊)
        df['护型强'] = df[COL_护型].fillna('').str[1].apply(lambda x: '强' if x in '甲乙己' else ('弱' if x in '丙丁戊' else '其他'))

        # ZA符号
        df['ZA符号'] = df[COL_ZA].apply(lambda x: '正' if x > 0 else ('负' if x < 0 else '零'))

        # 中符串末位
        df['中符末位'] = df[COL_MID].fillna('').str[-1]
        df['中符组'] = df['中符末位'].apply(lambda x: 'AB' if x in 'AB' else ('CDEF' if x in 'CDEF' else '其他'))

        frames.append(df)
    except Exception as e:
        print(f"  错误 {f}: {e}", flush=True)

    if (fi+1) % 20 == 0:
        print(f"  已处理 {fi+1}/{len(files)} ({time.time()-t0:.0f}s)", flush=True)

data = pd.concat(frames, ignore_index=True)
dg = data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8'])]
print(f"\n总样本: {len(data):,}, 清洗后: {len(dg):,}", flush=True)

# ========== 一、等高线基础数据 ==========
print("\n" + "="*80, flush=True)
print("一、等高线8类 下日冲高≥3%", flush=True)
print("="*80, flush=True)
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥2%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*55, flush=True)
for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
    sub = dg[dg['等高线']==c]
    nh = sub[COL_NEXT].dropna()
    print(f"{c:>8} | {len(sub):>8,} | {(nh>3).mean():>7.1%} | {(nh>2).mean():>7.1%} | {(nh>5).mean():>7.1%} | {nh.mean():>6.2f}%", flush=True)

# ========== 二、等高线内部：柱排 × 护型 的区分度 ==========
print("\n" + "="*80, flush=True)
print("二、等高线内部子维度区分度", flush=True)
print("（如果等高线内部子维度仍有区分度，则日冲22有额外价值）", flush=True)
print("="*80, flush=True)

for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
    sub = dg[dg['等高线']==c]
    if len(sub) < 1000: continue
    nh = sub[COL_NEXT].dropna()
    base_p3 = (nh > 3).mean()
    base_avg = nh.mean()

    print(f"\n--- {c} (n={len(sub):,}, 基准P(≥3%)={base_p3:.1%}) ---", flush=True)

    # 2a. 柱排区分度
    print(f"  柱排子分类:", flush=True)
    zp_vals = []
    for zp in ['升','人','跌']:
        szp = sub[sub['柱排类别']==zp]
        if len(szp) < 100: continue
        nzp = szp[COL_NEXT].dropna()
        p3 = (nzp > 3).mean()
        zp_vals.append(p3)
        print(f"    {zp}: n={len(szp):,}, P(≥3%)={p3:.1%}, 平均冲高={nzp.mean():.2f}%", flush=True)
    if len(zp_vals) >= 2:
        print(f"    → 极差: {max(zp_vals)-min(zp_vals):.1%}", flush=True)

    # 2b. 护型区分度
    print(f"  护型子分类:", flush=True)
    hx_vals = []
    for hx in ['强','弱']:
        shx = sub[sub['护型强']==hx]
        if len(shx) < 100: continue
        nhx = shx[COL_NEXT].dropna()
        p3 = (nhx > 3).mean()
        hx_vals.append(p3)
        print(f"    {hx}: n={len(shx):,}, P(≥3%)={p3:.1%}, 平均冲高={nhx.mean():.2f}%", flush=True)
    if len(hx_vals) >= 2:
        print(f"    → 极差: {max(hx_vals)-min(hx_vals):.1%}", flush=True)

    # 2c. 柱排×护型 交叉（日冲22的H/T核心）
    print(f"  柱排×护型交叉:", flush=True)
    cross_vals = []
    for zp in ['升','人','跌']:
        for hx in ['强','弱']:
            sc = sub[(sub['柱排类别']==zp) & (sub['护型强']==hx)]
            if len(sc) < 50: continue
            nc = sc[COL_NEXT].dropna()
            p3 = (nc > 3).mean()
            cross_vals.append(p3)
            print(f"    {zp}+{hx}: n={len(sc):,}, P(≥3%)={p3:.1%}, 平均冲高={nc.mean():.2f}%", flush=True)
    if len(cross_vals) >= 2:
        print(f"    → 交叉极差: {max(cross_vals)-min(cross_vals):.1%}", flush=True)

# ========== 三、等高线是否丢失极端信号 ==========
print("\n" + "="*80, flush=True)
print("三、等高线内部不同子集的极端信号", flush=True)
print("="*80, flush=True)

# 等高线全局最佳
for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
    sub = dg[dg['等高线']==c]
    nh = sub[COL_NEXT].dropna()
    base_p3 = (nh > 3).mean()

    # 在这个等高线内，找P(≥3%)最高的子集（柱排×护型×中符末位）
    sub['子集key'] = sub['柱排类别'] + '_' + sub['护型强'] + '_' + sub['中符组']
    subset_groups = sub.groupby('子集key')[COL_NEXT].agg(['count', lambda x: (x>3).mean()])
    subset_groups = subset_groups[subset_groups['count']>=30].sort_values('<lambda_0>', ascending=False)
    if len(subset_groups) >= 3:
        best_p3 = subset_groups['<lambda_0>'].iloc[0]
        print(f"  {c}: 最高子集P(≥3%)={best_p3:.1%} vs 整体{base_p3:.1%} (差值{best_p3-base_p3:.1%})", flush=True)
        for s, r in subset_groups.head(3).iterrows():
            print(f"    {s:>15}: n={r['count']:>6,}, P(≥3%)={r['<lambda_0>']:.1%}", flush=True)

# ========== 四、结论 ==========
print("\n" + "="*80, flush=True)
print("结论", flush=True)
print("="*80, flush=True)
print("1. 等高线内部子维度有无区分度？", flush=True)
print("2. 柱排+护型是否在等高线之上仍有信息？", flush=True)
print("3. 等高线是否完全可替代日冲22？", flush=True)
print("", flush=True)

# 汇总：各等高线内部极差
max_ranges = []
for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
    sub = dg[dg['等高线']==c]
    if len(sub) < 1000: continue
    cross_vals = []
    for zp in ['升','人','跌']:
        for hx in ['强','弱']:
            sc = sub[(sub['柱排类别']==zp) & (sub['护型强']==hx)]
            if len(sc) < 50: continue
            nc = sc[COL_NEXT].dropna()
            cross_vals.append((nc > 3).mean())
    if len(cross_vals) >= 2:
        max_ranges.append((c, max(cross_vals)-min(cross_vals), max(cross_vals), min(cross_vals)))

print("各等高线内柱排×护型极差:", flush=True)
for c, rng, mx, mn in sorted(max_ranges, key=lambda x: -x[1]):
    print(f"  {c}: 极差{rng:.1%} (最高{mx:.1%} vs 最低{mn:.1%})", flush=True)

best_avg = sum(rng for _, rng, _, _ in max_ranges) / len(max_ranges) if max_ranges else 0
print(f"  平均极差: {best_avg:.1%}", flush=True)
print(f"  等高线间极差: {dg.groupby('等高线')[COL_NEXT].apply(lambda x: (x>3).mean()).max() - dg.groupby('等高线')[COL_NEXT].apply(lambda x: (x>3).mean()).min():.1%}", flush=True)

# 核心判断：等高线内部极差 vs 等高线间极差
# 内部极差 = 等高线内柱排×护型交叉的P(≥3%)差异
# 间极差 = 等高线8类之间的P(≥3%)差异
between_range = dg.groupby('等高线')[COL_NEXT].apply(lambda x: (x>3).mean()).max() - dg.groupby('等高线')[COL_NEXT].apply(lambda x: (x>3).mean()).min()
if best_avg > between_range:
    print(f"\n核心判断: 等高线内部极差({best_avg:.1%}) > 等高线间极差({between_range:.1%})", flush=True)
    print(f"  → 日冲22的柱排+护型信息量 > 等高线本身的信息量", flush=True)
    print(f"  → 等高线不能完全替代日冲22，日冲22仍保留大量额外信息", flush=True)
else:
    print(f"\n核心判断: 等高线内部极差({best_avg:.1%}) ≤ 等高线间极差({between_range:.1%})", flush=True)
    print(f"  → 日冲22的柱排+护型信息量 ≤ 等高线本身", flush=True)
    print(f"  → 等高线可完全替代日冲22", flush=True)

print(f"\n耗时: {time.time()-t0:.0f}s", flush=True)