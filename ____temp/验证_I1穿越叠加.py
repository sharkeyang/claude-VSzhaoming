# -*- coding: utf-8 -*-
"""
I1/O1穿越检测叠加在等高线基座上的效果验证
核心问题：等高线基座 + I1条件，能否复现日冲22的I1态优势？
"""
import sys, os, time, glob, warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

sys.path.insert(0, os.path.join('____temp'))
from 随机抽样工具 import 随机取文件, 加载市板映射, 核心池板块, 排除池板块

DATA_DIR = '昭明算展/谕组日'
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_NEXT = '次日高幅'
COL_柱排 = '柱排'; COL_护型 = 'DXAB'
COL_涨幅 = '涨幅'; COL_高幅 = '高幅'

def classify_dg(za, mid):
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

# ========== 加载 + 随机抽样 ==========
加载市板映射()
files, 市板列 = 随机取文件(500, verbose=True)
print(f"\n总文件: {len(files)}, 开始处理...", flush=True)

frames = []; t0 = time.time()
core_count = 0

for fi, f in enumerate(files):
    try:
        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        市板 = 市板列[fi]

        df = pd.read_csv(f, encoding='gbk')
        if COL_ZA not in df.columns or len(df) < 50: continue

        if 市板 in 核心池板块:
            df['池'] = '核心'
        elif 市板 in 排除池板块:
            df['池'] = '排除'
        else:
            df['池'] = '未知'

        # 等高线
        df['等高线'] = df.apply(lambda r: classify_dg(r[COL_ZA], r[COL_MID]), axis=1)

        # 柱排首字
        df['柱排'] = df[COL_柱排].fillna('').str[0]
        df['柱排'] = df['柱排'].apply(lambda x: '升' if x == '升' else ('跌' if x == '跌' else '人'))

        # 护型
        df['护型'] = df[COL_护型].fillna('').str[1]
        df['护型'] = df['护型'].apply(lambda x: '强' if x in '甲乙己' else ('弱' if x in '丙丁戊' else '其他'))

        # 中符末位
        df['中符末'] = df[COL_MID].fillna('').str[-1]

        # 门开
        df['门开'] = (df[COL_ZC] > 0) & (df[COL_ZE] > 0)

        # 前日数据（穿越检测需要）
        df['前日ZA'] = df[COL_ZA].shift(1)
        df['前日涨幅'] = df[COL_涨幅].shift(1)

        # I1 穿越检测：负转正 + 大跳 + 大涨
        df['is_I1'] = (df['前日ZA'] < 0) & (df[COL_ZA] >= 0) & \
                      (df[COL_ZA] - df['前日ZA'] >= 3) & (df[COL_涨幅] >= 2)

        # O1 穿越检测：正转负 + 大跌 + 大跌
        df['is_O1'] = (df['前日ZA'] > 0) & (df[COL_ZA] <= 0) & \
                      (df[COL_ZA] - df['前日ZA'] <= -3) & (df[COL_涨幅] <= -2)

        df['is_I1O1'] = df['is_I1'] | df['is_O1']

        # 日冲22 I/O态（简化对比）
        df['前日ZA符号'] = df['前日ZA'].apply(lambda x: '正' if x > 0 else ('负' if x < 0 else '零') if pd.notna(x) else 'NA')
        df['日冲22_I'] = ''
        mask_I = (df['前日ZA符号']=='负') & (df[COL_ZA] >= 0) & (df['is_I1'])
        df.loc[mask_I, '日冲22_I'] = 'I1'
        df['日冲22_O'] = ''
        mask_O = (df['前日ZA符号']=='正') & (df[COL_ZA] <= 0) & (df['is_O1'])
        df.loc[mask_O, '日冲22_O'] = 'O1'

        frames.append(df)
    except Exception as e:
        print(f"  错误 {f}: {e}", flush=True)

    if (fi+1) % 100 == 0:
        print(f"  已处理 {fi+1}/{len(files)} ({time.time()-t0:.0f}s)", flush=True)

data = pd.concat(frames, ignore_index=True)
data_core = data[data['池']=='核心'].copy()
data_gate = data_core[data_core['门开']].copy()
print(f"\n核心池: {len(data_core):,} 行, 门开后: {len(data_gate):,} 行", flush=True)
print(f"I1占比: {data_gate['is_I1'].mean():.2%} ({data_gate['is_I1'].sum():,} 行)", flush=True)
print(f"O1占比: {data_gate['is_O1'].mean():.2%} ({data_gate['is_O1'].sum():,} 行)", flush=True)
print(f"I1或O1占比: {data_gate['is_I1O1'].mean():.2%} ({data_gate['is_I1O1'].sum():,} 行)", flush=True)

# ========== 一、I1穿越检测叠加效果 ==========
print("\n" + "="*80, flush=True)
print("一、等高线×柱排×护型 + I1穿越检测 → P(≥3%)变化", flush=True)
print("="*80, flush=True)
print(f"{'等高线基座分类':>24} | {'基准P(≥3%)':>10} | {'基准样本':>8} | {'+I1 P(≥3%)':>10} | {'+I1样本':>8} | {'提升':>6}", flush=True)
print("-"*70, flush=True)

dg = data_gate.groupby(['等高线','柱排','护型'])
results = []
for idx, sub in dg:
    nh = sub[COL_NEXT].dropna()
    base_p3 = (nh > 3).mean()
    base_n = len(sub)

    # +I1
    sub_i1 = sub[sub['is_I1']]
    nh_i1 = sub_i1[COL_NEXT].dropna()
    i1_p3 = (nh_i1 > 3).mean() if len(nh_i1) >= 20 else 0
    i1_n = len(nh_i1)

    # +O1
    sub_o1 = sub[sub['is_O1']]
    nh_o1 = sub_o1[COL_NEXT].dropna()
    o1_p3 = (nh_o1 > 3).mean() if len(nh_o1) >= 20 else 0
    o1_n = len(nh_o1)

    # +I1O1
    sub_io = sub[sub['is_I1O1']]
    nh_io = sub_io[COL_NEXT].dropna()
    io_p3 = (nh_io > 3).mean() if len(nh_io) >= 20 else 0
    io_n = len(nh_io)

    label = f"{idx[0]}_{idx[1]}_{idx[2]}"
    results.append((label, base_p3, base_n, i1_p3, i1_n, o1_p3, o1_n, io_p3, io_n))

# 按+I1效果排序
results.sort(key=lambda x: -x[1])

for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in results:
    if bn < 1000: continue  # 只显示大样本组合
    lift = f"+{i1p-bp:.1%}" if i1p > bp else f"{i1p-bp:.1%}" if i1n >= 20 else "—"
    print(f"{label:>24} | {bp:>9.1%} | {bn:>8,} | {i1p:>9.1%} | {i1n:>8} | {lift:>6}", flush=True)

# ========== 二、穿越态叠加汇总 ==========
print("\n" + "="*80, flush=True)
print("二、穿越态叠加效果汇总", flush=True)
print("="*80, flush=True)

# 基准（不加穿越）
base_p3 = (data_gate[COL_NEXT].dropna() > 3).mean()
print(f"\n核心池门开后基准: P(≥3%) = {base_p3:.1%} (n={len(data_gate):,})", flush=True)

# 加I1
sub_i1 = data_gate[data_gate['is_I1']]
print(f"叠加I1: P(≥3%) = {(sub_i1[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_i1):,}, 占比{len(sub_i1)/len(data_gate):.2%})", flush=True)

# 加O1
sub_o1 = data_gate[data_gate['is_O1']]
print(f"叠加O1: P(≥3%) = {(sub_o1[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_o1):,}, 占比{len(sub_o1)/len(data_gate):.2%})", flush=True)

# 加I1+O1
sub_io = data_gate[data_gate['is_I1O1']]
print(f"叠加I1或O1: P(≥3%) = {(sub_io[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_io):,}, 占比{len(sub_io)/len(data_gate):.2%})", flush=True)

# 不加I1O1
sub_no = data_gate[~data_gate['is_I1O1']]
print(f"排除I1O1: P(≥3%) = {(sub_no[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_no):,})", flush=True)

# 最佳叠加（等高线基座 + I1）
print(f"\n最佳叠加组合（等高线基座 + I1）:", flush=True)
best = sorted(results, key=lambda x: -x[3] if x[4] >= 20 else 0)
for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in best[:5]:
    if i1n >= 20:
        print(f"  {label} + I1: {i1p:.1%} (n={i1n}, 基准{bp:.1%}, 提升{i1p-bp:.1%})", flush=True)

print(f"\n最佳叠加组合（等高线基座 + O1）:", flush=True)
for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in sorted(results, key=lambda x: -x[5] if x[6] >= 20 else 0)[:5]:
    if o1n >= 20:
        print(f"  {label} + O1: {o1p:.1%} (n={o1n}, 基准{bp:.1%}, 提升{o1p-bp:.1%})", flush=True)

# ========== 三、与日冲22 I1/O1态的直接对比 ==========
print("\n" + "="*80, flush=True)
print("三、等高线基座+I1 vs 日冲22 I1/O1态 直接对比", flush=True)
print("="*80, flush=True)

# 日冲22 I1态
sub_i1_all = data_gate[data_gate['日冲22_I']=='I1']
print(f"\n日冲22 I1态: P(≥3%) = {(sub_i1_all[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_i1_all):,})", flush=True)

# 日冲22 O1态
sub_o1_all = data_gate[data_gate['日冲22_O']=='O1']
print(f"日冲22 O1态: P(≥3%) = {(sub_o1_all[COL_NEXT].dropna()>3).mean():.1%} (n={len(sub_o1_all):,})", flush=True)

# 等高线基准（不加穿越）中最好的组合
print(f"\n等高线基座最佳（不加穿越）: ", flush=True)
best_no = sorted(results, key=lambda x: -x[1])
for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in best_no[:3]:
    print(f"  {label}: {bp:.1%} (n={bn:,})", flush=True)

# 等高线基座+I1最好的组合
print(f"\n等高线基座+I1: ", flush=True)
for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in sorted(results, key=lambda x: -x[3])[:5]:
    if i1n >= 20:
        print(f"  {label}+I1: {i1p:.1%} (n={i1n}, 基准{bp:.1%})", flush=True)

# ========== 四、结论 ==========
print("\n" + "="*80, flush=True)
print("结论", flush=True)
print("="*80, flush=True)

# 基准值
base_all = (data_gate[COL_NEXT].dropna() > 3).mean()
i1_all = (sub_i1_all[COL_NEXT].dropna() > 3).mean() if len(sub_i1_all) >= 20 else 0
o1_all = (sub_o1_all[COL_NEXT].dropna() > 3).mean() if len(sub_o1_all) >= 20 else 0

print(f"1. 门开后核心池基准: {base_all:.1%}", flush=True)
print(f"2. I1穿越检测: {i1_all:.1%} (+{i1_all-base_all:.1%} vs 基准)", flush=True)
print(f"3. O1穿越检测: {o1_all:.1%} (+{o1_all-base_all:.1%} vs 基准)", flush=True)

# 最佳等高线基座+I1
best_i1 = sorted([(label, i1p, bn, i1n) for label, bp, bn, i1p, i1n, *_ in results if i1n >= 20], key=lambda x: -x[1])
best_o1 = sorted([(label, o1p, bn, o1n) for label, *_ in results if len(results[0]) > 5 for label, bp, bn, i1p, i1n, o1p, o1n, iop, ion in [results[0]]], key=lambda x: -x[1])

print(f"4. 等高线基座+I1最佳: {best_i1[0][1]:.1%} ({best_i1[0][0]}, n={best_i1[0][3]})" if best_i1 else "4. 无足够样本", flush=True)

print(f"\n{'='*60}", flush=True)
print(f"最终判断：等高线基座 + I1/O1穿越检测 → 能否完全替代日冲22？", flush=True)
print(f"基准(base) vs I1穿越差异: {i1_all-base_all:.1%}", flush=True)
print(f"{'='*60}", flush=True)

print(f"\n耗时: {time.time()-t0:.0f}s", flush=True)