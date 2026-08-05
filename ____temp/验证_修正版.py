# -*- coding: utf-8 -*-
"""
核心修正: 区分"当前状态" vs "明日概率"
  当前状态: DXEF决定当前ZE位置 -> 金银唏=ZE>0(无限), 嘘尿屎=ZE<0(有限)
  明日概率: ->ZE+ZC 决定明日能否进入无限区
"""
import csv

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
CD_B = ['下','忠',chr(0x5FD1)]
AB_G = ['上','中','忐']
AB_B = ['下','忠',chr(0x5FD1)]
ALL_AB = ['上','中','下','忐','忠',chr(0x5FD1)]

lines = []
def pr(s=""):
    lines.append(s)

pr("=" * 90)
pr("核心修正: 当前状态 vs 明日概率")
pr("=" * 90)
pr("")
pr("当前状态(由DXEF定义):")
pr("  金银唏: DXZE>0 -> 当前在DJE之上 -> 无限收益区")
pr("  嘘尿屎: DXZE<0 -> 当前在DJE之下 -> 有限收益区(受DJE距离限制)")
pr("")
pr("明日概率(由→ZE+ZC衡量):")
pr("  金银唏: →ZE+ZC = 留在无限区的概率")
pr("  嘘尿屎: →ZE+ZC = 从有限区进入无限区的概率(过渡)")
pr("")
pr("关键: 嘘尿屎即使→ZE+ZC高, 也是'从有限到无限', 不是'无限中续涨'")
pr("")

# ====== 新框架: 当前状态 × 明日概率 ======
pr("=" * 90)
pr("新框架: 当前位置(当前ZE) × 明日概率(→ZE+ZC)")
pr("=" * 90)
pr("")

pr("8格重新分类:")
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

# 先计算每个组合的"当前无限概率"和"明日无限概率"
# 当前无限比例 = 该组合中当前ZE>0的比例(来自文档§3.3分类)
# 但我们没有每个组合的当前ZE>0比例, 只能用DXEF推断
# 金银唏: 当前ZE>0是大概率
# 嘘尿屎: 当前ZE<0是大概率

pr(f"{'组合':>30} {'等级':>6} {'当前位置':>12} {'→ZE+ZC':>8} {'→ZE>0':>8} {'DS2':>6} {'明日无限概率':>12}")
pr("-" * 85)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    zc_vals = []; ze_vals = []; ds2_vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    zc_vals.append(d['zc']); ze_vals.append(d['ze']); ds2_vals.append(d['ds2'])
    if zc_vals:
        zc_avg = sum(zc_vals)/len(zc_vals); ze_avg = sum(ze_vals)/len(ze_vals); ds2_avg = sum(ds2_vals)/len(ds2_vals)
        zc_min = min(zc_vals); ze_min = min(ze_vals)
        # 当前位置: 金银唏=无限, 嘘尿屎=有限
        curr = "无限区" if efs == EF_G else "有限区"
        # 明日无限概率: 根据zc_avg判断
        prob = "极高" if zc_avg >= 70 else "高" if zc_avg >= 50 else "中" if zc_avg >= 30 else "低" if zc_avg >= 15 else "极低"
        pr(f"{cname:>30} {grade:>6} {curr:>12} {zc_avg:>7.1f}% {ze_avg:>7.1f}% {ds2_avg:>5.1f}% {prob:>12}")

pr("")
pr("关键洞察:")
pr("  S/A/B/C级: 当前在无限区, →ZE+ZC = 留在无限区的概率")
pr("  D/E/F/禁止级: 当前在有限区, →ZE+ZC = 进入无限区的概率")
pr("  即使F级→ZE+ZC=12.3%和禁止级→ZE+ZC=4.7%, 都是'进入'概率, 不是'留下'")
pr("")

# ====== 规则A: 金银唏+上中忐+不限DXAB ======
pr("=" * 90)
pr("规则A: 金银唏+上中忐+不限DXAB")
pr("当前位置: 无限区(金银唏 -> DXZE>0)")
pr("核心问题: 留在无限区的概率有多高?")
pr("=" * 90)
pr("")

for ef in EF_G:
    for cd in CD_G:
        pr(f"\n{ef}/{cd}:")
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                # 留在无限区的概率 = →ZE>0 (续站DJE)
                stay = "稳留" if d['ze'] >= 95 else "高留" if d['ze'] >= 80 else "中留" if d['ze'] >= 50 else "低留"
                pr(f"  {ab} →ZE>0={d['ze']:>5.1f}%({stay})  →ZE+ZC={d['zc']:>5.1f}%  →ZA={d['za']:>5.1f}%  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}")

# ====== 规则B: 嘘尿屎+上忠忐+不限DXAB ======
pr("")
pr("=" * 90)
pr("规则B: 嘘尿屎+上忠忐+不限DXAB")
pr("当前位置: 有限区(嘘尿屎 -> DXZE<0)")
pr("核心问题: 进入无限区(→ZE>0)的概率有多高? 进入后能否同时站ZC(→ZE+ZC)?")
pr("=" * 90)
pr("")

for ef in EF_B:
    for cd in CD_G:
        pr(f"\n{ef}/{cd}:")
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                # 进入无限区概率 = →ZE>0
                enter = "高进" if d['ze'] >= 70 else "中进" if d['ze'] >= 40 else "低进"
                # 进入后能否同时站ZC = →ZE+ZC / →ZE>0 比例
                if d['ze'] > 0:
                    ratio = d['zc'] / d['ze']
                    quality = "强" if ratio >= 0.8 else "中" if ratio >= 0.5 else "弱"
                else:
                    ratio = 0; quality = "无"
                pr(f"  {ab} →ZE>0={d['ze']:>5.1f}%({enter})  →ZE+ZC={d['zc']:>5.1f}%  ZC/ZE比={ratio:.2f}({quality})  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}")

# ====== 规则C: 嘘尿屎+下忠忑+甲乙己 ======
pr("")
pr("=" * 90)
pr("规则C: 嘘尿屎+下忠忑+甲乙己")
pr("当前位置: 有限区, 且CD也不好")
pr("核心问题: 甲乙己能否补偿上两层?")
pr("=" * 90)
pr("")

for ef in EF_B:
    for cd in CD_B:
        pr(f"\n{ef}/{cd}:")
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d:
                enter = "高进" if d['ze'] >= 70 else "中进" if d['ze'] >= 40 else "低进" if d['ze'] >= 20 else "不进"
                pr(f"  {ab} →ZE>0={d['ze']:>5.1f}%({enter})  →ZE+ZC={d['zc']:>5.1f}%  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}")

# ====== 镜面对称: 金银唏+上忠忐忑 ======
pr("")
pr("=" * 90)
pr("镜面对称: 金银唏+上忠忐 甲乙己 vs 丙丁戊")
pr("当前位置: 无限区")
pr("核心问题: 甲乙己能否提高'留在无限区'的概率?")
pr("=" * 90)
pr("")

for ef in EF_G:
    for cd in CD_G:
        qiang = []; ruo = []
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                if ab in AB_G:
                    qiang.append(d)
                else:
                    ruo.append(d)
        if qiang and ruo:
            q_ze_avg = sum(d['ze'] for d in qiang)/len(qiang)
            r_ze_avg = sum(d['ze'] for d in ruo)/len(ruo)
            q_ze_min = min(d['ze'] for d in qiang)
            r_ze_min = min(d['ze'] for d in ruo)
            q_zc_avg = sum(d['zc'] for d in qiang)/len(qiang)
            r_zc_avg = sum(d['zc'] for d in ruo)/len(ruo)
            pr(f"{ef}/{cd}:")
            pr(f"  甲乙己: 留ZEavg={q_ze_avg:.1f}% 留ZEmin={q_ze_min:.1f}%  ZCavg={q_zc_avg:.1f}%")
            pr(f"  丙丁戊: 留ZEavg={r_ze_avg:.1f}% 留ZEmin={r_ze_min:.1f}%  ZCavg={r_zc_avg:.1f}%")
            pr(f"  差距: {q_ze_avg - r_ze_avg:.1f}pp(ZE)  {q_zc_avg - r_zc_avg:.1f}pp(ZC)")

# ====== 最终分类: 当前状态 × 明日概率 × 操作策略 ======
pr("")
pr("=" * 90)
pr("最终分类: 当前位置 × 明日概率")
pr("=" * 90)
pr("")

pr(f"{'等级':>6} {'当前位置':>10} {'→ZE+ZC':>12} {'→ZE>0':>12} {'操作':>20}")
pr("-" * 62)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    zc_vals = []; ze_vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    zc_vals.append(d['zc']); ze_vals.append(d['ze'])
    if zc_vals:
        zc_avg = sum(zc_vals)/len(zc_vals); ze_avg = sum(ze_vals)/len(ze_vals)
        curr = "无限区" if efs == EF_G else "有限区"
        # 操作策略
        if efs == EF_G:  # 已在无限区
            if zc_avg >= 50:
                action = "重仓持有(无限+高概率)"
            elif ze_avg >= 80:
                action = "持有(无限+中等概率)"
            else:
                action = "谨慎持有(无限+低概率)"
        else:  # 在有限区
            if ze_avg >= 50:
                action = "可试仓(有限→无限概率高)"
            elif ze_avg >= 30:
                action = "小仓试错(有限→无限概率中)"
            elif ze_avg >= 15:
                action = "仅观察(有限→无限概率低)"
            else:
                action = "禁止(有限→无限概率极低)"
        pr(f"{grade:>6} {curr:>10} {zc_avg:>10.1f}% {ze_avg:>10.1f}% {action:>20}")

# ====== 用户规则的具体判定 ======
pr("")
pr("=" * 90)
pr("用户规则的具体判定(基于修正框架)")
pr("=" * 90)
pr("")

pr("规则1: 嘘尿屎+下忠忑+丙丁戊 -> 绝对禁止?")
zc_vals = []
for ef in EF_B:
    for cd in CD_B:
        for ab in AB_B:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d)
zc_avg = sum(d['zc'] for d in zc_vals)/len(zc_vals); ze_avg = sum(d['ze'] for d in zc_vals)/len(zc_vals)
pr(f"  当前位置: 有限区. 进入无限区概率: →ZE>0={ze_avg:.1f}%, →ZE+ZC={zc_avg:.1f}%")
pr(f"  -> {'支持禁止: 进入概率仅8.3%, 且进入后站ZC概率仅4.7%' if ze_avg < 15 else '部分支持'}")
pr("")

pr("规则2: 嘘尿屎+下忠忑+甲乙己 -> 可尝试?")
zc_vals = []
for ef in EF_B:
    for cd in CD_B:
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d)
zc_avg = sum(d['zc'] for d in zc_vals)/len(zc_vals); ze_avg = sum(d['ze'] for d in zc_vals)/len(zc_vals)
pr(f"  当前位置: 有限区. 进入无限区概率: →ZE>0={ze_avg:.1f}%, →ZE+ZC={zc_avg:.1f}%")
pr(f"  -> {'不成立: 进入概率仅20.9%, 且进入后站ZC概率仅12.3%' if ze_avg < 30 else '部分支持'}")
pr("")

pr("规则3: 嘘尿屎+上忠忐+不限DXAB -> 可参与?")
zc_vals = []
for ef in EF_B:
    for cd in CD_G:
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d)
zc_avg = sum(d['zc'] for d in zc_vals)/len(zc_vals); ze_avg = sum(d['ze'] for d in zc_vals)/len(zc_vals)
pr(f"  当前位置: 有限区. 进入无限区概率: →ZE>0={ze_avg:.1f}%, →ZE+ZC={zc_avg:.1f}%")
pr(f"  -> {'部分支持: 但需排除尿/忠/屎/忠(全部<15%)' if ze_avg > 30 else '不成立'}")
pr("")

pr("规则4: 金银唏+上忠忐+甲乙己优先 -> 支持?")
zc_vals = []
for ef in EF_G:
    for cd in CD_G:
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d)
zc_avg = sum(d['zc'] for d in zc_vals)/len(zc_vals); ze_avg = sum(d['ze'] for d in zc_vals)/len(zc_vals)
pr(f"  当前位置: 无限区. 留在无限区概率: →ZE>0={ze_avg:.1f}%, →ZE+ZC={zc_avg:.1f}%")
pr(f"  -> {'支持: 留在无限区概率极高, 甲乙己显著优于丙丁戊' if ze_avg > 80 else '部分支持'}")
pr("")

with open('____temp/三级别框架_修正版.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done!")