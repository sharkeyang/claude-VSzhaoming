# -*- coding: utf-8 -*-
"""月基命分V2：直接用年化收益（多长介入→WXZC<0退出）"""
import csv, os, glob, sys, time
from collections import defaultdict

TEMP = "____temp/谕组"
files = sorted(glob.glob(f"{TEMP}/谕组_*.csv"))
print(f"总文件: {len(files)}")

def parse_wxcd(s):
    for tag in ["金","银","屎","尿","唏","嘘"]:
        if tag in s: return tag
    return "?"

# 采样：取前500只（快速出结果）
sample = files[:500]
print(f"采样: {len(sample)}只")

t0 = time.time()
results = []

for fi, f in enumerate(sample):
    code = os.path.basename(f).replace("谕组_", "").replace(".csv", "")
    with open(f, "r", encoding="gbk") as fh:
        rows = list(csv.DictReader(fh))

    # 模拟交易：多长介入→WXZC<0退出
    in_pos = False
    持仓累积 = 1.0
    总收益 = 0.0
    交易次数 = 0
    持仓周数 = 0
    盈利次数 = 0
    盈利列表 = []
    亏损列表 = []
    柱排反转 = 0
    prev_dir = ""

    for i, row in enumerate(rows):
        try:
            zc = float(row.get("ZC周", 0))
            zb = float(row.get("ZB周", 0))
        except: continue
        wxcd = parse_wxcd(row.get("WXCD", ""))
        is_多长 = zc > 0 and wxcd in ("金","银") and zb > 0

        try: 周涨 = float(row.get("周涨", 0))
        except: 周涨 = 0

        zp = row.get("柱排周", "").strip()
        cur_dir = ""
        if zp.startswith("升"): cur_dir = "升"
        elif zp.startswith("跌"): cur_dir = "跌"

        if not in_pos:
            if is_多长:
                in_pos = True
                持仓累积 = 1.0
                持仓周数 = 0
                prev_dir = cur_dir
                持仓累积 *= (1 + 周涨 / 100)
                持仓周数 += 1
        else:
            持仓累积 *= (1 + 周涨 / 100)
            持仓周数 += 1

            # 柱排反转计数
            if cur_dir and prev_dir and cur_dir != prev_dir:
                柱排反转 += 1
            if cur_dir: prev_dir = cur_dir

            # 退出条件：WXZC<0
            if zc < 0:
                收益 = 持仓累积 - 1
                总收益 += 收益
                交易次数 += 1
                if 收益 > 0:
                    盈利次数 += 1
                    盈利列表.append(收益)
                else:
                    亏损列表.append(收益)
                in_pos = False

    if 交易次数 == 0:
        continue

    # 年化收益 = 总收益 / 持仓年数
    持仓年数 = 持仓周数 / 52
    年化 = 总收益 / 持仓年数 if 持仓年数 > 0 else 0

    # 其他指标（仅用于参考）
    胜率 = 盈利次数 / 交易次数 if 交易次数 > 0 else 0
    均盈 = sum(盈利列表)/len(盈利列表) if 盈利列表 else 0
    均亏 = abs(sum(亏损列表)/len(亏损列表)) if 亏损列表 else 0
    盈亏比 = 99 if not 亏损列表 else (0 if not 盈利列表 else 均盈/均亏)
    均单次 = 总收益 / 交易次数 if 交易次数 > 0 else 0
    震仓 = 柱排反转 / 持仓周数 if 持仓周数 > 0 else 0

    results.append((code, 年化, 胜率, 盈亏比, 均单次, 震仓, 交易次数, 持仓周数))

t = time.time() - t0
print(f"\n时间: {t:.0f}s")
print(f"有交易记录的股票: {len(results)}只")

# 按年化收益排序
results.sort(key=lambda r: -r[1])

print(f"\n年化收益分布（前30高）:")
print(f"{\"代码\":>10} {\"年化收益\":>10} {\"胜率\":>6} {\"盈亏比\":>6} {\"均单次\":>8} {\"震仓\":>6} {\"次数\":>4} {\"持仓周\":>6}")
for r in results[:30]:
    print(f"{r[0]:>10} {r[1]:>9.1%} {r[2]:>5.0%} {r[3]:>5.0f} {r[4]:>7.2%} {r[5]:>5.2f} {r[6]:>4} {r[7]:>6}")

print(f"\n年化收益分布（后30低）:")
for r in results[-30:]:
    print(f"{r[0]:>10} {r[1]:>9.1%} {r[2]:>5.0%} {r[3]:>5.0f} {r[4]:>7.2%} {r[5]:>5.2f} {r[6]:>4} {r[7]:>6}")

# 统计区间分布
from collections import Counter
bins = Counter()
for r in results:
    年化 = r[1]
    if 年化 < -0.2: bins["<-20%"] += 1
    elif 年化 < 0: bins["-20%~0%"] += 1
    elif 年化 < 0.1: bins["0~10%"] += 1
    elif 年化 < 0.2: bins["10~20%"] += 1
    elif 年化 < 0.5: bins["20~50%"] += 1
    elif 年化 < 1.0: bins["50~100%"] += 1
    else: bins[">100%"] += 1

print(f"\n年化收益区间分布:")
for k in ["<-20%", "-20%~0%", "0~10%", "10~20%", "20~50%", "50~100%", ">100%"]:
    n = bins.get(k, 0)
    print(f"  {k:>10}: {n:>4}只 ({n/len(results)*100:>5.1f}%)")

sys.stdout.flush()