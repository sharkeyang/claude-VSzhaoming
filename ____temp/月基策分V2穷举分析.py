# -*- coding: utf-8 -*-
"""月基策分V2：穷举多长区域内所有组合的续持率"""
import csv, os, glob, sys
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

# 采样
by_class = defaultdict(list)
for f in files:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    by_class[cls].append(f)

sample = []
for cls, n in [("ETF", 20), ("大盘", 30), ("中盘", 30), ("小盘", 20), ("北交所", 10)]:
    sample.extend(by_class.get(cls, [])[:n])

print(f"采样: {len(sample)}只")

# 解析函数
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

def parse_盈提示(s):
    s = s.strip()
    if "盈高" in s: return "盈高"
    if "盈宽" in s: return "盈宽"
    return "空"

# 加载数据
all_weeks = {}
for f in sample:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    rows = []
    with open(f, "r", encoding="gbk") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row["_code"] = code
            row["_class"] = cls
            row["_wxcd"] = parse_wxcd(row.get("WXCD", ""))
            row["_wxab"] = parse_wxab(row.get("WXAB", ""))
            row["_波型"] = parse_波型(row.get("波型", ""))
            row["_柱排"] = parse_柱排(row.get("柱排周", ""))
            row["_盈提示"] = parse_盈提示(row.get("盈提示", ""))
            try: row["_ZC"] = float(row.get("ZC周", 0))
            except: row["_ZC"] = 0
            try: row["_ZB"] = float(row.get("ZB周", 0))
            except: row["_ZB"] = 0
            try: row["_周涨"] = float(row.get("周涨", 0))
            except: row["_周涨"] = 0
            rows.append(row)
    all_weeks[code] = (cls, rows)

def is_多长(row):
    return row["_ZC"] > 0 and row["_wxcd"] in ("金", "银") and row["_ZB"] > 0

# ====== 第一步：找出多长区域内所有可能的维度值 ======
print("\n====== 第一步：多长区域内所有维度值分布 ======")
all_波型 = set()
all_柱排 = set()
all_wxab = set()
all_盈提示 = set()
all_wxcd = set()

dim_counts = {
    "波型": defaultdict(int),
    "柱排": defaultdict(int),
    "WXAB": defaultdict(int),
    "盈提示": defaultdict(int),
    "WXCD": defaultdict(int),
}

for code, (cls, rows) in all_weeks.items():
    for row in rows:
        if not is_多长(row): continue
        dim_counts["波型"][row["_波型"]] += 1
        dim_counts["柱排"][row["_柱排"]] += 1
        dim_counts["WXAB"][row["_wxab"]] += 1
        dim_counts["盈提示"][row["_盈提示"]] += 1
        dim_counts["WXCD"][row["_wxcd"]] += 1

for dim, cnts in dim_counts.items():
    print(f"\n  {dim}:")
    total = sum(cnts.values())
    for val, n in sorted(cnts.items(), key=lambda x: -x[1]):
        print(f"    {val:>6}: {n:>6} ({n/total*100:>5.1f}%)")

# ====== 第二步：穷举所有组合 ======
print("\n\n====== 第二步：穷举所有组合的续持率 ======")

# 决定哪些维度用于分类
# 排除WXCD（金vs银差异太小，2.9pp）
# 保留波型、柱排、WXAB、盈提示
# 但盈提示在样本中几乎全为空，先保留看看

# 3维穷举：波型×柱排×WXAB
dim_keys = ["_波型", "_柱排", "_wxab"]
combo3 = defaultdict(lambda: {"total": 0, "续持": 0})
combo3_by_class = defaultdict(lambda: defaultdict(lambda: {"total": 0, "续持": 0}))

# 也记录2维组合（波型×柱排、波型×WXAB、柱排×WXAB）
combo_bx = defaultdict(lambda: {"total": 0, "续持": 0})
combo_bw = defaultdict(lambda: {"total": 0, "续持": 0})
combo_xw = defaultdict(lambda: {"total": 0, "续持": 0})

for code, (cls, rows) in all_weeks.items():
    for i, row in enumerate(rows):
        if not is_多长(row): continue
        j = i + 5
        if j >= len(rows): continue

        k3 = f"{row['_波型']}|{row['_柱排']}|{row['_wxab']}"
        k_bx = f"{row['_波型']}|{row['_柱排']}"
        k_bw = f"{row['_波型']}|{row['_wxab']}"
        k_xw = f"{row['_柱排']}|{row['_wxab']}"

        cont = 1 if is_多长(rows[j]) else 0

        combo3[k3]["total"] += 1
        combo3[k3]["续持"] += cont
        combo3_by_class[cls][k3]["total"] += 1
        combo3_by_class[cls][k3]["续持"] += cont
        combo_bx[k_bx]["total"] += 1
        combo_bx[k_bx]["续持"] += cont
        combo_bw[k_bw]["total"] += 1
        combo_bw[k_bw]["续持"] += cont
        combo_xw[k_xw]["total"] += 1
        combo_xw[k_xw]["续持"] += cont

# 输出3维组合
print("\n--- 波型×柱排×WXAB 三维组合（按续持率降序） ---")
print(f"{'续持率':>8} {'样本':>8} {'波型':>6} {'柱排':>6} {'WXAB':>6}")
print("-" * 45)
results3 = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo3.items()]
results3.sort(key=lambda r: (-r[0], -r[1]))
for rate, n, key in results3:
    b, x, w = key.split("|")
    # 标记样本充足性
    marker = "  "
    if n < 10: marker = "⚠"  # 样本太少
    elif n < 50: marker = "△"  # 样本偏少
    print(f"  {rate:>6.1f}% {n:>8} {b:>6} {x:>6} {w:>6} {marker}")

# 输出2维组合（更稳定）
print("\n\n--- 波型×柱排 二维组合（按续持率降序） ---")
print(f"{'续持率':>8} {'样本':>8} {'波型':>6} {'柱排':>6}")
print("-" * 35)
results_bx = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo_bx.items()]
results_bx.sort(key=lambda r: (-r[0], -r[1]))
for rate, n, key in results_bx:
    b, x = key.split("|")
    marker = "  "
    if n < 10: marker = "⚠"
    elif n < 50: marker = "△"
    print(f"  {rate:>6.1f}% {n:>8} {b:>6} {x:>6} {marker}")

print("\n\n--- 柱排×WXAB 二维组合（按续持率降序） ---")
print(f"{'续持率':>8} {'样本':>8} {'柱排':>6} {'WXAB':>6}")
print("-" * 35)
results_xw = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo_xw.items()]
results_xw.sort(key=lambda r: (-r[0], -r[1]))
for rate, n, key in results_xw:
    x, w = key.split("|")
    marker = "  "
    if n < 10: marker = "⚠"
    elif n < 50: marker = "△"
    print(f"  {rate:>6.1f}% {n:>8} {x:>6} {w:>6} {marker}")

# ====== 第三步：按分类看各组合的差异 ======
print("\n\n====== 第三步：ETF vs 非ETF 各组合续持率差异 ======")
print(f"{'组合':>20} {'ETF续持率':>10} {'非ETF续持率':>10} {'ETF样本':>8} {'非ETF样本':>8} {'差异':>6}")
print("-" * 70)
for k3, v in combo3.items():
    if v["total"] < 50: continue
    etf = combo3_by_class.get("ETF", {}).get(k3, {"total":0, "续持":0})
    non = combo3_by_class.get("大盘", {}).get(k3, {"total":0, "续持":0})
    mid = combo3_by_class.get("中盘", {}).get(k3, {"total":0, "续持":0})
    small = combo3_by_class.get("小盘", {}).get(k3, {"total":0, "续持":0})
    non_total = non["total"] + mid["total"] + small["total"]
    non_cont = non["续持"] + mid["续持"] + small["续持"]
    if etf["total"] >= 50 and non_total >= 50:
        etf_rate = etf["续持"]/etf["total"]*100
        non_rate = non_cont/non_total*100
        diff = etf_rate - non_rate
        print(f"  {k3:>20} {etf_rate:>9.1f}% {non_rate:>9.1f}% {etf['total']:>8} {non_total:>8} {diff:>+5.1f}%")

# ====== 第四步：按自然分档 ======
print("\n\n====== 第四步：按续持率自然分档 ======")
# 用2维组合（波型×柱排）做分档基线，因为样本更稳定
tiers = {
    "S": (75, 100),
    "A": (68, 75),
    "B": (64, 68),
    "C": (60, 64),
    "D": (55, 60),
    "E": (0, 55),
}

for tier, (lo, hi) in tiers.items():
    print(f"\n  {tier}档 ({lo}~{hi}%):")
    for rate, n, key in results_bx:
        if lo <= rate < hi:
            b, x = key.split("|")
            print(f"    {b:>6}+{x:>6} {rate:>6.1f}% (n={n})")

# 最后：所有组合全覆盖的映射表
print("\n\n====== 全覆盖映射表 ======")
print("所有波型×柱排组合的续持率，以及建议分数档：")
bx_lookup = {k: v["续持"]/v["total"]*100 for k, v in combo_bx.items() if v["total"] > 0}

# 列出所有可能的波型和柱排
all_波型 = sorted([v for v in dim_counts["波型"].keys()])
all_柱排 = sorted([v for v in dim_counts["柱排"].keys()])

print(f"\n{'波型':>6} {'柱排':>6} {'续持率':>8} {'样本':>8} {'档位':>6} {'建议分':>6}")
print("-" * 50)
for b in all_波型:
    for x in all_柱排:
        key = f"{b}|{x}"
        if key in bx_lookup:
            rate = bx_lookup[key]
            n = combo_bx[key]["total"]
            # 自然分档
            if rate >= 75: tier, score = "S", 90
            elif rate >= 68: tier, score = "A", 75
            elif rate >= 64: tier, score = "B", 60
            elif rate >= 60: tier, score = "C", 50
            elif rate >= 55: tier, score = "D", 35
            else: tier, score = "E", 20
            marker = ""
            if n < 10: marker = " ⚠样本极少"
            elif n < 50: marker = " △样本偏少"
            print(f"  {b:>6} {x:>6} {rate:>7.1f}% {n:>8} {tier:>6} {score:>6}{marker}")
        else:
            print(f"  {b:>6} {x:>6} {'无数据':>8} {'0':>8} {'E':>6} {'20':>6}  ⚠无样本，默认E档")

# 加上WXAB的调节因子
print("\n\nWXAB调节因子（在基础分上加减）：")
wxab_rates = {}
for k, v in dim_counts["WXAB"].items():
    total = 0
    cont = 0
    for code, (cls, rows) in all_weeks.items():
        for i, row in enumerate(rows):
            if not is_多长(row): continue
            if row["_wxab"] != k: continue
            j = i + 5
            if j >= len(rows): continue
            total += 1
            if is_多长(rows[j]): cont += 1
    if total > 0:
        wxab_rates[k] = cont/total*100
        offset = wxab_rates[k] - 66.0  # 以基线66.0为基准
        print(f"  {k}: {wxab_rates[k]:.1f}% (调节{offset:+.1f}分)")

sys.stdout.flush()