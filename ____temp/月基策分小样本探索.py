# -*- coding: utf-8 -*-
"""月基策略V2：多长区域内组合续持率小样本探索"""
import csv, os, glob, sys
from collections import defaultdict

TEMP = "____temp/谕组"
files = sorted(glob.glob(f"{TEMP}/谕组_*.csv"))
print(f"总文件: {len(files)}")

# 按代码前缀分类
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

# 采样：ETF20+大盘30+中盘30+小盘20+北交所10
by_class = defaultdict(list)
for f in files:
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    cls = 分类(code)
    by_class[cls].append(f)

sample = []
for cls, n in [("ETF", 20), ("大盘", 30), ("中盘", 30), ("小盘", 20), ("北交所", 10)]:
    sample.extend(by_class.get(cls, [])[:n])

print(f"采样: {len(sample)}只")
for cls in ["ETF", "大盘", "中盘", "小盘", "北交所"]:
    n = len([f for f in sample if 分类(os.path.basename(f).replace("谕组_","").replace(".csv","")) == cls])
    print(f"  {cls}: {n}只")

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

# ====== 分析1：各维度单因素续持率 ======
print("\n====== 分析1：各维度单因素续持率 ======")
dims = {"波型": "_波型", "柱排": "_柱排", "盈提示": "_盈提示", "WXAB": "_wxab", "WXCD": "_wxcd"}

for dim_name, dim_key in dims.items():
    dim_counts = defaultdict(lambda: {"total": 0, "续持": 0})
    for code, (cls, rows) in all_weeks.items():
        for i, row in enumerate(rows):
            if not is_多长(row): continue
            j = i + 5
            if j < len(rows):
                val = row[dim_key]
                if val == "?": val = "其他"
                dim_counts[val]["total"] += 1
                if is_多长(rows[j]):
                    dim_counts[val]["续持"] += 1

    results = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in dim_counts.items() if v["total"] >= 5]
    results.sort(key=lambda r: -r[0])
    print(f"\n{dim_name}:")
    for rate, n, val in results:
        print(f"  {val:>6} {rate:>7.1f}% (n={n})")

# ====== 分析2：波型+柱排 二维组合 ======
print("\n\n====== 分析2：波型+柱排 二维组合 ======")
combo2 = defaultdict(lambda: {"total": 0, "续持": 0})
for code, (cls, rows) in all_weeks.items():
    for i, row in enumerate(rows):
        if not is_多长(row): continue
        j = i + 5
        if j < len(rows):
            key = f"{row['_波型']}|{row['_柱排']}"
            combo2[key]["total"] += 1
            if is_多长(rows[j]):
                combo2[key]["续持"] += 1

results2 = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo2.items() if v["total"] >= 5]
results2.sort(key=lambda r: (-r[0], -r[1]))
for rate, n, key in results2:
    波, 柱 = key.split("|")
    print(f"  {波:>6}+{柱:>6} {rate:>7.1f}% (n={n})")

# ====== 分析3：按分类看各维度差异 ======
print("\n\n====== 分析3：按分类看续持率差异 ======")
class_rates = defaultdict(lambda: {"total": 0, "续持": 0})
for code, (cls, rows) in all_weeks.items():
    for i, row in enumerate(rows):
        if not is_多长(row): continue
        j = i + 5
        if j < len(rows):
            class_rates[cls]["total"] += 1
            if is_多长(rows[j]):
                class_rates[cls]["续持"] += 1

print(f"  分类   续持率    样本")
for cls in ["ETF", "大盘", "中盘", "小盘", "北交所"]:
    v = class_rates.get(cls, {"total":0, "续持":0})
    if v["total"] > 0:
        print(f"  {cls:>6} {v['续持']/v['total']*100:>7.1f}%  {v['total']:>8}")

# ====== 分析4：ETF vs 非ETF 的波型+柱排差异 ======
print("\n\n====== 分析4：ETF vs 非ETF 的波型+柱排差异 ======")
for cls_label in ["ETF", "非ETF"]:
    combo_cls = defaultdict(lambda: {"total": 0, "续持": 0})
    for code, (cls, rows) in all_weeks.items():
        target = (cls == "ETF")
        if (cls_label == "ETF") != target: continue
        for i, row in enumerate(rows):
            if not is_多长(row): continue
            j = i + 5
            if j < len(rows):
                key = f"{row['_波型']}|{row['_柱排']}"
                combo_cls[key]["total"] += 1
                if is_多长(rows[j]):
                    combo_cls[key]["续持"] += 1
    print(f"\n  {cls_label}:")
    r = [(v["续持"]/v["total"]*100, v["total"], k) for k, v in combo_cls.items() if v["total"] >= 3]
    r.sort(key=lambda x: -x[0])
    for rate, n, key in r[:10]:
        print(f"    {key:>15} {rate:>7.1f}% (n={n})")

sys.stdout.flush()