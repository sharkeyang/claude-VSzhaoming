# -*- coding: utf-8 -*-
"""
三级别分类系统框架验证
"""
import csv, json

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

data = {}
for r in rows:
    data[(r['DXEF'], r['DXCD'], r['DXAB'])] = {
        'ze': float(r['→ZE>0']), 'zc': float(r['→ZE>0+ZC>0']),
        'za': float(r['→ZE>0+ZC>0+ZA>0']), 'ds2': float(r['下日DSHR>2']), 'n': int(r['样本']),
    }

def get(ef, cd, ab):
    return data.get((ef, cd, ab))

EF_G = ['金','银','唏']
EF_B = ['嘘','尿','屎']
CD_G = ['上','中','忐']
CD_B = ['下','忠',chr(0x5FD1)]  # 忑
AB_G = ['上','中','忐']
AB_B = ['下','忠',chr(0x5FD1)]

ALL_AB = ['上','中','下','忐','忠',chr(0x5FD1)]

lines = []

def pr(s=""):
    lines.append(s)

# ====== 8种组合全量分析 ======
pr("=" * 80)
pr("三级别分类系统: 8种组合全量数据")
pr("=" * 80)
pr("")
pr("DXEF分类: 甲乙己=金银唏, 丙丁戊=嘘尿屎")
pr("DXCD分类: 甲乙己=上中忐, 丙丁戊=下忠忑")
pr("DXAB分类: 甲乙己=上中忐, 丙丁戊=下忠忑")
pr("")

combos = [
    ("S级: 金银唏+上中忐+上中忐",  EF_G, CD_G, AB_G),
    ("A级: 金银唏+上中忐+下忠忑",  EF_G, CD_G, AB_B),
    ("B级: 金银唏+下忠忑+上中忐",  EF_G, CD_B, AB_G),
    ("C级: 金银唏+下忠忑+下忠忑",  EF_G, CD_B, AB_B),
    ("D级: 嘘尿屎+上中忐+上中忐",  EF_B, CD_G, AB_G),
    ("E级: 嘘尿屎+上中忐+下忠忑",  EF_B, CD_G, AB_B),
    ("F级: 嘘尿屎+下忠忑+上中忐",  EF_B, CD_B, AB_G),
    ("禁止: 嘘尿屎+下忠忑+下忠忑", EF_B, CD_B, AB_B),
]

for cname, efs, cds, abs_list in combos:
    vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    vals.append(d)
    if vals:
        ze_vals = [v['ze'] for v in vals]
        n_vals = [v['n'] for v in vals]
        avg = sum(ze_vals)/len(ze_vals)
        mn = min(ze_vals)
        mx = max(ze_vals)
        total_n = sum(n_vals)
        # 统计各区间
        gt_50 = sum(1 for v in ze_vals if v >= 50)
        gt_30 = sum(1 for v in ze_vals if v >= 30)
        lt_10 = sum(1 for v in ze_vals if v < 10)
        pr(f"{cname}")
        pr(f"  分支: {len(vals):>3}, 总样本: {total_n:>12,}")
        pr(f"  平均: {avg:>5.1f}%, 范围: {mn:.1f}~{mx:.1f}%")
        pr(f"  >=50%: {gt_50:>2}/{len(vals)}, >=30%: {gt_30:>2}/{len(vals)}, <10%: {lt_10:>2}/{len(vals)}")
        pr("")

# ====== 用户规则A: 金银唏+上中忐+不限DXAB ======
pr("=" * 80)
pr("规则A: 金银唏(DXEF>0) + 上中忐(DXCD) + 不限DXAB")
pr("=" * 80)
pr("")

for ef in EF_G:
    for cd in CD_G:
        vals = {}
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                vals[ab] = d
        if vals:
            ze_vals = {k: v['ze'] for k, v in vals.items()}
            mn = min(ze_vals.values())
            mx = max(ze_vals.values())
            rng = mx - mn
            mn_ab = min(ze_vals, key=ze_vals.get)
            pr(f"{ef}/{cd}: range={rng:.1f}pp, min={mn:.1f}%({mn_ab}), max={mx:.1f}%")
            for ab, d in vals.items():
                pr(f"  {ab} ->ZE>0={d['ze']:>6.1f}%  ->ZE+ZC={d['zc']:>6.1f}%  DSHR>2={d['ds2']:>5.1f}%  样本={d['n']:>8,}")

# ====== 用户规则B: 嘘尿屎+上忠忐+不限DXAB ======
pr("")
pr("=" * 80)
pr("规则B: 嘘尿屎(DXEF<0) + 上忠忐(DXCD) + 不限DXAB")
pr("=" * 80)
pr("")

for ef in EF_B:
    for cd in CD_G:
        vals = {}
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                vals[ab] = d
        if vals:
            ze_vals = {k: v['ze'] for k, v in vals.items()}
            mn = min(ze_vals.values())
            mx = max(ze_vals.values())
            rng = mx - mn
            mn_ab = min(ze_vals, key=ze_vals.get)
            lt_10 = sum(1 for v in ze_vals.values() if v < 10)
            all_ge_10 = all(v >= 10 for v in ze_vals.values())
            pr(f"{ef}/{cd}: range={rng:.1f}pp, min={mn:.1f}%({mn_ab}), max={mx:.1f}%, <10%={lt_10}/6 -> {'有效' if all_ge_10 else '无效'}")
            for ab, d in vals.items():
                tag = " <---" if d['ze'] < 10 else ""
                pr(f"  {ab} ->ZE>0={d['ze']:>6.1f}%  ->ZE+ZC={d['zc']:>6.1f}%  DSHR>2={d['ds2']:>5.1f}%  样本={d['n']:>8,}{tag}")

# ====== 用户规则C: 嘘尿屎+下忠忑+甲乙己 ======
pr("")
pr("=" * 80)
pr("规则C: 嘘尿屎(DXEF<0) + 下忠忑(DXCD) + 甲乙己(DXAB)")
pr("=" * 80)
pr("")

for ef in EF_B:
    for cd in CD_B:
        vals = []
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d:
                vals.append((ab, d))
        if vals:
            ze_vals = {k: v['ze'] for k, v in vals}
            mn = min(ze_vals.values())
            mx = max(ze_vals.values())
            mn_ab = min(ze_vals, key=ze_vals.get)
            pr(f"{ef}/{cd}: min={mn:.1f}%({mn_ab}), max={mx:.1f}%")
            for ab, d in vals:
                tag = " <---" if d['ze'] < 30 else ""
                pr(f"  {ab} ->ZE>0={d['ze']:>6.1f}%  ->ZE+ZC={d['zc']:>6.1f}%  样本={d['n']:>8,}{tag}")

# ====== 镜面对称: 金银唏+上忠忐 ======
pr("")
pr("=" * 80)
pr("镜面对称: 金银唏+上忠忐 不限DXAB vs 甲乙己优先")
pr("=" * 80)
pr("")

for ef in EF_G:
    for cd in CD_G:
        qiang_vals = {}
        ruo_vals = {}
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                if ab in AB_G:
                    qiang_vals[ab] = d['ze']
                else:
                    ruo_vals[ab] = d['ze']
        if qiang_vals and ruo_vals:
            q_avg = sum(qiang_vals.values())/len(qiang_vals)
            r_avg = sum(ruo_vals.values())/len(ruo_vals)
            q_min = min(qiang_vals.values())
            r_min = min(ruo_vals.values())
            q_ab = min(qiang_vals, key=qiang_vals.get)
            r_ab = min(ruo_vals, key=ruo_vals.get)
            pr(f"{ef}/{cd}:")
            pr(f"  甲乙己: avg={q_avg:.1f}%, min={q_min:.1f}%({q_ab})")
            pr(f"  丙丁戊: avg={r_avg:.1f}%, min={r_min:.1f}%({r_ab})")
            pr(f"  差距: {q_avg - r_avg:.1f}pp")

# ====== 最终框架建议 ======
pr("")
pr("=" * 80)
pr("框架建议: 三级别甲乙己/丙丁戊分类系统")
pr("=" * 80)
pr("")

# 框架层级
pr("第1层(DXEF): 战场方向")
pr("  甲乙己(金银唏) -> 允许多头操作")
pr("  丙丁戊(嘘尿屎) -> 限制性操作, 需下两层补偿")
pr("")
pr("第2层(DXCD): 操作时机")
pr("  甲乙己(上中忐) -> 时机有利, 可操作")
pr("  丙丁戊(下忠忑) -> 时机不利, 需第3层补偿")
pr("")
pr("第3层(DXAB): 护型质量")
pr("  甲乙己(上中忐) -> 护型强, 安全边际高")
pr("  丙丁戊(下忠忑) -> 护型弱, 仅上层有利时可用")
pr("")

# 8格表
pr("8格决策表:")
pr("")
pr(f"{'DXEF':>8} {'DXCD':>8} {'DXAB':>8} {'等级':>6} {'平均->ZE>0':>12} {'最低->ZE>0':>12} {'操作建议':>16}")
pr("-" * 72)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    vals.append(d['ze'])
    if vals:
        avg = sum(vals)/len(vals)
        mn = min(vals)
        if avg >= 80:
            advice = "优先参与"
        elif avg >= 60:
            advice = "正常参与"
        elif avg >= 40:
            advice = "谨慎参与"
        elif avg >= 20:
            advice = "小仓试错"
        else:
            advice = "禁止操作"
        ef_label = "金银唏" if efs == EF_G else "嘘尿屎"
        cd_label = "上中忐" if cds == CD_G else "下忠忑"
        ab_label = "上中忐" if abs_list == AB_G else "下忠忑"
        pr(f"{ef_label:>8} {cd_label:>8} {ab_label:>8} {grade:>6} {avg:>10.1f}% {mn:>10.1f}% {advice:>16}")

# 规则的例外
pr("")
pr("=" * 80)
pr("规则的例外与精细化调整")
pr("=" * 80)
pr("")
pr("例外1: 金银唏+上忠忐+下忠忑 中, 金/上+下忠忑 全都>98% -> 不必限制")
pr("例外2: 金银唏+上忠忐+下忠忑 中, 唏/中+下忠忑 最低54.6% -> 可操作但谨慎")
pr("例外3: 嘘尿屎+下忠忑+甲乙己 中, 只有CD=中有效, CD=下/忑无效")
pr("例外4: 嘘尿屎+上忠忐 中, 嘘/忠/下=8.6%, 尿/忠全体<15%, 屎/忠全体<5%")

with open('____temp/三级别分类框架验证.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done - saved to ____temp/三级别分类框架验证.md")