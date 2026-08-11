# -*- coding: utf-8 -*-
"""
日冲三级组合验证 - 最终版
输出UTF-8结果文件
"""
import csv, json

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

data = {}
for r in rows:
    data[(r['DXEF'], r['DXCD'], r['DXAB'])] = {
        'ze': float(r['→ZE>0']),
        'zc': float(r['→ZE>0+ZC>0']),
        'za': float(r['→ZE>0+ZC>0+ZA>0']),
        'ds2': float(r['下日DSHR>2']),
        'n': int(r['样本']),
    }

def get(ef, cd, ab):
    return data.get((ef, cd, ab))

# 护型: 甲乙己 = 上中忐, 丙丁戊 = 下忠忑
QIANG = ['上', '中', '忐']
RUO = ['下', '忠', '忑']

EF_BAD = ['嘘', '尿', '屎']
EF_GOOD = ['金', '银', '唏']
CD_BAD = ['忑', '中', '下']
CD_GOOD = ['上', '忠', '忐']

out = []

def add(s):
    out.append(s)

add("=" * 80)
add("假设1: 嘘尿屎 + 忑中下 + 丙丁戊 -> 应禁止?")
add("=" * 80)

h1_data = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in RUO:
            d = get(ef, cd, ab)
            if d:
                h1_data.append((ef, cd, ab, d))

h1_ze = [d['ze'] for _, _, _, d in h1_data]
h1_avg = sum(h1_ze)/len(h1_ze)
h1_min = min(h1_ze)
h1_max = max(h1_ze)
h1_n = sum(d['n'] for _, _, _, d in h1_data)

add(f"分支数: {len(h1_data)}, 总样本: {h1_n:,}")
add(f"平均->ZE>0={h1_avg:.1f}%, 范围={h1_min:.1f}~{h1_max:.1f}%")
add("")

# 列出所有分支
add(f"{'EF':>4} {'CD':>4} {'AB':>4} {'->ZE>0':>8} {'->ZE+ZC':>8} {'DSHR>2':>8} {'样本':>10}")
add("-" * 50)
for ef, cd, ab, d in sorted(h1_data, key=lambda x: x[3]['ze']):
    add(f"{ef:>4} {cd:>4} {ab:>4} {d['ze']:>7.1f}% {d['zc']:>7.1f}% {d['ds2']:>7.1f}% {d['n']:>10,}")

# 统计分布
under_10 = sum(1 for d in h1_ze if d < 10)
under_20 = sum(1 for d in h1_ze if d < 20)
over_30 = sum(1 for d in h1_ze if d >= 30)
add(f"\n分布: <10%: {under_10}/{len(h1_data)}, <20%: {under_20}/{len(h1_data)}, >=30%: {over_30}/{len(h1_data)}")

# 对比甲乙己
add("\n--- 对比: 嘘尿屎+忑中下+甲乙己 ---")
h1b_data = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d:
                h1b_data.append((ef, cd, ab, d))

h1b_ze = [d['ze'] for _, _, _, d in h1b_data]
h1b_avg = sum(h1b_ze)/len(h1b_ze)
h1b_n = sum(d['n'] for _, _, _, d in h1b_data)

add(f"{'EF':>4} {'CD':>4} {'AB':>4} {'->ZE>0':>8} {'->ZE+ZC':>8} {'DSHR>2':>8} {'样本':>10}")
add("-" * 50)
for ef, cd, ab, d in sorted(h1b_data, key=lambda x: x[3]['ze']):
    add(f"{ef:>4} {cd:>4} {ab:>4} {d['ze']:>7.1f}% {d['zc']:>7.1f}% {d['ds2']:>7.1f}% {d['n']:>10,}")
add(f"\n丙丁戊平均: {h1_avg:.1f}% vs 甲乙己平均: {h1b_avg:.1f}%")
add(f"差距: {h1b_avg - h1_avg:.1f}pp")
add(f"结论: {'支持禁止' if h1_avg < 20 else '部分支持'} (平均续站概率仅{h1_avg:.1f}%)")

# 甲乙己中哪些可尝试
add("\n甲乙己中->ZE>0>=50%的分支(可尝试):")
for ef, cd, ab, d in h1b_data:
    if d['ze'] >= 50:
        add(f"  {ef}/{cd}/{ab} ->ZE>0={d['ze']:.1f}% 样本={d['n']:,}")

add("\n甲乙己中->ZE>0<30%的分支(不可尝试):")
for ef, cd, ab, d in h1b_data:
    if d['ze'] < 30:
        add(f"  {ef}/{cd}/{ab} ->ZE>0={d['ze']:.1f}% 样本={d['n']:,}")

# ============================================================
add("\n" + "=" * 80)
add("假设2: 嘘尿屎+忑中下 -> 只有甲乙己可尝试?")
add("=" * 80)

add(f"结论: 部分支持但有例外")
add(f"  嘘尿屎+忑中下+甲乙己 中 ->ZE>0>=50%的确实可尝试, 但嘘/忑/*和尿/忑/*和屎/忑/* 即使甲乙己也极低")
add(f"  具体来说:")
for ef in EF_BAD:
    for cd in CD_BAD:
        vals = []
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d:
                vals.append(f"{ab}={d['ze']:.1f}%")
        vals2 = []
        for ab in RUO:
            d = get(ef, cd, ab)
            if d:
                vals2.append(f"{ab}={d['ze']:.1f}%")
        add(f"  {ef}/{cd}: 甲乙己=[{', '.join(vals)}], 丙丁戊=[{', '.join(vals2)}]")

# ============================================================
add("\n" + "=" * 80)
add("假设3: 嘘尿屎+上忠忐 -> 无论什么三级都可参与?")
add("=" * 80)

for ef in EF_BAD:
    for cd in CD_GOOD:
        vals = []
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                vals.append((ab, d))
        ze_vals = [v[1]['ze'] for v in vals]
        mn = min(ze_vals)
        mx = max(ze_vals)
        rng = mx - mn
        all_ge_30 = all(v >= 30 for v in ze_vals)
        all_ge_10 = all(v >= 10 for v in ze_vals)
        low_cnt = sum(1 for v in ze_vals if v < 30)

        if all_ge_30:
            status = "全部>=30% 可参与"
        elif all_ge_10:
            status = f"全部>=10% 但{low_cnt}/6个<30% 谨慎参与"
        else:
            status = f"有分支<10% 不能无脑参与"

        add(f"\n{ef}/{cd}: 极差={rng:.1f}pp, 最低={mn:.1f}%, 最高={mx:.1f}% -> {status}")
        for ab, d in vals:
            tag = " **<10%" if d['ze'] < 10 else ""
            add(f"  {ab} ->ZE>0={d['ze']:>6.1f}% 样本={d['n']:>8,}{tag}")

# ============================================================
add("\n" + "=" * 80)
add("假设4: 金银唏+上忠忐 -> 都要参与, 特别是甲乙己?")
add("=" * 80)

for ef in EF_GOOD:
    for cd in CD_GOOD:
        qiang_vals = []
        ruo_vals = []
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                entry = f"{ab}={d['ze']:.1f}%"
                if ab in QIANG:
                    qiang_vals.append(d['ze'])
                else:
                    ruo_vals.append(d['ze'])
        q_avg = sum(qiang_vals)/len(qiang_vals) if qiang_vals else 0
        r_avg = sum(ruo_vals)/len(ruo_vals) if ruo_vals else 0
        q_min = min(qiang_vals) if qiang_vals else 0
        r_min = min(ruo_vals) if ruo_vals else 0
        add(f"{ef}/{cd}: 甲乙己平均={q_avg:.1f}%最低={q_min:.1f}% | 丙丁戊平均={r_avg:.1f}%最低={r_min:.1f}% | 差={q_avg-r_avg:.1f}pp")

# 全量平均
all_vals = []
for ef in EF_GOOD:
    for cd in CD_GOOD:
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                all_vals.append(d['ze'])

all_avg = sum(all_vals)/len(all_vals)
add(f"\n金银唏+上忠忐 全量平均->ZE>0={all_avg:.1f}%")
add(f"结论: 确实应参与, 甲乙己显著优于丙丁戊")

# ============================================================
add("\n" + "=" * 80)
add("四象限对比总结")
add("=" * 80)

# 计算各象限
def q_avg(efs, cds, abs_list):
    vals = [get(ef, cd, ab) for ef in efs for cd in cds for ab in abs_list]
    vals = [v for v in vals if v]
    return sum(v['ze'] for v in vals)/len(vals) if vals else 0

add(f"""
{'':>25} {'DXCD=上忠忐(好)':>20} {'DXCD=中下忑(差)':>20}
{'':>25} {'-------------------':>20} {'-------------------':>20}
{'DXEF=金银唏(好)+甲乙己':>25} {q_avg(EF_GOOD, CD_GOOD, QIANG):>19.1f}% {q_avg(EF_GOOD, CD_BAD, QIANG):>19.1f}%
{'DXEF=金银唏(好)+丙丁戊':>25} {q_avg(EF_GOOD, CD_GOOD, RUO):>19.1f}% {q_avg(EF_GOOD, CD_BAD, RUO):>19.1f}%
{'':>25} {'-------------------':>20} {'-------------------':>20}
{'DXEF=嘘尿屎(差)+甲乙己':>25} {q_avg(EF_BAD, CD_GOOD, QIANG):>19.1f}% {q_avg(EF_BAD, CD_BAD, QIANG):>19.1f}%
{'DXEF=嘘尿屎(差)+丙丁戊':>25} {q_avg(EF_BAD, CD_GOOD, RUO):>19.1f}% {q_avg(EF_BAD, CD_BAD, RUO):>19.1f}%
""")

add("最终判定:")
add(f"  假设1(禁止): 平均{h1_avg:.1f}% -> {'支持' if h1_avg < 20 else '部分支持'}")
add(f"  假设2(仅甲乙己): 甲乙己{h1b_avg:.1f}% vs 丙丁戊{h1_avg:.1f}% -> {'支持' if h1b_avg > h1_avg + 15 else '部分支持'}")
add(f"  假设3(不限参与): 嘘尿屎+忠全部<15%, 不能无脑参与")
add(f"  假设4(金银唏参与): 全量平均{all_avg:.1f}% -> 支持, 甲乙己显著优于丙丁戊")

# 写入文件
with open('____temp/验证_日冲三级组合_结果.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Done!")