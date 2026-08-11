# -*- coding: utf-8 -*-
"""
三级别框架验证 - 修正版
核心指标: 下日DSHR>2 (次日冲高≥2%概率)
而不是 →ZE>0 (续站DJE概率, 已由DXEF决定)
"""
import csv

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

data = {}
for r in rows:
    data[(r['DXEF'], r['DXCD'], r['DXAB'])] = {
        'ze': float(r['→ZE>0']),
        'ds1': float(r['下日DSHR>1']),
        'ds2': float(r['下日DSHR>2']),
        'n': int(r['样本']),
    }

def get(ef, cd, ab):
    return data.get((ef, cd, ab))

EF_G = ['金','银','唏']
EF_B = ['嘘','尿','屎']
CD_G = ['上','中','忐']
CD_B = ['下','忠',chr(0x5FD1)]
AB_G = ['上','中','忐']
AB_B = ['下','忠',chr(0x5FD1)]
ALL_AB = ['上','中','下','忐','忠',chr(0x5FD1)]

lines = []
def pr(s=""):
    lines.append(s)

# ====== 8种组合 - 用DSHR>2 ======
pr("=" * 80)
pr("三级别分类系统: 8种组合 (指标: 下日DSHR>2)")
pr("=" * 80)
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

pr(f"{'组合':>30} {'等级':>6} {'平均DS2':>8} {'最低DS2':>8} {'最高DS2':>8} {'DS2≥30%':>8} {'DS2≥25%':>8} {'分支':>6}")
pr("-" * 90)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    vals.append(d['ds2'])
    if vals:
        avg = sum(vals)/len(vals)
        mn = min(vals)
        mx = max(vals)
        ge_30 = sum(1 for v in vals if v >= 30)
        ge_25 = sum(1 for v in vals if v >= 25)
        pr(f"{cname:>30} {grade:>6} {avg:>7.1f}% {mn:>7.1f}% {mx:>7.1f}% {ge_30:>5}/{len(vals)} {ge_25:>5}/{len(vals)} {len(vals):>6}")

# ====== 规则A: 金银唏+上中忐+不限DXAB (DSHR>2视角) ======
pr("")
pr("=" * 80)
pr("规则A: 金银唏+上中忐+不限DXAB (指标: 下日DSHR>2)")
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
            ds2_vals = {k: v['ds2'] for k, v in vals.items()}
            ze_vals = {k: v['ze'] for k, v in vals.items()}
            mn_ds2 = min(ds2_vals.values())
            mx_ds2 = max(ds2_vals.values())
            mn_ab = min(ds2_vals, key=ds2_vals.get)
            mn_ze = min(ze_vals.values())
            pr(f"{ef}/{cd}: DS2范围={mn_ds2:.1f}~{mx_ds2:.1f}%, 最低DS2在AB={mn_ab}, 最低ZE={mn_ze:.1f}%")
            for ab, d in vals.items():
                pr(f"  {ab} DS2={d['ds2']:>5.1f}%  DS1={d['ds1']:>5.1f}%  ZE={d['ze']:>5.1f}%  样本={d['n']:>8,}")

# ====== 规则B: 嘘尿屎+上忠忐+不限DXAB (DSHR>2视角) ======
pr("")
pr("=" * 80)
pr("规则B: 嘘尿屎+上忠忐+不限DXAB (指标: 下日DSHR>2)")
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
            ds2_vals = {k: v['ds2'] for k, v in vals.items()}
            mn_ds2 = min(ds2_vals.values())
            mx_ds2 = max(ds2_vals.values())
            mn_ab = min(ds2_vals, key=ds2_vals.get)
            lt_25 = sum(1 for v in ds2_vals.values() if v < 25)
            pr(f"{ef}/{cd}: DS2={mn_ds2:.1f}~{mx_ds2:.1f}%, 最低AB={mn_ab}, <25%={lt_25}/6")
            for ab, d in vals.items():
                tag = " <---" if d['ds2'] < 25 else ""
                pr(f"  {ab} DS2={d['ds2']:>5.1f}%  DS1={d['ds1']:>5.1f}%  ZE={d['ze']:>5.1f}%  样本={d['n']:>8,}{tag}")

# ====== 规则C: 嘘尿屎+下忠忑+甲乙己 (DSHR>2视角) ======
pr("")
pr("=" * 80)
pr("规则C: 嘘尿屎+下忠忑+甲乙己 (指标: 下日DSHR>2)")
pr("=" * 80)
pr("")

for ef in EF_B:
    for cd in CD_B:
        pr(f"\n{ef}/{cd}:")
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d:
                tag = " <---" if d['ds2'] < 25 else ""
                pr(f"  {ab} DS2={d['ds2']:>5.1f}%  DS1={d['ds1']:>5.1f}%  ZE={d['ze']:>5.1f}%  样本={d['n']:>8,}{tag}")

# ====== 镜面对称: 金银唏+上忠忐忑 (DSHR>2视角) ======
pr("")
pr("=" * 80)
pr("镜面对称: 金银唏+上忠忐 甲乙己 vs 丙丁戊 (指标: 下日DSHR>2)")
pr("=" * 80)
pr("")

for ef in EF_G:
    for cd in CD_G:
        qiang = {}
        ruo = {}
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                if ab in AB_G:
                    qiang[ab] = d['ds2']
                else:
                    ruo[ab] = d['ds2']
        if qiang and ruo:
            q_avg = sum(qiang.values())/len(qiang)
            r_avg = sum(ruo.values())/len(ruo)
            q_min = min(qiang.values())
            r_min = min(ruo.values())
            q_ab = min(qiang, key=qiang.get)
            r_ab = min(ruo, key=ruo.get)
            pr(f"{ef}/{cd}:")
            pr(f"  甲乙己: avg={q_avg:.1f}%, min={q_min:.1f}%({q_ab})")
            pr(f"  丙丁戊: avg={r_avg:.1f}%, min={r_min:.1f}%({r_ab})")
            pr(f"  差距: {q_avg - r_avg:.1f}pp")

# ====== 关键对比: →ZE>0 vs DSHR>2 的区分度差异 ======
pr("")
pr("=" * 80)
pr("核心对比: →ZE>0 vs DSHR>2 在8格中的区分度")
pr("=" * 80)
pr("")
pr(f"{'组合':>30} {'等级':>6} {'ZE平均':>8} {'ZE最低':>8} {'DS2平均':>8} {'DS2最低':>8} {'ZE极差':>8} {'DS2极差':>8}")
pr("-" * 90)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    ze_vals = []
    ds2_vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    ze_vals.append(d['ze'])
                    ds2_vals.append(d['ds2'])
    if ze_vals and ds2_vals:
        ze_avg = sum(ze_vals)/len(ze_vals)
        ze_min = min(ze_vals)
        ds2_avg = sum(ds2_vals)/len(ds2_vals)
        ds2_min = min(ds2_vals)
        ze_range = ze_avg - ze_min
        ds2_range = ds2_avg - ds2_min
        pr(f"{cname:>30} {grade:>6} {ze_avg:>7.1f}% {ze_min:>7.1f}% {ds2_avg:>7.1f}% {ds2_min:>7.1f}% {ze_range:>7.1f}pp {ds2_range:>7.1f}pp")

# ====== 关键发现: DSHR>2不随DXEF单调变化 ======
pr("")
pr("=" * 80)
pr("关键发现: DSHR>2 不随 DXEF 单调变化")
pr("一些→ZE>0很低的分支, DSHR>2反而很高")
pr("=" * 80)
pr("")

# 找出DSHR>2高但→ZE>0低的组合
pr("DSHR>2 >= 30% 但 →ZE>0 < 30% 的分支:")
pr(f"{'EF':>4} {'CD':>4} {'AB':>4} {'DS2':>6} {'DS1':>6} {'ZE':>6} {'样本':>10}")
pr("-" * 45)
for ef in ['金','银','唏','嘘','尿','屎']:
    for cd in ['上','中','下','忐','忠',chr(0x5FD1)]:
        for ab in ['上','中','下','忐','忠',chr(0x5FD1)]:
            d = get(ef, cd, ab)
            if d and d['ds2'] >= 30 and d['ze'] < 30:
                pr(f"{ef:>4} {cd:>4} {ab:>4} {d['ds2']:>5.1f}% {d['ds1']:>5.1f}% {d['ze']:>5.1f}% {d['n']:>10,}")

pr("")
pr("DSHR>2 < 25% 但 →ZE>0 > 50% 的分支:")
pr(f"{'EF':>4} {'CD':>4} {'AB':>4} {'DS2':>6} {'DS1':>6} {'ZE':>6} {'样本':>10}")
pr("-" * 45)
for ef in ['金','银','唏','嘘','尿','屎']:
    for cd in ['上','中','下','忐','忠',chr(0x5FD1)]:
        for ab in ['上','中','下','忐','忠',chr(0x5FD1)]:
            d = get(ef, cd, ab)
            if d and d['ds2'] < 25 and d['ze'] > 50:
                pr(f"{ef:>4} {cd:>4} {ab:>4} {d['ds2']:>5.1f}% {d['ds1']:>5.1f}% {d['ze']:>5.1f}% {d['n']:>10,}")

# ====== DSHR>2 的DXEF战场平均 ======
pr("")
pr("=" * 80)
pr("DXEF战场平均DSHR>2 (看战场本身是否决定冲高)")
pr("=" * 80)
pr("")
for ef in ['金','银','唏','嘘','尿','屎']:
    vals = []
    for cd in ['上','中','下','忐','忠',chr(0x5FD1)]:
        for ab in ['上','中','下','忐','忠',chr(0x5FD1)]:
            d = get(ef, cd, ab)
            if d:
                vals.append(d['ds2'])
    if vals:
        avg = sum(vals)/len(vals)
        mn = min(vals)
        mx = max(vals)
        pr(f"{ef}: DS2平均={avg:.1f}%, 范围={mn:.1f}~{mx:.1f}%")

with open('____temp/三级别框架验证_DSHR视角.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done!")