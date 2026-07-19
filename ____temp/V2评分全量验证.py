# -*- coding: utf-8 -*-
"""全量V2评分验证：7463只，找规律、看异常"""
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
    for tag in ["金","银","屎","尿","唏","嘘"]:
        if tag in s: return tag
    return "?"

def parse_wxab(s):
    for tag in ["甲","乙","丙","丁","戊","己"]:
        if tag in s: return tag
    return "?"

def parse_波型(s):
    for tag in ["龙猪","龙管","头正","震正","震负"]:
        if tag in s: return tag
    return "其他"

def parse_柱排(s):
    s = s.strip()
    if s.startswith("升"): return "升排"
    if s.startswith("跌"): return "跌排"
    if s.startswith("人"): return "人排"
    return "其他"

def V2评分(row, cls):
    """模拟VBA中的V2评分逻辑"""
    波型 = parse_波型(row.get("波型",""))
    柱排 = parse_柱排(row.get("柱排周",""))
    wxab = row.get("WXAB","")

    table = {
        ("龙猪","升排"):75, ("龙猪","人排"):61, ("龙猪","跌排"):58,
        ("龙管","升排"):70, ("龙管","人排"):58, ("龙管","跌排"):56,
        ("头正","升排"):63, ("头正","人排"):58, ("头正","跌排"):51,
        ("震正","升排"):65, ("震正","人排"):56, ("震正","跌排"):51,
        ("震负","升排"):62, ("震负","人排"):58, ("震负","跌排"):50,
    }
    score = table.get((波型, 柱排), 57)
    if 波型 == "其他" and 柱排 == "升排": score = 65
    elif 波型 == "其他" and 柱排 == "人排": score = 57
    elif 波型 == "其他" and 柱排 == "跌排": score = 52

    if "甲" in wxab: score += 3
    elif "己" in wxab: score -= 5
    elif "乙" in wxab: score -= 3

    if cls == "ETF": score += 7
    elif cls == "小盘": score -= 3

    return max(0, min(100, score))

t0 = time.time()

# 全量统计
score_buckets = defaultdict(lambda: {"total":0, "续持":0})
score_buckets_5 = defaultdict(lambda: {"total":0, "续持":0})
score_buckets_class = defaultdict(lambda: defaultdict(lambda: {"total":0, "续持":0}))
score_buckets_combo = defaultdict(lambda: {"total":0, "续持":0})

# 分析1: 评分 vs 实际续持率
# 分析2: 各分类的评分分布
# 分析3: 各组合的评分偏差
# 分析4: 分数相同的股票，续持率差异

total_多长 = 0
total_valid = 0

for fi, f in enumerate(files):
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    with open(f, "r", encoding="gbk") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    for i, row in enumerate(rows):
        try:
            zc = float(row.get("ZC周", 0))
            zb = float(row.get("ZB周", 0))
        except: continue
        wxcd = parse_wxcd(row.get("WXCD", ""))
        is_多长 = zc > 0 and wxcd in ("金","银") and zb > 0
        if not is_多长: continue
        total_多长 += 1

        score = V2评分(row, cls)
        if score <= 0: continue

        j = i + 5
        if j >= len(rows): continue
        try:
            zc2 = float(rows[j].get("ZC周", 0))
            zb2 = float(rows[j].get("ZB周", 0))
        except: continue
        wxcd2 = parse_wxcd(rows[j].get("WXCD", ""))
        cont = 1 if (zc2 > 0 and wxcd2 in ("金","银") and zb2 > 0) else 0
        total_valid += 1

        bucket = (score // 10) * 10
        bucket5 = (score // 5) * 5
        score_buckets[bucket]["total"] += 1
        score_buckets[bucket]["续持"] += cont
        score_buckets_5[bucket5]["total"] += 1
        score_buckets_5[bucket5]["续持"] += cont
        score_buckets_class[cls][bucket]["total"] += 1
        score_buckets_class[cls][bucket]["续持"] += cont

        波型 = parse_波型(row.get("波型",""))
        柱排 = parse_柱排(row.get("柱排周",""))
        combo_key = f"{波型}|{柱排}"
        score_buckets_combo[combo_key]["total"] += 1
        score_buckets_combo[combo_key]["续持"] += cont

    if (fi + 1) % 1000 == 0:
        print(f"  处理{fi+1}/{len(files)}只... 多长周数: {total_多长} ({time.time()-t0:.0f}s)")

t = time.time() - t0
print(f"\n总处理时间: {t:.0f}s")
print(f"多长区域总周数: {total_多长}")
print(f"有效验证周数: {total_valid}")

# ====== 分析1：按10分档 ======
print(f"\n====== 分析1：按10分档续持率（全量） ======")
print(f"{'分数段':>8} {'续持率':>8} {'样本':>10} {'占比':>8}")
print("-" * 40)
for bucket in sorted(score_buckets.keys()):
    v = score_buckets[bucket]
    if v["total"] < 100: continue
    rate = v["续持"]/v["total"]*100
    pct = v["total"]/total_valid*100
    print(f"  {bucket:>3}~{bucket+9}: {rate:>6.1f}% {v['total']:>10} {pct:>7.1f}%")

# 50分阈值
above = {"total":0, "续持":0}
below = {"total":0, "续持":0}
for bucket, v in score_buckets.items():
    if bucket >= 50:
        above["total"] += v["total"]
        above["续持"] += v["续持"]
    else:
        below["total"] += v["total"]
        below["续持"] += v["续持"]
print(f"\n50分阈值:")
print(f"  >=50分: {above['续持']/above['total']*100:.1f}% (n={above['total']})")
print(f"  <50分:  {below['续持']/below['total']*100:.1f}% (n={below['total']})")
print(f"  差异:   {above['续持']/above['total']*100 - below['续持']/below['total']*100:.1f}pp")

# ====== 分析2：按5分档 ======
print(f"\n====== 分析2：按5分档续持率 ======")
print(f"{'分数段':>8} {'续持率':>8} {'样本':>10}")
print("-" * 30)
for bucket5 in sorted(score_buckets_5.keys()):
    v = score_buckets_5[bucket5]
    if v["total"] < 100: continue
    rate = v["续持"]/v["total"]*100
    print(f"  {bucket5:>3}~{bucket5+4}: {rate:>6.1f}% {v['total']:>10}")

# ====== 分析3：各分类的评分分布 ======
print(f"\n====== 分析3：各分类的评分分布与续持率 ======")
for cls in ["ETF","大盘","中盘","小盘","北交所"]:
    buckets = score_buckets_class.get(cls, {})
    if not buckets: continue
    total_c = sum(v["total"] for v in buckets.values())
    cont_c = sum(v["续持"] for v in buckets.values())
    print(f"\n  {cls} (整体续持率{cont_c/total_c*100:.1f}%, n={total_c}):")
    for bucket in sorted(buckets.keys()):
        v = buckets[bucket]
        if v["total"] < 50: continue
        rate = v["续持"]/v["total"]*100
        pct = v["total"]/total_c*100
        print(f"    {bucket:>3}~{bucket+9}: {rate:>6.1f}% (占本类{pct:>5.1f}%, n={v['total']})")

# ====== 分析4：评分分布（看哪些分数段最集中） ======
print(f"\n====== 分析4：评分分布密度 ======")
score_dist = defaultdict(int)
for bucket, v in score_buckets.items():
    score_dist[bucket] = v["total"]
total = sum(score_dist.values())
for bucket in sorted(score_dist.keys()):
    pct = score_dist[bucket]/total*100
    bar = "█" * int(pct/2)
    print(f"  {bucket:>3}~{bucket+9}: {pct:>5.1f}% {bar}")

# ====== 分析5：各波型×柱排组合的评分偏差 ======
print(f"\n====== 分析5：各组合的评分与实际续持率偏差 ======")
print(f"{'组合':>15} {'实际续持率':>10} {'V2评分':>8} {'偏差':>6} {'样本':>8}")
print("-" * 55)
# 用全量数据重新计算各组合的实际续持率
combo_actual = defaultdict(lambda: {"total":0, "续持":0})
for f in files:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    with open(f, "r", encoding="gbk") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    for i, row in enumerate(rows):
        try:
            zc = float(row.get("ZC周", 0))
            zb = float(row.get("ZB周", 0))
        except: continue
        wxcd = parse_wxcd(row.get("WXCD", ""))
        if not (zc > 0 and wxcd in ("金","银") and zb > 0): continue
        j = i + 5
        if j >= len(rows): continue
        try:
            zc2 = float(rows[j].get("ZC周", 0))
            zb2 = float(rows[j].get("ZB周", 0))
        except: continue
        wxcd2 = parse_wxcd(rows[j].get("WXCD", ""))
        波型 = parse_波型(row.get("波型",""))
        柱排 = parse_柱排(row.get("柱排周",""))
        key = f"{波型}|{柱排}"
        combo_actual[key]["total"] += 1
        if zc2 > 0 and wxcd2 in ("金","银") and zb2 > 0:
            combo_actual[key]["续持"] += 1

# 对比V2评分与实际续持率
v2_lookup = {
    "龙猪|升排":75, "龙猪|人排":61, "龙猪|跌排":58,
    "龙管|升排":70, "龙管|人排":58, "龙管|跌排":56,
    "头正|升排":63, "头正|人排":58, "头正|跌排":51,
    "震正|升排":65, "震正|人排":56, "震正|跌排":51,
    "震负|升排":62, "震负|人排":58, "震负|跌排":50,
}
for key in sorted(combo_actual.keys()):
    v = combo_actual[key]
    if v["total"] < 100: continue
    actual = v["续持"]/v["total"]*100
    v2 = v2_lookup.get(key, 57)
    if key == "其他|升排": v2 = 65
    elif key == "其他|人排": v2 = 57
    elif key == "其他|跌排": v2 = 52
    diff = v2 - actual
    warn = " <<" if abs(diff) > 5 else ""
    print(f"  {key:>15} {actual:>9.1f}% {v2:>7} {diff:>+5.1f} {v['total']:>8}{warn}")

# ====== 分析6：异常检查——为什么有些分数段续持率不升反降 ======
print(f"\n====== 分析6：分数段异常分析 ======")
# 检查60~69分是否比50~59分提升不足
prev_rate = 0
for bucket5 in sorted(score_buckets_5.keys()):
    v = score_buckets_5[bucket5]
    if v["total"] < 100: continue
    rate = v["续持"]/v["total"]*100
    if prev_rate > 0:
        lift = rate - prev_rate
        if lift < 1:
            print(f"  ⚠ {bucket5-5}~{bucket5-1}→{bucket5}~{bucket5+4}: 续持率{prev_rate:.1f}%→{rate:.1f}% (提升仅{lift:.1f}pp)")
    prev_rate = rate

sys.stdout.flush()