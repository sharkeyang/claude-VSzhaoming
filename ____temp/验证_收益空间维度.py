# -*- coding: utf-8 -*-
"""
三级别框架 - 正确维度: 收益空间无限vs有限
核心逻辑:
  →ZE>0: 续站DJE - 进入无上限收益区域
  →ZE+ZC: 续站DJE+DJC - 主升区域
  →ZE+ZC+ZA: 三级续站 - 最强区域
  DSHR>2: 短期波动率 - 不同维度
"""
import csv

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

data = {}
for r in rows:
    data[(r['DXEF'], r['DXCD'], r['DXAB'])] = {
        'ze': float(r['→ZE>0']),
        'zc': float(r['→ZE>0+ZC>0']),
        'za': float(r['→ZE>0+ZC>0+ZA>0']),
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

# ====== 核心: 8格组合 + 收益空间指标 ======
pr("=" * 90)
pr("三级别分类系统: 收益空间维度 (无限vs有限)")
pr("=" * 90)
pr("")
pr("三级指标含义:")
pr("  →ZE>0:     续站DJE概率 -> 进入无上限收益区域")
pr("  →ZE+ZC:    续站DJE+DJC概率 -> 主升区(文档§3.2: 中位收益8.23%, P90=77.77%)")
pr("  →ZE+ZC+ZA: 三级均线全守 -> 最强区(持主)")
pr("  DSHR>2:    次日冲高>2%概率 -> 短期波动, 独立维度")
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

pr(f"{'组合':>30} {'等级':>6} {'ZE→0':>8} {'ZE+ZC':>8} {'ZE+ZC+ZA':>8} {'DS2':>6} {'样本':>12}")
pr("-" * 80)

for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    ze_vals = []; zc_vals = []; za_vals = []; ds2_vals = []; all_n = 0
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    ze_vals.append(d['ze']); zc_vals.append(d['zc'])
                    za_vals.append(d['za']); ds2_vals.append(d['ds2'])
                    all_n += d['n']
    if ze_vals:
        ze_avg = sum(ze_vals)/len(ze_vals); ze_min = min(ze_vals)
        zc_avg = sum(zc_vals)/len(zc_vals); zc_min = min(zc_vals)
        za_avg = sum(za_vals)/len(za_vals); za_min = min(za_vals)
        ds2_avg = sum(ds2_vals)/len(ds2_vals)
        pr(f"{cname:>30} {grade:>6} {ze_avg:>7.1f}% {zc_avg:>7.1f}% {za_avg:>7.1f}% {ds2_avg:>5.1f}% {all_n:>12,}")
        pr(f"{'':>30} {'':>6} 最低:{ze_min:.1f}%  最低:{zc_min:.1f}%  最低:{za_min:.1f}%")
        pr("")

# ====== 关键: 用户规则在"无限收益"维度的表现 ======
pr("=" * 90)
pr("规则A: 金银唏+上中忐+不限DXAB (无限收益维度)")
pr("=" * 90)
pr("")

for ef in EF_G:
    for cd in CD_G:
        pr(f"\n{ef}/{cd}:")
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                # 无限收益品质: 同时续ZE+ZC+ZA的概率
                pr(f"  {ab} ->ZE+ZC+ZA={d['za']:>5.1f}%  ->ZE+ZC={d['zc']:>5.1f}%  ->ZE>0={d['ze']:>5.1f}%  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}")

# ====== 规则B: 嘘尿屎+上忠忐 (无限收益维度) ======
pr("")
pr("=" * 90)
pr("规则B: 嘘尿屎+上忠忐+不限DXAB (无限收益维度)")
pr("=" * 90)
pr("")

for ef in EF_B:
    for cd in CD_G:
        pr(f"\n{ef}/{cd}:")
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d:
                tag = ""
                if d['zc'] < 30: tag = " [ZC<30%: 震荡区, 收益有天花板]"
                elif d['zc'] < 50: tag = " [ZC<50%: 有限收益]"
                pr(f"  {ab} ->ZE+ZC+ZA={d['za']:>5.1f}%  ->ZE+ZC={d['zc']:>5.1f}%  ->ZE>0={d['ze']:>5.1f}%  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}{tag}")

# ====== 规则C: 嘘尿屎+下忠忑+甲乙己 (无限收益维度) ======
pr("")
pr("=" * 90)
pr("规则C: 嘘尿屎+下忠忑+甲乙己 (无限收益维度)")
pr("=" * 90)
pr("")

for ef in EF_B:
    for cd in CD_B:
        pr(f"\n{ef}/{cd}:")
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d:
                pr(f"  {ab} ->ZE+ZC+ZA={d['za']:>5.1f}%  ->ZE+ZC={d['zc']:>5.1f}%  ->ZE>0={d['ze']:>5.1f}%  DS2={d['ds2']:>5.1f}%  N={d['n']:>8,}")

# ====== 镜面对称: 金银唏+上忠忐忑 (无限收益维度) ======
pr("")
pr("=" * 90)
pr("镜面对称: 金银唏+上忠忐 甲乙己 vs 丙丁戊 (无限收益维度)")
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
            pr(f"\n{ef}/{cd}:")
            pr(f"  甲乙己(上中忐):")
            for d in qiang:
                pr(f"    {d['za']:>5.1f}%/{d['zc']:>5.1f}%/{d['ze']:>5.1f}%  DS2={d['ds2']:>5.1f}%")
            pr(f"  丙丁戊(下忠忑):")
            for d in ruo:
                pr(f"    {d['za']:>5.1f}%/{d['zc']:>5.1f}%/{d['ze']:>5.1f}%  DS2={d['ds2']:>5.1f}%")

# ====== 核心: 三级分类的"收益空间"区分度 ======
pr("")
pr("=" * 90)
pr("核心: 三级分类对收益空间的区分度 (→ZE+ZC 才是关键指标)")
pr("=" * 90)
pr("")
pr("文档§3.2 结论:")
pr("  →ZE+ZC>0 (主升区): 中位持有期收益 8.23%, P90=77.77%, >50%收益概率=16.9%")
pr("  →ZE+ZC≤0 (震荡区): 中位持有期收益 3.96%, P90=21.01%, >50%收益概率=1.3%")
pr("  差距: 2.1x中位, 3.7x P90, 13x >50%概率")
pr("")
pr("所以 →ZE+ZC 是判断'无限vs有限收益'的核心指标")
pr("")

# 按8格计算 →ZE+ZC 平均
pr(f"{'组合':>30} {'等级':>6} {'ZE+ZC平均':>10} {'ZE+ZC最低':>10} {'范围':>16} {'DS2':>6}")
pr("-" * 80)
for cname, efs, cds, abs_list in combos:
    grade = cname.split(":")[0].strip()
    zc_vals = []; ds2_vals = []
    for ef in efs:
        for cd in cds:
            for ab in abs_list:
                d = get(ef, cd, ab)
                if d:
                    zc_vals.append(d['zc']); ds2_vals.append(d['ds2'])
    if zc_vals:
        zc_avg = sum(zc_vals)/len(zc_vals); zc_min = min(zc_vals); zc_max = max(zc_vals)
        ds2_avg = sum(ds2_vals)/len(ds2_vals)
        pr(f"{cname:>30} {grade:>6} {zc_avg:>9.1f}% {zc_min:>9.1f}% {zc_min:.1f}~{zc_max:.1f}% {ds2_avg:>5.1f}%")

# ====== 关键: 你要的"绝对禁止"定位 ======
pr("")
pr("=" * 90)
pr("绝对禁止区的定位: 嘘尿屎+下忠忑+丙丁戊")
pr("→ZE+ZC平均=3.0%, 最低=0.1%")
pr("→ 这是'无限收益'概率仅3%的区域, 冲高(30%)但空间有限")
pr("=" * 90)
pr("")

# 对比: 用户想知道的各种组合的 →ZE+ZC
pr("三个关键对比:")
pr("")

# 1. 绝对禁止: 嘘尿屎+下忠忑+丙丁戊
zc_vals = []
for ef in EF_B:
    for cd in CD_B:
        for ab in AB_B:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d['zc'])
zc_avg = sum(zc_vals)/len(zc_vals); zc_min = min(zc_vals); zc_max = max(zc_vals)
pr(f"1) 绝对禁止(嘘尿屎+下忠忑+丙丁戊):")
pr(f"   →ZE+ZC平均={zc_avg:.1f}%, 范围={zc_min:.1f}~{zc_max:.1f}%")
pr(f"   → '无限收益'概率极低, 应禁止")
pr("")

# 2. 二级禁止+甲乙己: 嘘尿屎+下忠忑+甲乙己
zc_vals = []
for ef in EF_B:
    for cd in CD_B:
        for ab in AB_G:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d['zc'])
zc_avg = sum(zc_vals)/len(zc_vals); zc_min = min(zc_vals); zc_max = max(zc_vals)
pr(f"2) 二级坏+甲乙己(嘘尿屎+下忠忑+甲乙己):")
pr(f"   →ZE+ZC平均={zc_avg:.1f}%, 范围={zc_min:.1f}~{zc_max:.1f}%")
pr(f"   → 比绝对禁止好, 但大部分仍有限")
pr("")

# 3. 一级好+二级好+不限: 金银唏+上中忐+不限
zc_vals = []
for ef in EF_G:
    for cd in CD_G:
        for ab in ALL_AB:
            d = get(ef, cd, ab)
            if d: zc_vals.append(d['zc'])
zc_avg = sum(zc_vals)/len(zc_vals); zc_min = min(zc_vals); zc_max = max(zc_vals)
pr(f"3) 金银唏+上中忐+不限DXAB:")
pr(f"   →ZE+ZC平均={zc_avg:.1f}%, 范围={zc_min:.1f}~{zc_max:.1f}%")
pr(f"   → '无限收益'概率高, 应参与")
pr("")

# ====== 两个维度融合: 收益空间 × 短期波动 ======
pr("=" * 90)
pr("融合框架: 收益空间(→ZE+ZC) × 短期波动(DSHR>2)")
pr("=" * 90)
pr("")
pr("  收益空间维度: 三级分类决定")
pr("    →ZE+ZC > 50%: 主升区, 收益无上限")
pr("    →ZE+ZC 20~50%: 过渡区, 收益有限")
pr("    →ZE+ZC < 20%: 震荡区, 收益有天花板")
pr("")
pr("  短期波动维度: 管宽/市板/DSHA决定")
pr("    DSHR>2 > 30%: 高冲高概率")
pr("    DSHR>2 20~30%: 中等")
pr("    DSHR>2 < 20%: 低冲高概率")
pr("")
pr("  操作策略:")
pr("    →ZE+ZC>50% + DS2>30%: 无限收益+高概率 -> 重仓")
pr("    →ZE+ZC>50% + DS2<20%: 无限收益+低概率 -> 轻仓等")
pr("    →ZE+ZC<20% + DS2>30%: 有限收益+高概率 -> 超短快进快出")
pr("    →ZE+ZC<20% + DS2<20%: 有限收益+低概率 -> 不做")
pr("")

# 四象限
pr("四象限矩阵:")
pr("")
pr(f"{'':>25} {'DSHR>2>30%(高冲高)':>25} {'DSHR>2<20%(低冲高)':>25}")
pr(f"{'':>25} {'-------------------':>25} {'-------------------':>25}")

# 无限收益象限
zc_high_ds_high = []
zc_high_ds_low = []
zc_low_ds_high = []
zc_low_ds_low = []

for ef in ['金','银','唏','嘘','尿','屎']:
    for cd in ['上','中','下','忐','忠',chr(0x5FD1)]:
        for ab in ['上','中','下','忐','忠',chr(0x5FD1)]:
            d = get(ef, cd, ab)
            if d:
                if d['zc'] >= 50 and d['ds2'] >= 30:
                    zc_high_ds_high.append((ef, cd, ab, d))
                elif d['zc'] >= 50 and d['ds2'] < 20:
                    zc_high_ds_low.append((ef, cd, ab, d))
                elif d['zc'] < 20 and d['ds2'] >= 30:
                    zc_low_ds_high.append((ef, cd, ab, d))
                elif d['zc'] < 20 and d['ds2'] < 20:
                    zc_low_ds_low.append((ef, cd, ab, d))

pr(f"{'→ZE+ZC>50% (无限收益)':>25} {len(zc_high_ds_high):>14}个分支 {len(zc_high_ds_low):>14}个分支")
pr(f"{'→ZE+ZC<20% (有限收益)':>25} {len(zc_low_ds_high):>14}个分支 {len(zc_low_ds_low):>14}个分支")
pr("")

# 展示几个典型例子
pr("典型例子:")
pr("")
pr("无限收益+高冲高(重仓):")
cnt = 0
for ef, cd, ab, d in sorted(zc_high_ds_high, key=lambda x: -x[3]['zc'])[:5]:
    pr(f"  {ef}/{cd}/{ab}: ZE+ZC={d['zc']:.1f}%  DS2={d['ds2']:.1f}%  N={d['n']:,}")

pr("")
pr("无限收益+低冲高(轻仓等):")
for ef, cd, ab, d in sorted(zc_high_ds_low, key=lambda x: -x[3]['zc'])[:5]:
    pr(f"  {ef}/{cd}/{ab}: ZE+ZC={d['zc']:.1f}%  DS2={d['ds2']:.1f}%  N={d['n']:,}")

pr("")
pr("有限收益+高冲高(超短快进):")
for ef, cd, ab, d in sorted(zc_low_ds_high, key=lambda x: -x[3]['ds2'])[:5]:
    pr(f"  {ef}/{cd}/{ab}: ZE+ZC={d['zc']:.1f}%  DS2={d['ds2']:.1f}%  N={d['n']:,}")

pr("")
pr("有限收益+低冲高(不做):")
for ef, cd, ab, d in sorted(zc_low_ds_low, key=lambda x: -x[3]['zc'])[:5]:
    pr(f"  {ef}/{cd}/{ab}: ZE+ZC={d['zc']:.1f}%  DS2={d['ds2']:.1f}%  N={d['n']:,}")

with open('____temp/三级别框架_收益空间维度.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done!")