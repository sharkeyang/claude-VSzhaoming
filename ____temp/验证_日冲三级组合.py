"""
日冲策略三级组合验证脚本
验证用户提出的4个假设，基于216分支全量概率表(2000万样本)

用户假设:
1. 嘘尿屎 + 忑中下 + 丙丁戊 → 应禁止
2. 嘘尿屎 + 忑中下 → 只有甲乙己可尝试
3. 嘘尿屎 + 忐忠上 → 无论三级是什么都可参与
4. 金银唏 + 上忐忠 → 都要参与，特别是甲乙己

DXAB→护型映射:
  上→甲, 中→乙, 下→丙, 忐→己, 忠→丁, 忑→戊
  甲乙己(强护型)=上/中/忐, 丙丁戊(弱护型)=下/忠/忑
"""

import csv
import io
from collections import defaultdict

# 读取CSV
with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"总行数: {len(rows)}")
print("="*100)

# 护型映射
DXAB_TO_HU = {
    '上': '甲(强)', '中': '乙(强)', '忐': '己(强)',
    '下': '丙(弱)', '忠': '丁(弱)', '忑': '戊(弱)'
}
QIANG = ['上', '中', '忐']  # 甲乙己
RUO = ['下', '忠', '忑']    # 丙丁戊

# 构建查询结构
data = {}
for r in rows:
    key = (r['DXEF'], r['DXCD'], r['DXAB'])
    data[key] = {
        '→ZE>0': float(r['→ZE>0']),
        '→ZE+ZC': float(r['→ZE>0+ZC>0']),
        '→ZE+ZC+ZA': float(r['→ZE>0+ZC>0+ZA>0']),
        'DSHR>0': float(r['下日DSHR>0']),
        'DSHR>1': float(r['下日DSHR>1']),
        'DSHR>2': float(r['下日DSHR>2']),
        '均HR': float(r['均HR']) if r['均HR'] else 0,
        '中位HR': float(r['中位HR']) if r['中位HR'] else 0,
        '样本': int(r['样本']),
    }

def get(ef, cd, ab):
    return data.get((ef, cd, ab), None)

def fmt(d):
    if d is None:
        return "N/A"
    return f"{d:.1f}%"

# ============================================================
# 假设1: 嘘尿屎 + 忑中下 + 丙丁戊 → 应禁止
# ============================================================
print("\n" + "="*100)
print("假设1: 嘘尿屎 + 忑中下 + 丙丁戊 → 应禁止？")
print("="*100)

EF_BAD = ['嘘', '尿', '屎']
CD_BAD = ['忑', '中', '下']

print(f"\n{'DXEF':>4} {'DXCD':>4} {'DXAB':>4} {'护型':>8} {'→ZE>0':>8} {'→ZE+ZC':>8} {'→ZE+ZC+ZA':>8} {'DSHR>2':>8} {'样本':>8}")
print("-"*70)

total_samples = 0
count_bad = 0
ze_sum = 0
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in RUO:
            d = get(ef, cd, ab)
            if d:
                print(f"{ef:>4} {cd:>4} {ab:>4} {DXAB_TO_HU[ab]:>8} {fmt(d['→ZE>0']):>8} {fmt(d['→ZE+ZC']):>8} {fmt(d['→ZE+ZC+ZA']):>8} {fmt(d['DSHR>2']):>8} {d['样本']:>8,}")
                total_samples += d['样本']
                count_bad += 1
                ze_sum += d['→ZE>0']

avg_ze = ze_sum / count_bad if count_bad else 0
print(f"\n共{count_bad}个分支，{total_samples:,}样本，平均→ZE>0={avg_ze:.1f}%")
print()

# 对比：同样的嘘尿屎+忑中下，但甲乙己
print("--- 对比：嘘尿屎 + 忑中下 + 甲乙己(强护型) ---")
print(f"{'DXEF':>4} {'DXCD':>4} {'DXAB':>4} {'护型':>8} {'→ZE>0':>8} {'→ZE+ZC':>8} {'→ZE+ZC+ZA':>8} {'DSHR>2':>8} {'样本':>8}")
print("-"*70)

count_strong = 0
ze_sum_strong = 0
sample_strong = 0
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d:
                print(f"{ef:>4} {cd:>4} {ab:>4} {DXAB_TO_HU[ab]:>8} {fmt(d['→ZE>0']):>8} {fmt(d['→ZE+ZC']):>8} {fmt(d['→ZE+ZC+ZA']):>8} {fmt(d['DSHR>2']):>8} {d['样本']:>8,}")
                count_strong += 1
                ze_sum_strong += d['→ZE>0']
                sample_strong += d['样本']

avg_ze_strong = ze_sum_strong / count_strong if count_strong else 0
print(f"\n甲乙己组: 共{count_strong}个分支，{sample_strong:,}样本，平均→ZE>0={avg_ze_strong:.1f}%")
print(f"丙丁戊组: 共{count_bad}个分支，{total_samples:,}样本，平均→ZE>0={avg_ze:.1f}%")
print(f"差距: {avg_ze_strong - avg_ze:.1f}pp")

# ============================================================
# 假设2: 嘘尿屎 + 忑中下 → 只有甲乙己可尝试
# ============================================================
print("\n" + "="*100)
print("假设2: 嘘尿屎 + 忑中下 → 只有甲乙己可尝试？")
print("="*100)

print(f"\n按DXAB护型分组对比:")
print(f"{'DXAB组':>8} {'分支数':>6} {'样本':>10} {'平均→ZE>0':>10} {'→ZE>0≥50%':>10} {'→ZE>0≥30%':>10} {'→ZE>0<10%':>10}")
print("-"*65)

for group_name, ab_list in [('甲乙己', QIANG), ('丙丁戊', RUO)]:
    total_s = 0
    over_50 = 0
    over_30 = 0
    under_10 = 0
    ze_vals = []
    for ef in EF_BAD:
        for cd in CD_BAD:
            for ab in ab_list:
                d = get(ef, cd, ab)
                if d:
                    total_s += d['样本']
                    ze = d['→ZE>0']
                    ze_vals.append(ze)
                    if ze >= 50: over_50 += 1
                    if ze >= 30: over_30 += 1
                    if ze < 10: under_10 += 1
    avg_ze_group = sum(ze_vals)/len(ze_vals) if ze_vals else 0
    print(f"{group_name:>8} {len(ze_vals):>6} {total_s:>10,} {avg_ze_group:>9.1f}% {over_50:>8} {over_30:>8} {under_10:>8}")

# 具体看哪些分支的甲乙己→ZE>0>50%
print("\n甲乙己中→ZE>0≥50%的分支:")
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d and d['→ZE>0'] >= 50:
                print(f"  {ef}/{cd}/{ab}({DXAB_TO_HU[ab]}) →ZE>0={d['→ZE>0']:.1f}% 样本={d['样本']:,}")

print("\n甲乙己中→ZE>0<30%的分支:")
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d and d['→ZE>0'] < 30:
                print(f"  {ef}/{cd}/{ab}({DXAB_TO_HU[ab]}) →ZE>0={d['→ZE>0']:.1f}% 样本={d['样本']:,}")

# ============================================================
# 假设3: 嘘尿屎 + 忐忠上 → 无论三级是什么都可参与
# ============================================================
print("\n" + "="*100)
print("假设3: 嘘尿屎 + 忐忠上 → 无论三级是什么都可参与？")
print("="*100)

CD_GOOD = ['上', '忠', '忐']

print(f"\n{'DXEF':>4} {'DXCD':>4} {'DXAB':>4} {'护型':>8} {'→ZE>0':>8} {'→ZE+ZC':>8} {'→ZE+ZC+ZA':>8} {'DSHR>2':>8} {'样本':>8}")
print("-"*70)

ze_vals_3 = []
for ef in EF_BAD:
    for cd in CD_GOOD:
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                ze_vals_3.append(d['→ZE>0'])
                print(f"{ef:>4} {cd:>4} {ab:>4} {DXAB_TO_HU[ab]:>8} {fmt(d['→ZE>0']):>8} {fmt(d['→ZE+ZC']):>8} {fmt(d['→ZE+ZC+ZA']):>8} {fmt(d['DSHR>2']):>8} {d['样本']:>8,}")

# 按(ef, cd)分组看极差
print("\n按(EF, CD)分组看极差:")
for ef in EF_BAD:
    for cd in CD_GOOD:
        vals = []
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                vals.append((d['→ZE>0'], ab, d['样本']))
        if vals:
            max_v = max(v[0] for v in vals)
            min_v = min(v[0] for v in vals)
            range_v = max_v - min_v
            # 看有多少个→ZE>0<30%
            low_count = sum(1 for v in vals if v[0] < 30)
            print(f"  {ef}/{cd}: 极差={range_v:.1f}pp, 最低={min_v:.1f}%, 最高={max_v:.1f}%, →ZE>0<30%: {low_count}/{len(vals)}")

# 统计"真正可参与"的门槛
print("\n假设3的可行性判定:")
for ef in EF_BAD:
    for cd in CD_GOOD:
        vals = []
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                vals.append(d)

        # 如果所有DXAB的→ZE>0都≥50%，则"无论什么三级都可参与"
        all_above_50 = all(v['→ZE>0'] >= 50 for v in vals)
        all_above_30 = all(v['→ZE>0'] >= 30 for v in vals)
        all_above_10 = all(v['→ZE>0'] >= 10 for v in vals)
        status = "✅ 全部≥50%可参与" if all_above_50 else \
                 "⚠️ 全部≥30%谨慎参与" if all_above_30 else \
                 "❌ 有分支<10%不可大意" if not all_above_10 else \
                 "⚠️ 全部≥10%但部分<30%"
        print(f"  {ef}/{cd}: {status}")

# ============================================================
# 假设4: 金银唏 + 上忐忠 → 都要参与，特别是甲乙己
# ============================================================
print("\n" + "="*100)
print("假设4: 金银唏 + 上忐忠 → 都要参与，特别是甲乙己")
print("="*100)

EF_GOOD = ['金', '银', '唏']

print(f"\n{'DXEF':>4} {'DXCD':>4} {'DXAB':>4} {'护型':>8} {'→ZE>0':>8} {'→ZE+ZC':>8} {'→ZE+ZC+ZA':>8} {'DSHR>2':>8} {'样本':>8}")
print("-"*70)

for ef in EF_GOOD:
    for cd in CD_GOOD:
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                print(f"{ef:>4} {cd:>4} {ab:>4} {DXAB_TO_HU[ab]:>8} {fmt(d['→ZE>0']):>8} {fmt(d['→ZE+ZC']):>8} {fmt(d['→ZE+ZC+ZA']):>8} {fmt(d['DSHR>2']):>8} {d['样本']:>8,}")

# 按(ef,cd)分组看极差
print("\n按(EF, CD)分组, 甲乙己 vs 丙丁戊对比:")
for ef in EF_GOOD:
    for cd in CD_GOOD:
        qiang_vals = []
        ruo_vals = []
        for ab, group in [('上', '强'), ('中', '强'), ('下', '弱'), ('忐', '强'), ('忠', '弱'), ('忑', '弱')]:
            d = get(ef, cd, ab)
            if d:
                if group == '强':
                    qiang_vals.append(d['→ZE>0'])
                else:
                    ruo_vals.append(d['→ZE>0'])
        if qiang_vals and ruo_vals:
            avg_qiang = sum(qiang_vals)/len(qiang_vals)
            avg_ruo = sum(ruo_vals)/len(ruo_vals)
            min_qiang = min(qiang_vals)
            min_ruo = min(ruo_vals)
            print(f"  {ef}/{cd}: 甲乙己平均={avg_qiang:.1f}% 最低={min_qiang:.1f}% | 丙丁戊平均={avg_ruo:.1f}% 最低={min_ruo:.1f}% | 差={avg_qiang-avg_ruo:.1f}pp")

# ============================================================
# 镜面对称验证: 分类对比
# ============================================================
print("\n" + "="*100)
print("镜面对称验证: 分类边界")
print("="*100)

print("\n四个假设的边界对比:")
print(f"{'条件组':>20} {'分支数':>6} {'平均→ZE>0':>10} {'范围':>20} {'判定':>8}")
print("-"*70)

# A组: 嘘尿屎/忑中下/丙丁戊 (应禁止)
ze_vals_a = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in RUO:
            d = get(ef, cd, ab)
            if d: ze_vals_a.append(d['→ZE>0'])
avg_a = sum(ze_vals_a)/len(ze_vals_a) if ze_vals_a else 0
min_a = min(ze_vals_a) if ze_vals_a else 0
max_a = max(ze_vals_a) if ze_vals_a else 0
print(f"{'A.嘘尿屎/忑中下/丙丁戊':>20} {len(ze_vals_a):>6} {avg_a:>9.1f}% {min_a:.1f}~{max_a:.1f}% {'禁止':>8}")

# B组: 嘘尿屎/忑中下/甲乙己 (可尝试)
ze_vals_b = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d: ze_vals_b.append(d['→ZE>0'])
avg_b = sum(ze_vals_b)/len(ze_vals_b) if ze_vals_b else 0
min_b = min(ze_vals_b) if ze_vals_b else 0
max_b = max(ze_vals_b) if ze_vals_b else 0
print(f"{'B.嘘尿屎/忑中下/甲乙己':>20} {len(ze_vals_b):>6} {avg_b:>9.1f}% {min_b:.1f}~{max_b:.1f}% {'尝试':>8}")

# C组: 嘘尿屎/忐忠上/不限 (可参与)
ze_vals_c = []
for ef in EF_BAD:
    for cd in CD_GOOD:
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d: ze_vals_c.append(d['→ZE>0'])
avg_c = sum(ze_vals_c)/len(ze_vals_c) if ze_vals_c else 0
min_c = min(ze_vals_c) if ze_vals_c else 0
max_c = max(ze_vals_c) if ze_vals_c else 0
print(f"{'C.嘘尿屎/忐忠上/不限':>20} {len(ze_vals_c):>6} {avg_c:>9.1f}% {min_c:.1f}~{max_c:.1f}% {'参与':>8}")

# D组: 金银唏/上忐忠/不限 (应参与)
ze_vals_d = []
for ef in EF_GOOD:
    for cd in CD_GOOD:
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d: ze_vals_d.append(d['→ZE>0'])
avg_d = sum(ze_vals_d)/len(ze_vals_d) if ze_vals_d else 0
min_d = min(ze_vals_d) if ze_vals_d else 0
max_d = max(ze_vals_d) if ze_vals_d else 0
print(f"{'D.金银唏/上忐忠/不限':>20} {len(ze_vals_d):>6} {avg_d:>9.1f}% {min_d:.1f}~{max_d:.1f}% {'参与':>8}")

# E组: 金银唏/上忐忠/甲乙己 (务必参与)
ze_vals_e = []
for ef in EF_GOOD:
    for cd in CD_GOOD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d: ze_vals_e.append(d['→ZE>0'])
avg_e = sum(ze_vals_e)/len(ze_vals_e) if ze_vals_e else 0
min_e = min(ze_vals_e) if ze_vals_e else 0
max_e = max(ze_vals_e) if ze_vals_e else 0
print(f"{'E.金银唏/上忐忠/甲乙己':>20} {len(ze_vals_e):>6} {avg_e:>9.1f}% {min_e:.1f}~{max_e:.1f}% {'优先':>8}")

# F组: 嘘尿屎/忑中下/丙丁戊 中异常值分析
print("\n--- A组(禁止区)中→ZE>0>30%的异常值 ---")
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in RUO:
            d = get(ef, cd, ab)
            if d and d['→ZE>0'] > 30:
                print(f"  ⚠️ {ef}/{cd}/{ab}({DXAB_TO_HU[ab]}) →ZE>0={d['→ZE>0']:.1f}% 样本={d['样本']:,}")

# ============================================================
# 综合结论表
# ============================================================
print("\n" + "="*100)
print("综合结论: 镜面对称验证")
print("="*100)

print("""
假设1: 嘘尿屎 + 忑中下 + 丙丁戊 → 应禁止
  → 数据: 平均→ZE>0={:.1f}%, 范围{:.1f}~{:.1f}%
  → 结论: {} 应禁止. 理由: 平均{:.1f}%的续站概率极低
""".format(avg_a, min_a, max_a,
           "✅ 支持" if avg_a < 20 else "⚠️ 部分支持",
           avg_a))

print("""
假设2: 嘘尿屎 + 忑中下 → 只有甲乙己可尝试
  → 对比: 甲乙己平均{:.1f}% vs 丙丁戊平均{:.1f}%
  → 结论: {}
""".format(avg_b, avg_a,
           "✅ 支持" if avg_b > avg_a + 15 else "⚠️ 部分支持"))

print("""
假设3: 嘘尿屎 + 忐忠上 → 无论三级是什么都可参与
  → 平均→ZE>0={:.1f}%, 范围{:.1f}~{:.1f}%
  → 结论: {}
""".format(avg_c, min_c, max_c,
           "⚠️ 条件不成立" if min_c < 10 else "✅ 支持"))

print("""
假设4: 金银唏 + 上忐忠 → 都要参与,特别是甲乙己
  → 全量平均{:.1f}%, 甲乙己平均{:.1f}%, 范围{:.1f}~{:.1f}%
  → 结论: {}
""".format(avg_d, avg_e, min_e, max_e,
           "✅ 支持" if avg_d > 70 else "⚠️ 部分支持"))

# 四象限对比
print("\n=== 四象限对比 ===")
print(f"{'':>25} {'DXEF=金银唏(好)':>20} {'DXEF=嘘尿屎(差)':>20}")
print(f"{'':>25} {'DXCD=上忐忠(好)':>20} {'DXCD=上忐忠(好)':>20}")
print(f"{'DXCD=中下忑(差)+甲乙己':>25} {avg_e if False else '':>20.1f}% {avg_b:>19.1f}%")
print(f"{'DXCD=中下忑(差)+丙丁戊':>25} {avg_d if False else '':>20.1f}% {avg_a:>19.1f}%")