# -*- coding: utf-8 -*-
"""
日冲22态 vs 日层等高线(等1-8) 同数据对比
- 同一行数据同时计算两种分类
- 交叉表：等高线内各日冲22态的P(≥3%)差异
- 关键问题：等高线是否完全替代日冲22？
"""
import pandas as pd, numpy as np, os, glob, time, random
from collections import OrderedDict

DATA_DIR = os.path.join('昭明算展', '谕组日')
COL_ZA = '日ZA'; COL_ZC = '日ZC'; COL_ZE = '日ZE'
COL_MID = '中符串'; COL_TOP = '顶型'
COL_HR = '高幅'; COL_PR = '涨幅'; COL_NEXT = '次日高幅'
COL_DXEF = 'DXEF'; COL_DXCD = 'DXCD'; COL_DXAB = 'DXAB'
COL_柱排 = '柱排'; COL_护型 = 'DXAB'

random.seed(42); np.random.seed(42)

# ========== 一、分类函数 ==========

def classify_等高线(za, mid):
    """等1-8 + 零轴 — 末位逻辑 Right$(中符串,1)，阈值3"""
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); mid = str(mid) if pd.notna(mid) else ''
    last_char = mid[-1] if len(mid) > 0 else ''
    has_ab = last_char in 'AB'
    has_cdef = last_char in 'CDEF'
    if za > 0:
        if za == 1: return '等1'
        elif za >= 2 and has_ab: return '等3'
        elif za >= 2 and has_cdef and za <= 3: return '等2'
        elif za > 3 and has_cdef: return '等4'
        elif za >= 2: return '等0'
        else: return '等0'
    elif za < 0:
        if za == -1: return '等5'
        elif za >= -3 and has_ab: return '等6'
        elif za <= -2 and has_cdef: return '等7'
        elif za < -3 and has_ab: return '等8'
        elif za <= -2: return '等0'
        else: return '等0'
    else:
        return '零轴'

def classify_日冲22(row, prev_rows, next_rows):
    """
    日冲22态分类（简化版，基于VBA代码逻辑）
    需要历史行和未来行（I4双穿需要）
    返回: 状态名称, 状态编号(H1-H6/T1-T4/I1-I6/O1-O6)
    """
    za = row[COL_ZA]
    if pd.isna(za): return 'NA', 'NA'
    za = int(za)
    pr = row[COL_PR] if pd.notna(row[COL_PR]) else 0
    hr = row[COL_HR] if pd.notna(row[COL_HR]) else 0
    mid = str(row[COL_MID]) if pd.notna(row[COL_MID]) else ''
    zhu_pai = str(row[COL_柱排]) if pd.notna(row[COL_柱排]) else ''
    hu_xing = str(row[COL_护型]) if pd.notna(row[COL_护型]) else ''

    # 提取护型第二字（甲/乙/丙/丁/戊/己）
    hu_type = hu_xing[1:2] if len(hu_xing) > 1 else ''
    last_char = mid[-1] if len(mid) > 0 else ''
    first_char = mid[0] if len(mid) > 0 else ''
    zhu_pai_first = zhu_pai[0:1] if zhu_pai else ''

    # 计算前5日ZA
    prev_za = []
    for p in prev_rows:
        if p is not None and pd.notna(p[COL_ZA]):
            prev_za.append(int(p[COL_ZA]))
        else:
            prev_za.append(0)
    while len(prev_za) < 5:
        prev_za.insert(0, 0)

    # 前3柱排
    prev_zp = []
    for p in prev_rows:
        if p is not None and pd.notna(p[COL_柱排]):
            prev_zp.append(str(p[COL_柱排])[:1])
        else:
            prev_zp.append('')
    while len(prev_zp) < 3:
        prev_zp.insert(0, '')

    # 前日ZA（紧邻的前一行）
    prev_za_raw = int(prev_za[0]) if prev_za else 0  # prev_za[0] = 最近的前一行

    # 连阳/连阴
    lian_yang = 0; lian_yin = 0
    for p in prev_rows:
        if p is not None and pd.notna(p[COL_PR]):
            if p[COL_PR] > 0: lian_yang += 1
            else: break
        else: break
    for p in prev_rows:
        if p is not None and pd.notna(p[COL_PR]):
            if p[COL_PR] < 0: lian_yin += 1
            else: break
        else: break

    # ZA统计
    za_max = max(prev_za) if prev_za else 0
    za_min = min(prev_za) if prev_za else 0
    za_mean = sum(prev_za) / len(prev_za) if prev_za else 0

    # === 检测 ===
    state = ''

    # H_ DJA之上
    if za > 0:
        if zhu_pai_first == '升' and last_char == 'C':
            state = 'H1_升_日中符C'
        if not state and zhu_pai_first == '升' and hu_type in '甲乙己' and last_char != 'C':
            state = 'H2_升_护型强'
        if not state and zhu_pai_first == '升' and hu_type in '丙丁戊' and last_char != 'C':
            state = 'H3_升_护型弱'
        if not state and zhu_pai_first == '跌':
            state = 'H6_跌_跌排'
        if not state and za <= 3:
            state = 'H4_人_ZA3内'
        if not state:
            state = 'H5_人_ZA3外'
    # T_ DJA之下
    elif za < 0:
        if zhu_pai_first == '升' and hu_type in '丙丁戊':
            state = 'T1_升_护型弱'
        if not state and zhu_pai_first == '跌':
            state = 'T2_跌_跌排'
        if not state and za >= -3:
            state = 'T3_人_ZA3内'
        if not state:
            state = 'T4_人_ZA3外'
    # I_ 负转正当天
    elif prev_za_raw < 0 and za >= 0:
        if za - prev_za_raw >= 3 and pr >= 2:
            state = 'I1_暴涨_大柱上破'
        if not state and za_mean <= -3:
            # I4 双穿（需要未来数据）
            for j, nr in enumerate(next_rows):
                if nr is None or pd.isna(nr[COL_ZA]): break
                nza = int(nr[COL_ZA])
                if nza == -1:
                    for k, nr2 in enumerate(next_rows[j+1:j+11]):
                        if nr2 is None or pd.isna(nr2[COL_ZA]): break
                        if int(nr2[COL_ZA]) >= 0:
                            if k <= 5: state = 'I4_双穿_M底加仓'
                            break
                    break
        if not state and za_max >= -3:
            # I2: 回落确认
            peak_idx = 0; peak_val = 0
            for i, v in enumerate(prev_za):
                if v > peak_val: peak_val = v; peak_idx = i
            post_peak_min = min(prev_za[peak_idx:]) if peak_idx < len(prev_za)-1 else 9999
            if peak_idx < len(prev_za)-1 and peak_val - post_peak_min >= 2:
                state = 'I2_归JA_回落确认'
        if not state and za_max >= -3:
            state = 'I3_归JA_直上DJA'
        if not state:
            # I5: 乌龟爬坡
            if lian_yang >= 3 and pr < 2:
                state = 'I5_碎步_缓步上升'
        if not state:
            state = 'I6_其他_其他上破'
    # O_ 正转负当天
    elif prev_za_raw > 0 and za <= 0:
        if za_max > 0 and za - prev_za_raw <= -3 and pr <= -2:
            # O1: 需要前3非跌
            prev_3_not_decline = all(p is None or pd.isna(p[COL_PR]) or p[COL_PR] >= 0 for p in prev_rows[:3])
            if prev_3_not_decline:
                state = 'O1_晴天霹雳'
        if not state and za_max >= -3:
            # O2: 诱多陷阱
            peak_idx = 0; peak_val = 0
            for i, v in enumerate(prev_za):
                if v > peak_val: peak_val = v; peak_idx = i
            post_peak_min = min(prev_za[peak_idx:]) if peak_idx < len(prev_za)-1 else 9999
            if peak_idx < len(prev_za)-1 and peak_val - post_peak_min >= 2:
                state = 'O2_反弹失败'
        if not state and za_max >= -3:
            state = 'O3_一刀两断'
        if not state:
            # O4: M头
            if za_mean >= 0:
                state = 'O4_M头逃命'
        if not state:
            # O5: 温水煮青蛙
            if lian_yin >= 3 and pr > -2:
                state = 'O5_温水煮青蛙'
        if not state:
            state = 'O6_其他_其他跌破'
    else:
        state = '零轴'

    # 提取编号
    sid = state.split('_')[0] if state and '_' in state else state
    return state, sid


# ========== 二、批量处理 ==========
def process_files(max_files=500):
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    files = files[:max_files] if len(files) > max_files else files
    print(f"处理 {len(files)} 个文件, 预期 ~{len(files)*1500:,} 行")

    all_rows = []
    t0 = time.time()

    for fi, f in enumerate(files):
        try:
            df = pd.read_csv(f, encoding='gbk')
            if COL_ZA not in df.columns or len(df) < 50: continue

            # 预计算等高线
            df['等高线'] = df.apply(lambda r: classify_等高线(r[COL_ZA], r[COL_MID]), axis=1)

            # 日冲22需要逐行处理（因为有历史/未来依赖）
            for i in range(len(df)):
                row = df.iloc[i]

                # 获取历史行（倒序，最近的在最后）
                prev_rows = []
                for j in range(i-1, max(i-10, -1), -1):
                    prev_rows.append(df.iloc[j])

                # 获取未来行
                next_rows = []
                for j in range(i+1, min(i+16, len(df))):
                    next_rows.append(df.iloc[j])

                state, sid = classify_日冲22(row, prev_rows, next_rows)
                df.at[df.index[i], '日冲22态'] = state
                df.at[df.index[i], '日冲22编号'] = sid

            all_rows.append(df)

            if (fi+1) % 50 == 0:
                elapsed = time.time() - t0
                print(f"  已处理 {fi+1}/{len(files)} ({elapsed:.0f}s, ~{elapsed/(fi+1):.1f}s/file)")
        except Exception as e:
            print(f"  错误 {f}: {e}")

    data = pd.concat(all_rows, ignore_index=True)
    print(f"\n总样本: {len(data):,} 行, {time.time()-t0:.0f}s")
    return data

# 运行
print("="*80)
print("日冲22态 vs 日层等高线 同数据对比分析")
print("="*80)
data = process_files(max_files=500)
print(f"最终样本: {len(data):,} 行")

# 清洗
data = data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
data = data[data['日冲22编号'] != 'NA']
print(f"清洗后: {len(data):,} 行")

# ========== 三、分类分布 ==========
print("\n" + "="*80)
print("一、各分类分布")
print("="*80)
print("\n--- 日冲22态分布 ---")
state_counts = data['日冲22编号'].value_counts()
for s, c in state_counts.items():
    print(f"  {s:>20}: {c:>8,} ({c/len(data)*100:>5.1f}%)")

print("\n--- 等高线分布 ---")
dg_counts = data['等高线'].value_counts()
for s, c in dg_counts.items():
    print(f"  {s:>8}: {c:>10,} ({c/len(data)*100:>5.1f}%)")

# ========== 四、下日冲高概率对比 ==========
print("\n" + "="*80)
print("二、下日冲高≥3% 概率对比")
print("="*80)

# 等高线
print("\n--- 等高线 ---")
print(f"{'分类':>8} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'P(≥2%)':>8} | {'平均冲高':>8}")
print("-"*55)
for c in ['等1','等2','等3','等4','等5','等6','等7','等8','零轴']:
    sub = data[data['等高线']==c]
    if len(sub) < 200: continue
    nh = sub[COL_NEXT].dropna()
    if len(nh) < 200: continue
    print(f"{c:>8} | {len(sub):>8,} | {(nh>3).mean():>7.1%} | {(nh>5).mean():>7.1%} | {(nh>2).mean():>7.1%} | {nh.mean():>6.2f}%")

# 日冲22态
print("\n--- 日冲22态 ---")
print(f"{'分类':>20} | {'样本':>8} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'P(≥2%)':>8} | {'平均冲高':>8}")
print("-"*70)
# 按P(≥3%)降序
state_results = []
for s in state_counts.index:
    sub = data[data['日冲22编号']==s]
    if len(sub) < 50: continue
    nh = sub[COL_NEXT].dropna()
    if len(nh) < 50: continue
    p3 = (nh>3).mean()
    state_results.append((s, len(sub), p3, (nh>5).mean(), (nh>2).mean(), nh.mean()))
state_results.sort(key=lambda x: -x[2])
for s,n,p3,p5,p2,avg in state_results:
    print(f"{s:>20} | {n:>8,} | {p3:>7.1%} | {p5:>7.1%} | {p2:>7.1%} | {avg:>6.2f}%")

# ========== 五、交叉表 ==========
print("\n" + "="*80)
print("三、交叉表：等高线 × 日冲22态 → P(≥3%)")
print("（等高线内部子分类的区分度 = 等高线是否完全替代日冲22的关键）")
print("="*80)

# 按等高线分组
dg_cats = ['等1','等2','等3','等4','等5','等6','等7','等8']
for c in dg_cats:
    sub = data[data['等高线']==c]
    if len(sub) < 500: continue
    print(f"\n--- {c} (n={len(sub):,}) ---")
    sub_states = sub.groupby('日冲22编号')[COL_NEXT].agg(['count', lambda x: (x>3).mean(), lambda x: (x>5).mean(), 'mean'])
    sub_states.columns = ['样本', 'P(≥3%)', 'P(≥5%)', '平均冲高']
    # 过滤小样本
    sub_states = sub_states[sub_states['样本']>=30]
    sub_states = sub_states.sort_values('P(≥3%)', ascending=False)
    print(f"{'日冲22态':>12} | {'样本':>6} | {'P(≥3%)':>8} | {'P(≥5%)':>8} | {'平均冲高':>8}")
    print("-"*55)
    for s, r in sub_states.iterrows():
        print(f"{s:>12} | {r['样本']:>6,} | {r['P(≥3%)']:>7.1%} | {r['P(≥5%)']:>7.1%} | {r['平均冲高']:>6.2f}%")
    # 加总
    nh = sub[COL_NEXT].dropna()
    print(f"{'等高线总':>12} | {len(nh):>6,} | {(nh>3).mean():>7.1%} | {(nh>5).mean():>7.1%} | {nh.mean():>6.2f}%")
    # 极差
    if len(sub_states) >= 2:
        p3_vals = sub_states['P(≥3%)'].values
        print(f"  → 内部极差: {p3_vals.max()-p3_vals.min():.1%} (最高{max(p3_vals):.1%} vs 最低{min(p3_vals):.1%})")

# ========== 六、等高线丢失率分析 ==========
print("\n" + "="*80)
print("四、等高线丢失率：等高线最佳 vs 日冲22最佳")
print("（等高线内最高P(≥3%)是否接近日冲22全局最高？）")
print("="*80)

# 等高线全局最佳
nh_all = data[COL_NEXT].dropna()
print(f"\n全局基准: P(≥3%) = {(nh_all>3).mean():.1%} (n={len(nh_all):,})")

# 等高线最佳
best_dg = ''; best_dg_p3 = 0
for c in dg_cats:
    sub = data[data['等高线']==c]
    nh = sub[COL_NEXT].dropna()
    p3 = (nh>3).mean()
    if p3 > best_dg_p3: best_dg_p3 = p3; best_dg = c
print(f"等高线最佳: {best_dg} P(≥3%) = {best_dg_p3:.1%}")

# 日冲22最佳（排除小样本）
best_st = ''; best_st_p3 = 0
for s, n, p3, p5, p2, avg in state_results:
    if n >= 100 and p3 > best_st_p3:
        best_st_p3 = p3; best_st = s
print(f"日冲22最佳: {best_st} P(≥3%) = {best_st_p3:.1%} (n={[r[1] for r in state_results if r[0]==best_st][0]:,})")
print(f"差异: 日冲22最佳 - 等高线最佳 = {best_st_p3-best_dg_p3:.1%}")

# 日冲22前5 vs 等高线各分类
print(f"\n--- 日冲22前5（按P(≥3%)，样本≥100） ---")
for s, n, p3, p5, p2, avg in state_results[:5]:
    if n < 100: continue
    # 这个状态属于哪个等高线？
    sub = data[data['日冲22编号']==s]
    top_dg = sub['等高线'].value_counts().index[0]
    dg_p3 = (data[data['等高线']==top_dg][COL_NEXT].dropna()>3).mean()
    print(f"  {s:>12}: 自身P(≥3%)={p3:.1%} (n={n:,}) → 等高线归入{top_dg} (P(≥3%)={dg_p3:.1%}) → 丢失{(p3-dg_p3)*100:.1f}pp")

# ========== 七、等高线内最大区分度 ==========
print("\n" + "="*80)
print("五、等高线内部最大区分度（等高线内最高 vs 最低日冲22态）")
print("如果内部极差大 → 等高线不够细，日冲22有额外价值")
print("="*80)
print(f"{'等高线':>8} | {'样本':>8} | {'内部极差':>8} | {'最高态':>12} | {'最高P(≥3%)':>10} | {'最低态':>12} | {'最低P(≥3%)':>10}")
print("-"*75)
for c in dg_cats:
    sub = data[data['等高线']==c]
    if len(sub) < 500: continue
    sub_states = sub.groupby('日冲22编号')[COL_NEXT].agg(['count', lambda x: (x>3).mean()])
    sub_states = sub_states[sub_states['count']>=30]
    if len(sub_states) < 2: continue
    p3_vals = sub_states['<lambda_0>'].values
    max_s = sub_states['<lambda_0>'].idxmax()
    min_s = sub_states['<lambda_0>'].idxmin()
    print(f"{c:>8} | {len(sub):>8,} | {p3_vals.max()-p3_vals.min():>7.1%} | {max_s:>12} | {p3_vals.max():>9.1%} | {min_s:>12} | {p3_vals.min():>9.1%}")

print(f"\n{'='*80}")
print("结论：等高线 vs 日冲22 对比完成")
print(f"{'='*80}")