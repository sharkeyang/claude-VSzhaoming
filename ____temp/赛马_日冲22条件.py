# -*- coding: utf-8 -*-
"""
赛马_日冲22条件.py — 条件赛马分析
把日冲22态中的各个条件拆分出来，逐一叠加到"等高线×柱排×护型"基座上，
测试哪些条件有助于提升 P(下日冲高≥2%)。

方法：
- 随机取 500 个谕组日文件（避免字母序偏倚）
- 只分析核心池(Qic/Qim/Qit/Qin)，门开后(ZC>0 且 ZE>0)
- 对每个条件，在等高线×柱排×护型每个分组内，比较"带条件" vs "不带条件"的 P(≥2%)/P(≥3%)
- 组内提升按条件样本量加权平均 = 该条件在基座上的净提升(pp)
- 同时给出全局(不加条件)基线作为参照

判定：提升≥2pp 保留，<2pp 舍弃。
"""
import os, glob, time, random, warnings
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

DATA_DIR = os.path.join('昭明算展', '谕组日')
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_NEXT = '次日高幅'
COL_柱排 = '柱排'; COL_护型 = 'DXAB'
COL_涨幅 = '涨幅'; COL_顶型 = '顶型'; COL_波型 = '波型'; COL_连阳 = 'BT连阳'
N = 500
SEED = 42
MIN_GROUP = 30   # 分组内条件样本量的最小阈值(否则统计噪声过大)

# ========== 等高线分类（与三擂台赛一致） ==========
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
核心池板块 = {'Qic', 'Qim', 'Qit', 'Qin'}

# ========== 随机抽样 ==========
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
random.seed(SEED); random.shuffle(files)
files = files[:N]
print(f"总文件 {len(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))):,}，随机取 {N} 个", flush=True)

# ========== 主处理 ==========
frames = []; t0 = time.time()
匹配_核心 = 0; 匹配_其他 = 0
for fi, f in enumerate(files):
    try:
        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        市板 = 市板dict.get(cidl, None)
        if 市板 not in 核心池板块:
            匹配_其他 += 1
            continue
        匹配_核心 += 1

        df = pd.read_csv(f, encoding='gbk')
        if COL_ZA not in df.columns or len(df) < 55: continue

        # 等高线
        df['等高线'] = df.apply(lambda r: classify_dg(r[COL_ZA], r[COL_MID]), axis=1)
        # 柱排首字
        df['柱排'] = df[COL_柱排].fillna('').str[0]
        df['柱排'] = df['柱排'].apply(lambda x: '升' if x == '升' else ('跌' if x == '跌' else '人'))
        # 护型第二字：强/弱
        df['护型'] = df[COL_护型].fillna('').str[1]
        df['护型'] = df['护型'].apply(lambda x: '强' if x in '甲乙己' else ('弱' if x in '丙丁戊' else '其他'))

        # ---- 条件计算 ----
        # 前日数据
        df['前日ZA'] = df[COL_ZA].shift(1)
        df['前日涨幅'] = df[COL_涨幅].shift(1)
        # 近5日均值/峰谷
        df['前5日ZA均值'] = df[COL_ZA].rolling(5, min_periods=5).mean().shift(1)
        df['前5日ZA峰谷'] = df[COL_ZA].rolling(5, min_periods=5).max().shift(1) \
                          - df[COL_ZA].rolling(5, min_periods=5).min().shift(1)

        ZA = df[COL_ZA]; 前ZA = df['前日ZA']
        # 1. I1穿越：前日ZA<0、今日ZA≥0、ZA跳≥3、涨幅≥2%
        df['c_I1'] = (前ZA < 0) & (ZA >= 0) & ((ZA - 前ZA) >= 3) & (df[COL_涨幅] >= 2)
        # 2. O1穿越：前日ZA>0、今日ZA≤0、ZA跳≤-3、跌幅≤-2%
        df['c_O1'] = (前ZA > 0) & (ZA <= 0) & ((ZA - 前ZA) <= -3) & (df[COL_涨幅] <= -2)
        # 3. 连阳≥3：BT连阳>=3
        df['c_连阳'] = df[COL_连阳] >= 3
        # 4. 连阴≥3：BT连阳<=-3
        df['c_连阴'] = df[COL_连阳] <= -3
        # 5. 顶型"龙"
        df['c_龙'] = df[COL_顶型].fillna('').str.contains('龙', na=False)
        # 6. 波型"多长/多空"
        df['c_多长'] = df[COL_波型].fillna('').str.contains('多长|多空', na=False)
        # 7. I2类：近DJA处回落再上破（前5日ZA内峰谷差≥2，且今日ZA为正且小）
        df['c_I2'] = (df['前5日ZA峰谷'] >= 2) & (ZA > 0) & (ZA <= 3)
        # 8. I5类：连阳≥3且涨幅<2%（碎步爬坡）
        df['c_I5'] = (df[COL_连阳] >= 3) & (df[COL_涨幅] < 2)
        # 9. O4类：前5日ZA均值≥0（M头逃命）
        df['c_O4'] = df['前5日ZA均值'] >= 0

        # 门开
        df['门开'] = (df[COL_ZC] > 0) & (df[COL_ZE] > 0)
        frames.append(df[['等高线','柱排','护型','门开',COL_NEXT,
                          'c_I1','c_O1','c_连阳','c_连阴','c_龙','c_多长','c_I2','c_I5','c_O4']])
    except Exception as e:
        print(f"  错误 {f}: {e}", flush=True)
    if (fi+1) % 100 == 0:
        print(f"  已处理 {fi+1}/{len(files)} ({time.time()-t0:.0f}s)", flush=True)

data = pd.concat(frames, ignore_index=True)
print(f"\n加载完成: 核心池 {匹配_核心} 文件, 其他 {匹配_其他} 文件, 总行数 {len(data):,} ({time.time()-t0:.0f}s)", flush=True)

# ========== 只保留有效等高线 + 门后核心池 ==========
data = data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate = data[data['门开']].copy()
gate = gate[gate[COL_NEXT].notna()]
print(f"门后核心池有效样本: {len(gate):,} 行", flush=True)

# ========== 条件清单 ==========
conds = [
    ('I1穿越', 'c_I1', '前日ZA<0→今日ZA≥0, 跳≥3, 涨幅≥2%'),
    ('O1穿越', 'c_O1', '前日ZA>0→今日ZA≤0, 跳≤-3, 跌幅≤-2%'),
    ('连阳≥3', 'c_连阳', '连续3日以上涨幅>0'),
    ('连阴≥3', 'c_连阴', '连续3日以上跌幅<0'),
    ('顶型龙', 'c_龙', '顶型列含"龙"字'),
    ('波型多长', 'c_多长', '波型列含"多长/多空"'),
    ('I2类', 'c_I2', '前5日ZA峰谷差≥2 且 0<ZA≤3'),
    ('I5类', 'c_I5', '连阳≥3 且 今日涨幅<2%'),
    ('O4类', 'c_O4', '前5日ZA均值≥0'),
]

# ========== 全局基线（不加任何条件） ==========
base_p2 = (gate[COL_NEXT] > 2).mean()
base_p3 = (gate[COL_NEXT] > 3).mean()
print(f"\n全局基线(门后核心池, 无条件): P(≥2%)={base_p2:.1%}  P(≥3%)={base_p3:.1%}  样本={len(gate):,}", flush=True)

# ========== 逐条件计算 ==========
rows = []
for 名称, col, 说明 in conds:
    sub = gate[gate[col]]
    n = len(sub)
    if n == 0:
        rows.append({'条件': 名称, '说明': 说明, '样本': 0, '样本占比': 0,
                     'P2': 0, 'P3': 0, '基P2': base_p2, '基P3': base_p3,
                     '提升P2': 0, '提升P3': 0, '净提升P2': 0, '净提升P3': 0,
                     '覆盖组数': 0, '一致正提升': 0})
        continue

    p2 = (sub[COL_NEXT] > 2).mean()
    p3 = (sub[COL_NEXT] > 3).mean()

    # 组内净提升（在等高线×柱排×护型基座内，加权）
    grp = gate.groupby(['等高线','柱排','护型'])
    grp_w_sum = 0.0; grp_n_sum = 0; 覆盖组 = 0; 一致正 = 0
    for key, g in grp:
        gsub = g[g[col]]
        if len(gsub) < MIN_GROUP: continue
        gbase = g[~g[col]]
        if len(gbase) < MIN_GROUP: continue
        p2_w = (gsub[COL_NEXT] > 2).mean()
        p2_wo = (gbase[COL_NEXT] > 2).mean()
        grp_w_sum += (p2_w - p2_wo) * len(gsub)
        grp_n_sum += len(gsub)
        覆盖组 += 1
        if (p2_w - p2_wo) > 0: 一致正 += 1
    净P2 = grp_w_sum / grp_n_sum if grp_n_sum else 0
    一致率 = 一致正 / 覆盖组 if 覆盖组 else 0

    rows.append({'条件': 名称, '说明': 说明, '样本': n, '样本占比': n/len(gate),
                 'P2': p2, 'P3': p3, '基P2': base_p2, '基P3': base_p3,
                 '提升P2': p2 - base_p2, '提升P3': p3 - base_p3,
                 '净提升P2': 净P2, '净提升P3': p3 - base_p3,
                 '覆盖组数': 覆盖组, '一致正提升': 一致率})

res = pd.DataFrame(rows)

# ========== 输出表格 ==========
print("\n" + "="*90, flush=True)
print("赛马结果 — 各条件在 等高线×柱排×护型 基座上的边际提升", flush=True)
print("="*90, flush=True)
print(f"{'条件':<8} | {'样本':>7} | {'占比':>6} | {'P2':>6} | {'P3':>6} | {'基P2':>6} | {'组内净升P2':>9} | {'一致率':>6} | {'覆盖组':>5}", flush=True)
print("-"*90, flush=True)
for _, r in res.sort_values('净提升P2', ascending=False).iterrows():
    if r['样本'] == 0:
        print(f"{r['条件']:<8} | {'0':>7} | {'0%':>6} | {'-':>6} | {'-':>6} | {'-':>6} | {'--':>9} | {'--':>6} | {0:>5}  (无匹配样本)", flush=True)
        continue
    print(f"{r['条件']:<8} | {r['样本']:>7,} | {r['样本占比']:>5.1%} | {r['P2']:>5.1%} | {r['P3']:>5.1%} | {r['基P2']:>5.1%} | {r['净提升P2']:>+8.1%} | {r['一致正提升']:>5.1%} | {r['覆盖组数']:>5}", flush=True)

# ========== 结论 ==========
print("\n" + "="*90, flush=True)
print("结论判定（以组内净提升P2为准：≥2pp 保留，<2pp 舍弃）", flush=True)
print("="*90, flush=True)
print(f"{'条件':<8} | {'净提升P2(pp)':>12} | {'判定':>6}", flush=True)
print("-"*40, flush=True)
for _, r in res.sort_values('净提升P2', ascending=False).iterrows():
    if r['样本'] == 0:
        print(f"{r['条件']:<8} | {'--':>12} | {'舍弃(无样本)':>6}", flush=True)
        continue
    pp = r['净提升P2'] * 100
    判定 = '保留' if pp >= 2 else '舍弃'
    print(f"{r['条件']:<8} | {pp:>+11.2f} | {判定:>6}", flush=True)

print("\n耗时: {:.0f}s".format(time.time()-t0), flush=True)