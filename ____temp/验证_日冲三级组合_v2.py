"""
日冲策略三级组合验证脚本 - 净版(无emoji)
"""
import csv

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

DXAB_TO_HU = {
    '上': '甲(强)', '中': '乙(强)', '忐': '己(强)',
    '下': '丙(弱)', '忠': '丁(弱)', '忑': '戊(弱)'
}
QIANG = ['上', '中', '忐']  # 甲乙己
RUO = ['下', '忠', '忑']    # 丙丁戊

data = {}
for r in rows:
    key = (r['DXEF'], r['DXCD'], r['DXAB'])
    data[key] = {
        '->ZE>0': float(r['->ZE>0']),
        '->ZE+ZC': float(r['->ZE>0+ZC>0']),
        '->ZE+ZC+ZA': float(r['->ZE>0+ZC>0+ZA>0']),
        'DSHR>2': float(r['下日DSHR>2']),
        '样本': int(r['样本']),
    }

def get(ef, cd, ab):
    return data.get((ef, cd, ab))

EF_BAD = ['嘘', '尿', '屎']
CD_BAD = ['忑', '中', '下']
CD_GOOD = ['上', '忠', '忐']
EF_GOOD = ['金', '银', '唏']

# ============================================================
print("="*80)
print("验证: 假设1 - 嘘尿屎+忑中下+丙丁戊 应禁止?")
print("="*80)

vals_a = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in RUO:
            d = get(ef, cd, ab)
            if d: vals_a.append((ef, cd, ab, d))

print(f"分支数: {len(vals_a)}, 总样本: {sum(v[3]['样本'] for v in vals_a):,}")
print(f"{'EF':>4} {'CD':>4} {'AB':>4} {'护型':>8} {'->ZE>0':>8} {'->ZE+ZC':>8} {'样本':>10}")
print("-"*50)
for ef, cd, ab, d in vals_a:
    print(f"{ef:>4} {cd:>4} {ab:>4} {DXAB_TO_HU[ab]:>8} {d['->ZE>0']:>7.1f}% {d['->ZE+ZC']:>7.1f}% {d['样本']:>10,}")
avg_a = sum(v[3]['->ZE>0'] for v in vals_a) / len(vals_a)
min_a = min(v[3]['->ZE>0'] for v in vals_a)
max_a = max(v[3]['->ZE>0'] for v in vals_a)
print(f"\n平均->ZE>0={avg_a:.1f}%, 范围={min_a:.1f}~{max_a:.1f}%")
print(f"结论: {'完全禁止' if avg_a < 10 else '基本禁止'} (平均仅{avg_a:.1f}%的续站概率)")

# 对比：甲乙己
vals_b = []
for ef in EF_BAD:
    for cd in CD_BAD:
        for ab in QIANG:
            d = get(ef, cd, ab)
            if d: vals_b.append((ef, cd, ab, d))

avg_b = sum(v[3]['->ZE>0'] for v in vals_b) / len(vals_b)
print(f"\n对比: 嘘尿屎+忑中下+甲乙己 平均->ZE>0={avg_b:.1f}%")
print(f"甲乙己比丙丁戊高 {avg_b - avg_a:.1f}pp")

# ============================================================
print("\n" + "="*80)
print("验证: 假设2 - 嘘尿屎+忑中下 只有甲乙己可尝试?")
print("="*80)

# 甲乙己中哪些真能看
print("\n甲乙己中->ZE>0>=50%的分支(可尝试):")
for ef, cd, ab, d in vals_b:
    if d['->ZE>0'] >= 50:
        print(f"  {ef}/{cd}/{ab}({DXAB_TO_HU[ab]}) ->ZE>0={d['->ZE>0']:.1f}% 样本={d['样本']:,}")

print("\n甲乙己中->ZE>0<30%的分支(不可尝试):")
for ef, cd, ab, d in vals_b:
    if d['->ZE>0'] < 30:
        print(f"  {ef}/{cd}/{ab}({DXAB_TO_HU[ab]}) ->ZE>0={d['->ZE>0']:.1f}% 样本={d['样本']:,}")

print("\n关键发现: 嘘/忑/*和尿/忑/*和屎/忑/* 即使甲乙己也极低")
print("  -> 嘘尿屎+忑中下 中真正能尝试的只有 嘘/中+甲乙己, 嘘/下+甲乙己, 尿/中+甲乙己, 屎/中+甲乙己")
print("  -> 嘘尿屎+忑 无论甲乙己丙丁戊都不可参与")

# ============================================================
print("\n" + "="*80)
print("验证: 假设3 - 嘘尿屎+忐忠上 无论三级是什么都可参与?")
print("="*80)

for ef in EF_BAD:
    for cd in CD_GOOD:
        vals = []
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d: vals.append((ab, DXAB_TO_HU[ab], d))

        min_ze = min(v[2]['->ZE>0'] for v in vals)
        max_ze = max(v[2]['->ZE>0'] for v in vals)
        range_ze = max_ze - min_ze
        all_ge_30 = all(v[2]['->ZE>0'] >= 30 for v in vals)
        all_ge_10 = all(v[2]['->ZE>0'] >= 10 for v in vals)
        low_count = sum(1 for v in vals if v[2]['->ZE>0'] < 30)

        status = "全部>=30% OK" if all_ge_30 else \
                 f"有{low_count}/6个分支<30%" if not all_ge_10 else \
                 "全部>=10%但部分<30%"

        print(f"\n{ef}/{cd}: 极差={range_ze:.1f}pp, 最低={min_ze:.1f}%, 最高={max_ze:.1f}% -> {status}")
        for ab, hu, d in vals:
            tag = " !!!" if d['->ZE>0'] < 10 else "     "
            print(f"  {ab:>4}({hu:>8}) ->ZE>0={d['->ZE>0']:>6.1f}% 样本={d['样本']:>8,}{tag}")

# ============================================================
print("\n" + "="*80)
print("验证: 假设4 - 金银唏+上忐忠 都要参与,特别是甲乙己?")
print("="*80)

for ef in EF_GOOD:
    for cd in CD_GOOD:
        print(f"\n{ef}/{cd}:")
        for ab in ['上', '中', '下', '忐', '忠', '忑']:
            d = get(ef, cd, ab)
            if d:
                hu_type = "甲乙己" if ab in QIANG else "丙丁戊"
                print(f"  {ab:>4}({hu_type}) ->ZE>0={d['->ZE>0']:>6.1f}% ->ZE+ZC={d['->ZE+ZC']:>6.1f}% ->ZE+ZC+ZA={d['->ZE+ZC+ZA']:>6.1f}% DSHR>2={d['DSHR>2']:>5.1f}% 样本={d['样本']:>8,}")

# ============================================================
print("\n" + "="*80)
print("四象限对比总结")
print("="*80)

# 计算各象限均值
def avg_ze(efs, cds, abs_list):
    vals = [get(ef, cd, ab) for ef in efs for cd in cds for ab in abs_list]
    vals = [v for v in vals if v]
    return sum(v['->ZE>0'] for v in vals) / len(vals) if vals else 0

# 象限1: 金银唏+上忐忠+甲乙己 (最好的)
q1 = avg_ze(EF_GOOD, CD_GOOD, QIANG)
# 象限2: 金银唏+上忐忠+丙丁戊 (好战场+好时机+弱护型)
q2 = avg_ze(EF_GOOD, CD_GOOD, RUO)
# 象限3: 嘘尿屎+中下忑+甲乙己 (差战场+差时机+强护型)
q3 = avg_ze(EF_BAD, CD_BAD, QIANG)
# 象限4: 嘘尿屎+中下忑+丙丁戊 (最差)
q4 = avg_ze(EF_BAD, CD_BAD, RUO)

print(f"""
{'':>25} {'DXCD=上忐忠(好)':>20} {'DXCD=中下忑(差)':>20}
{'':>25} {'-------------------':>20} {'-------------------':>20}
{'DXEF=金银唏(好)+甲乙己':>25} {q1:>19.1f}% {q3:>19.1f}%
{'DXEF=金银唏(好)+丙丁戊':>25} {q2:>19.1f}% {q4:>19.1f}%
{'':>25} {'-------------------':>20} {'-------------------':>20}
{'DXEF=嘘尿屎(差)+甲乙己':>25} {avg_ze(EF_BAD, CD_GOOD, QIANG):>19.1f}% {q3:>19.1f}%
{'DXEF=嘘尿屎(差)+丙丁戊':>25} {avg_ze(EF_BAD, CD_GOOD, RUO):>19.1f}% {q4:>19.1f}%
""")

print("各假设判定:")
print(f"  假设1(禁止): 平均{avg_a:.1f}%, {'支持' if avg_a < 20 else '部分支持'}")
print(f"  假设2(仅甲乙己): 甲乙己{avg_b:.1f}% vs 丙丁戊{avg_a:.1f}%, {'支持' if avg_b > avg_a + 15 else '部分支持'}")
print(f"  假设3(不限): 注意尿/忠和屎/忠全部<15%, 不能无脑参与")
print(f"  假设4(参与): 平均{avg_ze(EF_GOOD, CD_GOOD, ['上','中','下','忐','忠','忑']):.1f}%, {'支持' if avg_ze(EF_GOOD, CD_GOOD, ['上','中','下','忐','忠','忑']) > 70 else '部分支持'}")

# 给出最终操作规则
print("\n最终操作规则建议:")
print(f"""
1. 禁止区: 嘘尿屎+中下忑+丙丁戊
   ->ZE>0平均{avg_a:.1f}%, 确实应禁止. {f'注意: 有三个异常分支(嘘/中/忠={get("嘘","中","忠")["->ZE>0"]:.1f}%, 嘘/中/忑={get("嘘","中","忑")["->ZE>0"]:.1f}%, 嘘/下/忠={get("嘘","下","忠")["->ZE>0"]:.1f}%)需单独处理' if avg_a < 20 else ''}

2. 尝试区: 嘘尿屎+中下+甲乙己
   ->ZE>0平均{avg_b:.1f}%, 但需注意:
   - 嘘/中+甲乙己(->ZE>0={get("嘘","中","上")["->ZE>0"] if get("嘘","中","上") else "N/A":.1f}~{get("嘘","中","忐")["->ZE>0"] if get("嘘","中","忐") else "N/A":.1f}%) 可尝试
   - 嘘/下+甲乙己(->ZE>0={get("嘘","下","上")["->ZE>0"] if get("嘘","下","上") else "N/A":.1f}~{get("嘘","下","忐")["->ZE>0"] if get("嘘","下","忐") else "N/A":.1f}%) 可尝试
   - 嘘/忑+甲乙己(->ZE>0={get("嘘","忑","上")["->ZE>0"] if get("嘘","忑","上") else "N/A":.1f}~{get("嘘","忑","忐")["->ZE>0"] if get("嘘","忑","忐") else "N/A":.1f}%) 不可尝试
   - 所有+忑的甲乙己都不可尝试: 嘘/忑/上={get("嘘","忑","上")["->ZE>0"] if get("嘘","忑","上") else "N/A":.1f}%, 尿/忑/上={get("尿","忑","上")["->ZE>0"] if get("尿","忑","上") else "N/A":.1f}%, 屎/忑/上={get("屎","忑","上")["->ZE>0"] if get("屎","忑","上") else "N/A":.1f}%

3. 嘘尿屎+忐忠上:
   - 尿/忠(全部<15%)和屎/忠(全部<5%) 不能无脑参与
   - 嘘/忠(8.6~49.7%) 部分可参与
   - 上/忐 可参与, 但需注意DXAB的影响

4. 金银唏+上忐忠:
   - 平均->ZE>0={avg_ze(EF_GOOD, CD_GOOD, ['上','中','下','忐','忠','忑']):.1f}%, 确实应参与
   - 甲乙己({avg_ze(EF_GOOD, CD_GOOD, QIANG):.1f}%) 优于 丙丁戊({avg_ze(EF_GOOD, CD_GOOD, RUO):.1f}%)
""")