# -*- coding: utf-8 -*-
"""全量数据验证：多长区域波型×柱排组合续持率稳定性"""
import csv, os, glob, sys, time
from collections import defaultdict

TEMP = "____temp/谕组"
files = sorted(glob.glob(f"{TEMP}/谕组_*.csv"))
print(f"总文件: {len(files)}")

def 分类(code):
    c = code.replace("谕组_", "").replace(".csv", "").lower()
    if c.startswith("sz159") or c.startswith("sh510") or c.startswith("sh588") or c.startswith("sh563"):
        return "ETF"
    if c.startswith("sh600") or c.startswith("sh601") or c.startswith("sh603") or c.startswith("sh605"):
        return "大盘"
    if c.startswith("sz000") or c.startswith("sz002"):
        return "中盘"
    if c.startswith("sz300") or c.startswith("sh688"):
        return "小盘"
    if c.startswith("bj"):
        return "北交所"
    return "其他"

def parse_wxcd(s):
    for tag in ["金", "银", "屎", "尿", "唏", "嘘"]:
        if tag in s: return tag
    return "?"

def parse_wxab(s):
    for tag in ["甲", "乙", "丙", "丁", "戊", "己"]:
        if tag in s: return tag
    return "?"

def parse_波型(s):
    for tag in ["龙猪", "龙管", "头正", "震正", "震负"]:
        if tag in s: return tag
    return "其他"

def parse_柱排(s):
    s = s.strip()
    if s.startswith("升"): return "升排"
    if s.startswith("跌"): return "跌排"
    if s.startswith("人"): return "人排"
    return "其他"

t0 = time.time()

# 统计：波型×柱排 + WXAB + 分类
combo_bx = defaultdict(lambda: {"total": 0, "续持": 0})
combo_bx_wxab = defaultdict(lambda: {"total": 0, "续持": 0})
combo_bx_class = defaultdict(lambda: {"total": 0, "续持": 0})  # 按分类
total_多长 = 0
total_续持 = 0

for fi, f in enumerate(files):
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)

    with open(f, "r", encoding="gbk") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            try:
                row["_ZC"] = float(row.get("ZC周", 0))
                row["_ZB"] = float(row.get("ZB周", 0))
            except:
                row["_ZC"] = 0
                row["_ZB"] = 0
            row["_wxcd"] = parse_wxcd(row.get("WXCD", ""))
            row["_wxab"] = parse_wxab(row.get("WXAB", ""))
            row["_波型"] = parse_波型(row.get("波型", ""))
            row["_柱排"] = parse_柱排(row.get("柱排周", ""))
            row["_class"] = cls
            rows.append(row)

    # 计算续持率：遍历所有行，对多长行检查5周后是否仍多长
    for i, row in enumerate(rows):
        is_多长 = row["_ZC"] > 0 and row["_wxcd"] in ("金", "银") and row["_ZB"] > 0
        if not is_多长: continue
        total_多长 += 1
        j = i + 5
        if j >= len(rows): continue
        rj = rows[j]
        cont = 1 if (rj["_ZC"] > 0 and rj["_wxcd"] in ("金", "银") and rj["_ZB"] > 0) else 0

        k_bx = f"{row['_波型']}|{row['_柱排']}"
        k_bx_wxab = f"{row['_波型']}|{row['_柱排']}|{row['_wxab']}"
        k_bx_cls = f"{row['_波型']}|{row['_柱排']}|{row['_class']}"

        combo_bx[k_bx]["total"] += 1
        combo_bx[k_bx]["续持"] += cont
        combo_bx_wxab[k_bx_wxab]["total"] += 1
        combo_bx_wxab[k_bx_wxab]["续持"] += cont
        combo_bx_class[k_bx_cls]["total"] += 1
        combo_bx_class[k_bx_cls]["续持"] += cont
        total_续持 += cont

    if (fi + 1) % 500 == 0:
        elapsed = time.time() - t0
        print(f"  处理{fi+1}/{len(files)}只... 多长周数: {total_多长} ({elapsed:.0f}s)")

t = time.time() - t0
print(f"\n总处理时间: {t:.0f}s")
print(f"多长区域总周数: {total_多长}")
print(f"有5周后数据的多长周数: {sum(v['total'] for v in combo_bx.values())}")
基线总 = sum(v['续持'] for v in combo_bx.values())
基线样本 = sum(v['total'] for v in combo_bx.values())
print(f"整体续持率: {基线总/基线样本*100:.1f}% (基线样本={基线样本})")

# ====== 分析1：波型×柱排 全量续持率 vs 小样本 ======
print("\n\n====== 分析1：波型×柱排 全量续持率 vs 小样本 ======")
print(f"{'波型':>6} {'柱排':>6} {'全量续持率':>10} {'全量样本':>10} {'小样本续持率':>10} {'小样本':>8} {'差异':>6}")
print("-" * 65)

# 小样本基准数据（来自前一次110只分析）
sample_bx = {
    "龙猪|升排": 75.7, "龙猪|人排": 75.0, "龙猪|跌排": 55.3,
    "龙管|升排": 68.2, "龙管|人排": 57.4, "龙管|跌排": 56.6,
    "头正|升排": 65.5, "头正|人排": 60.9, "头正|跌排": 48.8,
    "震正|升排": 66.8, "震正|人排": 58.7, "震正|跌排": 55.0,
    "震负|升排": 59.9, "震负|人排": 59.2, "震负|跌排": 55.0,
}

# 按全量续持率降序
results_bx = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo_bx.items()]
results_bx.sort(key=lambda r: (-r[0], -r[1]))

for rate, n, key in results_bx:
    sample_r = sample_bx.get(key, None)
    if sample_r:
        diff = rate - sample_r
        print(f"  {key.split('|')[0]:>6} {key.split('|')[1]:>6} {rate:>9.1f}% {n:>10} {sample_r:>9.1f}% {'~':>8} {diff:>+5.1f}%")
    else:
        print(f"  {key.split('|')[0]:>6} {key.split('|')[1]:>6} {rate:>9.1f}% {n:>10} {'无数据':>10}")

# ====== 分析2：自然分档（基于全量数据） ======
print("\n\n====== 分析2：自然分档 ======")
print(f"{'档位':>6} {'续持率':>10} {'组合':>20} {'样本':>10}")
print("-" * 55)

# 用全量数据重新分档
tier_groups = defaultdict(list)
for rate, n, key in results_bx:
    if rate >= 75:
        tier_groups["S(75~100%)"].append((rate, n, key))
    elif rate >= 68:
        tier_groups["A(68~75%)"].append((rate, n, key))
    elif rate >= 64:
        tier_groups["B(64~68%)"].append((rate, n, key))
    elif rate >= 60:
        tier_groups["C(60~64%)"].append((rate, n, key))
    elif rate >= 55:
        tier_groups["D(55~60%)"].append((rate, n, key))
    else:
        tier_groups["E(0~55%)"].append((rate, n, key))

for tier in ["S(75~100%)", "A(68~75%)", "B(64~68%)", "C(60~64%)", "D(55~60%)", "E(0~55%)"]:
    items = tier_groups.get(tier, [])
    if not items: continue
    print(f"\n  {tier}:")
    for rate, n, key in items:
        print(f"    {key:>20} {rate:>9.1f}% (n={n})")

# ====== 分析3：WXAB调节因子 ======
print("\n\n====== 分析3：WXAB调节因子（全量数据） ======")
wxab_rates = defaultdict(lambda: {"total": 0, "续持": 0})
for k, v in combo_bx_wxab.items():
    b, x, w = k.split("|")
    wxab_rates[w]["total"] += v["total"]
    wxab_rates[w]["续持"] += v["续持"]

baseline = 基线总 / 基线样本 * 100
print(f"全量基线: {baseline:.1f}%")
for w in ["甲", "乙", "己", "丙", "丁", "戊"]:
    v = wxab_rates.get(w, {"total": 0, "续持": 0})
    if v["total"] > 0:
        rate = v["续持"]/v["total"]*100
        adj = rate - baseline
        print(f"  {w}: {rate:.1f}% (n={v['total']}, 调节{adj:+.1f}分)")

# ====== 分析4：ETF vs 非ETF 调节 ======
print("\n\n====== 分析4：分类调节 ======")
class_rates = defaultdict(lambda: {"total": 0, "续持": 0})
for k, v in combo_bx_class.items():
    b, x, cls = k.split("|")
    class_rates[cls]["total"] += v["total"]
    class_rates[cls]["续持"] += v["续持"]

for cls in ["ETF", "大盘", "中盘", "小盘", "北交所"]:
    v = class_rates.get(cls, {"total": 0, "续持": 0})
    if v["total"] > 0:
        rate = v["续持"]/v["total"]*100
        adj = rate - baseline
        print(f"  {cls}: {rate:.1f}% (n={v['total']}, 调节{adj:+.1f}分)")

# ====== 分析5：关键差异——ETF vs 非ETF 各组合对比 ======
print("\n\n====== 分析5：ETF vs 非ETF 关键组合差异 ======")
print(f"{'组合':>20} {'ETF%':>8} {'非ETF%':>8} {'ETF样本':>8} {'非ETF样本':>8} {'差异':>6}")
print("-" * 65)

# 汇总ETF和非ETF
etf_combo = defaultdict(lambda: {"total": 0, "续持": 0})
non_combo = defaultdict(lambda: {"total": 0, "续持": 0})
for k, v in combo_bx_class.items():
    b, x, cls = k.split("|")
    key = f"{b}|{x}"
    if cls == "ETF":
        etf_combo[key]["total"] += v["total"]
        etf_combo[key]["续持"] += v["续持"]
    else:
        non_combo[key]["total"] += v["total"]
        non_combo[key]["续持"] += v["续持"]

for key in sorted(etf_combo.keys()):
    e = etf_combo[key]
    n = non_combo.get(key, {"total": 0, "续持": 0})
    if e["total"] >= 50 and n["total"] >= 50:
        e_rate = e["续持"]/e["total"]*100
        n_rate = n["续持"]/n["total"]*100
        diff = e_rate - n_rate
        print(f"  {key:>20} {e_rate:>7.1f}% {n_rate:>7.1f}% {e['total']:>8} {n['total']:>8} {diff:>+5.1f}%")

sys.stdout.flush()