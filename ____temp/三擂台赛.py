# -*- coding: utf-8 -*-
"""
三擂台赛：等高线基座 vs 等高线+柱排+护型 vs 日冲22态
- 同一批数据，同时计算三种分类
- 门开后(ZC>0 + DXCD=上)，核心池
- 按P(≥3%)排序，映射操作等级A/B/C/D/E
"""
import sys, time, os, glob, warnings
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

DATA_DIR = os.path.join('昭明算展', '谕组日')
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_NEXT = '次日高幅'
COL_柱排 = '柱排'; COL_护型 = 'DXAB'
COL_涨幅 = '涨幅'; COL_高幅 = '高幅'

# ========== 分类函数 ==========
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

# ========== 市板映射 ==========
市板映射 = pd.read_csv('____temp/市板映射.csv', encoding='utf-8')
市板映射['CIDL'] = 市板映射['CIDL'].astype(str).str.strip()
市板dict = dict(zip(市板映射['CIDL'], 市板映射['市板']))
# 核心池 = Qic(中证500) + Qim(中证1000) + Qit(中证2000) + Qin(中证非)
核心池板块 = {'Qic', 'Qim', 'Qit', 'Qin'}
排除池板块 = {'Qd', 'Qe', 'Qif', 'Qst'}
print(f"市板映射: {len(市板映射)} 条, 核心池板块: {核心池板块}", flush=True)

# ========== 主处理 ==========
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f"总文件数: {len(files)}")
# 随机抽样，避免字母序偏倚
import random
random.seed(42)
random.shuffle(files)
files = files[:500]
print(f"随机取500个文件...", flush=True)

frames = []; t0 = time.time()
匹配_核心 = 0; 匹配_排除 = 0; 匹配_未映射 = 0

for fi, f in enumerate(files):
    try:
        # 从文件名提取 CIDL
        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        市板 = 市板dict.get(cidl, None)

        df = pd.read_csv(f, encoding='gbk')
        if COL_ZA not in df.columns or len(df) < 50: continue

        # 记录市板
        if 市板 in 核心池板块:
            df['池'] = '核心'
            匹配_核心 += 1
        elif 市板 in 排除池板块:
            df['池'] = '排除'
            匹配_排除 += 1
        else:
            df['池'] = '未映射'
            匹配_未映射 += 1

        # 等高线
        df['等高线'] = df.apply(lambda r: classify_dg(r[COL_ZA], r[COL_MID]), axis=1)

        # 柱排首字
        df['柱排'] = df[COL_柱排].fillna('').str[0]
        df['柱排'] = df['柱排'].apply(lambda x: '升' if x == '升' else ('跌' if x == '跌' else '人'))

        # 护型第二字：强/弱
        df['护型'] = df[COL_护型].fillna('').str[1]
        df['护型'] = df['护型'].apply(lambda x: '强' if x in '甲乙己' else ('弱' if x in '丙丁戊' else '其他'))

        # 中符末位
        df['中符末'] = df[COL_MID].fillna('').str[-1]

        # 日冲22 H/T 状态（简化版，只覆盖 H/T >90% 数据）
        # H1-H6: ZA>0
        # T1-T4: ZA<0
        # I/O: 需要穿越检测，单独处理
        df['ZA符号'] = df[COL_ZA].apply(lambda x: '正' if x > 0 else ('负' if x < 0 else '零'))
        df['H状态'] = ''

        # H_ DJA之上
        mask_H = df['ZA符号'] == '正'
        df.loc[mask_H & (df['柱排']=='升') & (df['中符末']=='C'), 'H状态'] = 'H1'
        df.loc[mask_H & (df['H状态']=='') & (df['柱排']=='升') & (df['护型']=='强'), 'H状态'] = 'H2'
        df.loc[mask_H & (df['H状态']=='') & (df['柱排']=='升') & (df['护型']=='弱'), 'H状态'] = 'H3'
        df.loc[mask_H & (df['H状态']=='') & (df['柱排']=='跌'), 'H状态'] = 'H6'
        df.loc[mask_H & (df['H状态']=='') & (df[COL_ZA]<=3), 'H状态'] = 'H4'
        df.loc[mask_H & (df['H状态']==''), 'H状态'] = 'H5'

        # T_ DJA之下
        df['T状态'] = ''
        mask_T = df['ZA符号'] == '负'
        df.loc[mask_T & (df['柱排']=='升') & (df['护型']=='弱'), 'T状态'] = 'T1'
        df.loc[mask_T & (df['T状态']=='') & (df['柱排']=='跌'), 'T状态'] = 'T2'
        df.loc[mask_T & (df['T状态']=='') & (df[COL_ZA]>=-3), 'T状态'] = 'T3'
        df.loc[mask_T & (df['T状态']==''), 'T状态'] = 'T4'

        # I/O 穿越态（需要前一行）
        df['前日ZA'] = df[COL_ZA].shift(1)
        df['前日涨幅'] = df[COL_涨幅].shift(1)
        df['前日柱排'] = df[COL_柱排].shift(1).fillna('').str[0]
        df['前日柱排'] = df['前日柱排'].apply(lambda x: '升' if x == '升' else ('跌' if x == '跌' else '人'))
        df['前日ZA符号'] = df['前日ZA'].apply(lambda x: '正' if x > 0 else ('负' if x < 0 else '零') if pd.notna(x) else 'NA')

        # I_ 负转正当天
        df['I状态'] = ''
        mask_I = (df['前日ZA符号']=='负') & (df['ZA符号']=='正')
        df.loc[mask_I & (df[COL_ZA] - df['前日ZA'] >= 3) & (df[COL_涨幅] >= 2), 'I状态'] = 'I1'
        # I4: 需要未来数据，简化处理
        df.loc[mask_I & (df['I状态']==''), 'I状态'] = 'I2'  # 默认归入I2

        # O_ 正转负当天
        df['O状态'] = ''
        mask_O = (df['前日ZA符号']=='正') & (df['ZA符号']=='负')
        df.loc[mask_O & (df[COL_ZA] - df['前日ZA'] <= -3) & (df[COL_涨幅] <= -2), 'O状态'] = 'O1'
        df.loc[mask_O & (df['O状态']==''), 'O状态'] = 'O6'  # 默认归入O6

        # 合并成日冲22态
        df['日冲22'] = df['H状态'] + df['T状态'] + df['I状态'] + df['O状态']
        df['日冲22'] = df['日冲22'].apply(lambda x: x if x != '' else '零轴')

        # 门开条件
        df['门开'] = (df[COL_ZC] > 0) & (df[COL_ZE] > 0)

        frames.append(df)
    except Exception as e:
        print(f"  错误 {f}: {e}", flush=True)

    if (fi+1) % 100 == 0:
        print(f"  已处理 {fi+1}/{len(files)} ({time.time()-t0:.0f}s)", flush=True)

data = pd.concat(frames, ignore_index=True)
print(f"\n总样本: {len(data):,} 行, {time.time()-t0:.0f}s", flush=True)
print(f"池分布: 核心={匹配_核心}文件, 排除={匹配_排除}文件, 未映射={匹配_未映射}文件", flush=True)

# 清洗 + 只保留核心池
data = data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
data_core = data[data['池'] == '核心'].copy()
data_exc = data[data['池'] == '排除'].copy()
print(f"\n核心池: {len(data_core):,} 行, 排除池: {len(data_exc):,} 行", flush=True)

# 门开基准对比
print(f"\n门开基准: 核心池门开 {len(data_core[data_core['门开']]):,} ({len(data_core[data_core['门开']])/len(data_core)*100:.1f}%), 排除池门开 {len(data_exc[data_exc['门开']]):,} ({len(data_exc[data_exc['门开']])/len(data_exc)*100:.1f}%)", flush=True)
print(f"核心池门开P(≥3%): {(data_core[data_core['门开']][COL_NEXT].dropna()>3).mean():.1%}", flush=True)
print(f"排除池门开P(≥3%): {(data_exc[data_exc['门开']][COL_NEXT].dropna()>3).mean():.1%}", flush=True)

# 使用核心池
data = data_core.copy()
print(f"\n=== 以下全部为核心池数据 ===", flush=True)

# ========== 一、全样本基础分布 ==========
print("\n" + "="*80, flush=True)
print("一、三擂台 - 全样本(门开前)分布", flush=True)
print("="*80, flush=True)

# 擂台A: 等高线8类
print("\n--- 擂台A: 等高线8类 ---", flush=True)
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*50, flush=True)
for c in ['等1','等2','等3','等4','等5','等6','等7','等8','零轴']:
    sub = data[data['等高线']==c]
    nh = sub[COL_NEXT].dropna()
    if len(nh) < 200: continue
    print(f"{c:>8} | {len(sub):>8,} | {(nh>3).mean():>7.1%} | {(nh>5).mean():>7.1%} | {nh.mean():>6.2f}%", flush=True)

# 擂台B: 等高线×柱排×护型
print("\n--- 擂台B: 等高线×柱排×护型 ---", flush=True)
print(f"{'分类':>24} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*65, flush=True)
dg_b = data.groupby(['等高线','柱排','护型'])[COL_NEXT].agg(['count', lambda x: (x>3).mean(), lambda x: (x>5).mean(), 'mean'])
dg_b = dg_b[dg_b['count']>=100].sort_values('<lambda_0>', ascending=False)
for idx, r in dg_b.iterrows():
    lab = f"{idx[0]}_{idx[1]}_{idx[2]}"
    print(f"{lab:>24} | {r['count']:>8,} | {r['<lambda_0>']:>7.1%} | {r['<lambda_1>']:>7.1%} | {r['mean']:>6.2f}%", flush=True)
print(f"  共{len(dg_b)}个组合, 极差: {dg_b['<lambda_0>'].max()-dg_b['<lambda_0>'].min():.1%}", flush=True)

# 擂台C: 日冲22态
print("\n--- 擂台C: 日冲22态 ---", flush=True)
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*50, flush=True)
dg_c = data.groupby('日冲22')[COL_NEXT].agg(['count', lambda x: (x>3).mean(), lambda x: (x>5).mean(), 'mean'])
dg_c = dg_c[dg_c['count']>=100].sort_values('<lambda_0>', ascending=False)
for idx, r in dg_c.iterrows():
    print(f"{idx:>8} | {r['count']:>8,} | {r['<lambda_0>']:>7.1%} | {r['<lambda_1>']:>7.1%} | {r['mean']:>6.2f}%", flush=True)
print(f"  共{len(dg_c)}个状态, 极差: {dg_c['<lambda_0>'].max()-dg_c['<lambda_0>'].min():.1%}", flush=True)

# ========== 二、门开后核心比较 ==========
print("\n\n" + "="*80, flush=True)
print("二、门开后(ZC>0 + DXCD=上) 三擂台对比", flush=True)
print("="*80, flush=True)

data_gate = data[data['门开']].copy()
print(f"门开后样本: {len(data_gate):,} 行 ({len(data_gate)/len(data)*100:.1f}%)", flush=True)

# 擂台A: 等高线8类（门开后）
print("\n--- 擂台A: 等高线8类(门开后) ---", flush=True)
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*50, flush=True)
a_vals = []
for c in ['等1','等2','等3','等4','等5','等6','等7','等8','零轴']:
    sub = data_gate[data_gate['等高线']==c]
    nh = sub[COL_NEXT].dropna()
    if len(nh) < 100: continue
    p3 = (nh>3).mean()
    a_vals.append((c, p3, len(sub), (nh>2).mean(), nh.mean()))
    print(f"{c:>8} | {len(sub):>8,} | {p3:>7.1%} | {(nh>5).mean():>7.1%} | {nh.mean():>6.2f}%", flush=True)
a_range = max(a_vals, key=lambda x: x[1])[1] - min(a_vals, key=lambda x: x[1])[1] if a_vals else 0
print(f"  极差: {a_range:.1%}", flush=True)

# 擂台B: 等高线×柱排×护型（门开后）
print("\n--- 擂台B: 等高线×柱排×护型(门开后) ---", flush=True)
print(f"{'分类':>24} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥2%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*65, flush=True)
b_grp = data_gate.groupby(['等高线','柱排','护型'])[COL_NEXT].agg(['count', lambda x: (x>3).mean(), lambda x: (x>2).mean(), 'mean'])
b_grp = b_grp[b_grp['count']>=50].sort_values('<lambda_0>', ascending=False)
b_vals = []
for idx, r in b_grp.iterrows():
    lab = f"{idx[0]}_{idx[1]}_{idx[2]}"
    b_vals.append((lab, r['<lambda_0>'], r['count']))
    print(f"{lab:>24} | {r['count']:>8,} | {r['<lambda_0>']:>7.1%} | {r['<lambda_1>']:>7.1%} | {r['mean']:>6.2f}%", flush=True)
b_range = max(b_vals, key=lambda x: x[1])[1] - min(b_vals, key=lambda x: x[1])[1] if b_vals else 0
print(f"  共{len(b_grp)}个组合, 极差: {b_range:.1%}", flush=True)

# 擂台C: 日冲22态（门开后）
print("\n--- 擂台C: 日冲22态(门开后) ---", flush=True)
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥2%)':>8} | {'平均冲高':>8}", flush=True)
print("-"*55, flush=True)
c_grp = data_gate.groupby('日冲22')[COL_NEXT].agg(['count', lambda x: (x>3).mean(), lambda x: (x>2).mean(), 'mean'])
c_grp = c_grp[c_grp['count']>=50].sort_values('<lambda_0>', ascending=False)
c_vals = []
for idx, r in c_grp.iterrows():
    c_vals.append((idx, r['<lambda_0>'], r['count']))
    print(f"{idx:>8} | {r['count']:>8,} | {r['<lambda_0>']:>7.1%} | {r['<lambda_1>']:>7.1%} | {r['mean']:>6.2f}%", flush=True)
c_range = max(c_vals, key=lambda x: x[1])[1] - min(c_vals, key=lambda x: x[1])[1] if c_vals else 0
print(f"  共{len(c_grp)}个状态, 极差: {c_range:.1%}", flush=True)

# ========== 三、操作等级映射 ==========
print("\n\n" + "="*80, flush=True)
print("三、操作等级映射（按P(≥3%)排序）", flush=True)
print("="*80, flush=True)

def map_grade(p3):
    if p3 >= 0.60: return 'A'
    if p3 >= 0.50: return 'B'
    if p3 >= 0.40: return 'C'
    if p3 >= 0.30: return 'D'
    return 'E'

print("\n--- 擂台A: 等高线8类等级映射 ---", flush=True)
print(f"{'等级':>4} | {'分类':>8} | {'P(≥3%)':>8} | {'样本':>8}", flush=True)
print("-"*35, flush=True)
for c, p3, n, _, _ in sorted(a_vals, key=lambda x: -x[1]):
    g = map_grade(p3)
    print(f"  {g} | {c:>8} | {p3:>7.1%} | {n:>8,}", flush=True)

print("\n--- 擂台B: 等高线×柱排×护型等级映射 ---", flush=True)
print(f"{'等级':>4} | {'分类':>24} | {'P(≥3%)':>8} | {'样本':>8}", flush=True)
print("-"*50, flush=True)
for lab, p3, n in sorted(b_vals, key=lambda x: -x[1]):
    g = map_grade(p3)
    print(f"  {g} | {lab:>24} | {p3:>7.1%} | {n:>8,}", flush=True)

print("\n--- 擂台C: 日冲22态等级映射 ---", flush=True)
print(f"{'等级':>4} | {'分类':>8} | {'P(≥3%)':>8} | {'样本':>8}", flush=True)
print("-"*35, flush=True)
for idx, p3, n in sorted(c_vals, key=lambda x: -x[1]):
    g = map_grade(p3)
    print(f"  {g} | {idx:>8} | {p3:>7.1%} | {n:>8,}", flush=True)

# ========== 四、A/B级操作对比 ==========
print("\n\n" + "="*80, flush=True)
print("四、关键指标对比", flush=True)
print("="*80, flush=True)

# 擂台A
a_ab = sum(1 for _, p3, _, _, _ in a_vals if p3 >= 0.50)
a_ab_p3 = max([p3 for _, p3, _, _, _ in a_vals if p3 >= 0.50], default=0)
a_ab_n = sum(n for _, p3, n, _, _ in a_vals if p3 >= 0.50)
a_top_p3 = max(a_vals, key=lambda x: x[1])[1] if a_vals else 0
a_top_n = max(a_vals, key=lambda x: x[1])[2] if a_vals else 0

# 擂台B
b_ab = sum(1 for _, p3, _ in b_vals if p3 >= 0.50)
b_ab_p3 = max([p3 for _, p3, _ in b_vals if p3 >= 0.50], default=0)
b_ab_n = sum(n for _, p3, n in b_vals if p3 >= 0.50)
b_top_p3 = max(b_vals, key=lambda x: x[1])[1] if b_vals else 0
b_top_n = max(b_vals, key=lambda x: x[1])[2] if b_vals else 0

# 擂台C
c_ab = sum(1 for _, p3, _ in c_vals if p3 >= 0.50)
c_ab_p3 = max([p3 for _, p3, _ in c_vals if p3 >= 0.50], default=0)
c_ab_n = sum(n for _, p3, n in c_vals if p3 >= 0.50)
c_top_p3 = max(c_vals, key=lambda x: x[1])[1] if c_vals else 0
c_top_n = max(c_vals, key=lambda x: x[1])[2] if c_vals else 0

print(f"\n{'指标':>20} | {'擂台A':>12} | {'擂台B':>12} | {'擂台C':>12}", flush=True)
print("-"*60, flush=True)
print(f"{'A/B级数量':>20} | {a_ab:>12} | {b_ab:>12} | {c_ab:>12}", flush=True)
print(f"{'A/B级最高P(≥3%)':>20} | {a_ab_p3:>11.1%} | {b_ab_p3:>11.1%} | {c_ab_p3:>11.1%}", flush=True)
print(f"{'A/B级总样本':>20} | {a_ab_n:>12,} | {b_ab_n:>12,} | {c_ab_n:>12,}", flush=True)
print(f"{'全局最高P(≥3%)':>20} | {a_top_p3:>11.1%} | {b_top_p3:>11.1%} | {c_top_p3:>11.1%}", flush=True)
print(f"{'最高态样本量':>20} | {a_top_n:>12,} | {b_top_n:>12,} | {c_top_n:>12,}", flush=True)
print(f"{'整体极差':>20} | {a_range:>11.1%} | {b_range:>11.1%} | {c_range:>11.1%}", flush=True)

print(f"\n耗时: {time.time()-t0:.0f}s", flush=True)