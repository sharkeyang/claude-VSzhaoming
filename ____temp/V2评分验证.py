# -*- coding: utf-8 -*-
"""验证V2月基策分：用谕组CSV数据跑评分，验证与真实续持率的匹配度"""
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
    if row["_四域"] != "多长":
        return 0

    bx = parse_波型(row.get("波型",""))
    zp = parse_柱排(row.get("柱排周",""))
    wxab = parse_wxab(row.get("WXAB",""))

    # 基础分表
    table = {
        ("龙猪","升排"):75, ("龙猪","人排"):61, ("龙猪","跌排"):58,
        ("龙管","升排"):70, ("龙管","人排"):58, ("龙管","跌排"):56,
        ("头正","升排"):63, ("头正","人排"):58, ("头正","跌排"):51,
        ("震正","升排"):65, ("震正","人排"):56, ("震正","跌排"):51,
        ("震负","升排"):62, ("震负","人排"):58, ("震负","跌排"):50,
    }
    score = table.get((bx, zp), 57)
    if bx == "其他" and zp == "升排": score = 65
    elif bx == "其他" and zp == "人排": score = 57
    elif bx == "其他" and zp == "跌排": score = 52

    # WXAB调节
    if "甲" in row.get("WXAB",""): score += 3
    elif "己" in row.get("WXAB",""): score -= 5
    elif "乙" in row.get("WXAB",""): score -= 3

    # 分类调节
    if cls == "ETF": score += 7
    elif cls in ("小盘",): score -= 3

    return max(0, min(100, score))

# 采样
by_class = defaultdict(list)
for f in files:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    by_class[cls].append(f)

sample = []
for cls, n in [("ETF",50), ("大盘",100), ("中盘",100), ("小盘",50), ("北交所",20)]:
    sample.extend(by_class.get(cls, [])[:n])

print(f"采样: {len(sample)}只")

# 加载数据并评分
score_buckets = defaultdict(lambda: {"total":0, "续持":0, "scores":[]})
score_buckets_5 = defaultdict(lambda: {"total":0, "续持":0})

for f in sample:
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
        row["_四域"] = "多长" if (zc > 0 and wxcd in ("金","银") and zb > 0) else "其他"

        score = V2评分(row, cls)
        if score == 0: continue

        # 按分档统计
        bucket = (score // 10) * 10
        score_buckets[bucket]["total"] += 1
        score_buckets[bucket]["scores"].append(score)

        j = i + 5
        if j < len(rows):
            try:
                zc2 = float(rows[j].get("ZC周", 0))
                zb2 = float(rows[j].get("ZB周", 0))
            except: continue
            wxcd2 = parse_wxcd(rows[j].get("WXCD", ""))
            cont = 1 if (zc2 > 0 and wxcd2 in ("金","银") and zb2 > 0) else 0
            score_buckets[bucket]["续持"] += cont
            score_buckets_5[score // 5 * 5]["total"] += 1
            score_buckets_5[score // 5 * 5]["续持"] += cont

# 按10分档输出
print(f"\n====== 按10分档统计续持率 ======")
print(f"{'分数段':>8} {'续持率':>8} {'样本':>8} {'评价':>8}")
print("-" * 40)
for bucket in sorted(score_buckets.keys()):
    v = score_buckets[bucket]
    if v["total"] < 50: continue
    rate = v["续持"]/v["total"]*100
    avg = sum(v["scores"])/len(v["scores"])
    tag = ""
    if rate >= 65: tag = "持有"
    elif rate >= 50: tag = "关注"
    else: tag = "退出"
    print(f"  {bucket:>3}~{bucket+9}: {rate:>6.1f}% {v['total']:>8} {tag:>8}")

# 验证50分阈值
print(f"\n====== 50分阈值验证 ======")
above = {"total":0, "续持":0}
below = {"total":0, "续持":0}
for bucket, v in score_buckets.items():
    if bucket >= 50:
        above["total"] += v["total"]
        above["续持"] += v["续持"]
    else:
        below["total"] += v["total"]
        below["续持"] += v["续持"]

if above["total"] > 0:
    print(f"  ≥50分: {above['续持']/above['total']*100:.1f}%续持率 (n={above['total']})")
if below["total"] > 0:
    print(f"  <50分: {below['续持']/below['total']*100:.1f}%续持率 (n={below['total']})")
print(f"  差异: {above['续持']/above['total']*100 - below['续持']/below['total']*100:.1f}pp")

# 5分档输出（更精细）
print(f"\n====== 按5分档统计续持率 ======")
print(f"{'分数段':>8} {'续持率':>8} {'样本':>8}")
print("-" * 30)
for bucket in sorted(score_buckets_5.keys()):
    v = score_buckets_5[bucket]
    if v["total"] < 30: continue
    rate = v["续持"]/v["total"]*100
    print(f"  {bucket:>3}~{bucket+4}: {rate:>6.1f}% {v['total']:>8}")

# 按分类看评分分布
print(f"\n====== 按分类看评分分布 ======")
class_scores = defaultdict(lambda: {"total":0, "avg":0, "scores":[]})
for f in sample:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    with open(f, "r", encoding="gbk") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    for row in rows:
        try:
            zc = float(row.get("ZC周", 0))
            zb = float(row.get("ZB周", 0))
        except: continue
        wxcd = parse_wxcd(row.get("WXCD", ""))
        if not (zc > 0 and wxcd in ("金","银") and zb > 0): continue
        score = V2评分(row, cls)
        class_scores[cls]["total"] += 1
        class_scores[cls]["scores"].append(score)

for cls in ["ETF","大盘","中盘","小盘","北交所"]:
    v = class_scores.get(cls, {"total":0, "scores":[]})
    if v["total"] > 0:
        avg = sum(v["scores"])/len(v["scores"])
        print(f"  {cls}: 平均分{avg:.1f} (n={v['total']})")

sys.stdout.flush()