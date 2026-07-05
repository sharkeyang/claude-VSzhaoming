"""
Backtest scorecard on 10 stocks from zdata
"""
import pandas as pd, numpy as np, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent / "_产出物"))
from MC2_5_迁移VBA_核1_数据加载引擎 import 读取ZdataCSV, 全量结算
from MC2_5_迁移VBA_核2_策略计算引擎 import 提取WXCD前缀, DXAB护型分类, 计算日层联动系列

codes = ['sh512660','sz300304','sz000510','sh600155','sh513100',
         'sh000016','sh512480','sz159919','sh516880','sh000852']
zdata_dir = r"D:\zdata\data中股"

all_data = []
for code in codes:
    try:
        df = 读取ZdataCSV(code, zdata_dir)
        df = 全量结算(df)
        df["WXCD"] = 提取WXCD前缀(df)
        df["护型"] = DXAB护型分类(df)
        df["联动"] = df["WXCD"] + 计算日层联动系列(
            df["ZE"].values, df["CD"].values, df["ZC"].values,
            df["BC"].values, df["AB"].values, df["ZA"].values,
            df["ZB"].values, df["ZD"].values)
        df["代码"] = code
        all_data.append(df)
        print(f"  {code}: {len(df)}行")
    except Exception as e:
        print(f"  {code}: ERROR {e}")

big = pd.concat(all_data, ignore_index=True)
print(f"\n总数据: {len(big)}行")

# Compute 四域周 and scorecard items
big["BTZC"] = pd.to_numeric(big["BTZC"], errors="coerce")
big["BTZD"] = pd.to_numeric(big["BTZD"], errors="coerce")
big["BTZB"] = pd.to_numeric(big["BTZB"], errors="coerce")
big["BTZE"] = pd.to_numeric(big["BTZE"], errors="coerce")
big["BTZA"] = pd.to_numeric(big["BTZA"], errors="coerce")
big["BTAB"] = pd.to_numeric(big["BTAB"], errors="coerce")
big["ZE"] = pd.to_numeric(big["BTZE"], errors="coerce")
big["ZC"] = pd.to_numeric(big["BTZC"], errors="coerce")
big["ZA"] = pd.to_numeric(big["BTZA"], errors="coerce")
big["AB"] = pd.to_numeric(big["BTAB"], errors="coerce")

# 四域周 (simplified - using daily BTZ as proxy for weekly)
# 四域周 logic: if BTZC>0 then (BTZC>0 & BTCD>0 & BTZB>0 -> 多长 else 多被)
# else: (BTZC<=0 & BTCD<=0 & BTZB<=0 -> 空长 else 空看)
big["WXCD首"] = big["WXCD"].astype(str).str[0]
big["WXAB首"] = big["护型"].astype(str).str[0]

# 四域 (approximate with daily data)
cond_zl = (big["BTZC"] > 0)
cond_dc = (big["CD"] > 0) if "CD" in big.columns else cond_zl
cond_zb = (big["BTZB"] > 0)
big["周四域"] = "空看"
big.loc[cond_zl & cond_dc & cond_zb, "周四域"] = "多长"
big.loc[cond_zl & ~(cond_dc & cond_zb), "周四域"] = "多被"
big.loc[~cond_zl & ~(big["BTZC"] <= 0), "周四域"] = "空看"  # fix
big.loc[(big["BTZC"] <= 0) & (big["CD"] <= 0) & (big["BTZB"] <= 0), "周四域"] = "空长"

# Fix: simpler approach
conditions = [
    (big["BTZC"] > 0) & (big["CD"] > 0) & (big["BTZB"] > 0),
    (big["BTZC"] > 0) & ~((big["CD"] > 0) & (big["BTZB"] > 0)),
    (big["BTZC"] <= 0) & (big["CD"] <= 0) & (big["BTZB"] <= 0),
]
choices = ["多长", "多被", "空长"]
big["周四域"] = np.select(conditions, choices, default="空看")

# WXAB
big["WXAB合格"] = big["WXAB首"].isin(["甲","乙","己"])

# WTAB
big["WTAB类型"] = "久交"
big.loc[big["BTAB"] <= 3, "WTAB类型"] = "刚交"
big.loc[(big["BTAB"] > 3) & (big["BTAB"] <= 10), "WTAB类型"] = "正交"

# 仓日类
big["仓日类"] = "无"
mask_ze = big["ZE"] > 0
big.loc[mask_ze, "仓日类"] = "上" + big.loc[mask_ze, "WXAB首"]

# 日层段 (approximation)
big["日层段"] = "持被"
big.loc[(big["ZA"] > 0), "日层段"] = "持主"
big.loc[(big["ZC"] == 1), "日层段"] = "买初"
big.loc[(big["ZC"] < 0), "日层段"] = "卖浮"

# ===== SCORECARD =====
def calc_score(row):
    if row["WXZC"] <= 0 or row["DXZE"] <= 0:
        return 0, "一票否决"

    s = 0

    # 四域(50)
    if row["周四域"] == "多长": s += 50
    elif row["周四域"] == "多被": s += 25
    elif row["周四域"] == "空看": s += 10
    else: return 0, "空长"

    # WXAB(5)
    if row["WXAB合格"]: s += 5

    # WTAB(5)
    if row["WTAB类型"] == "正交": s += 5
    elif row["WTAB类型"] == "刚交": s += 3
    elif row["WTAB类型"] == "久交": s += 2

    # 仓日类(10)
    if "上" in str(row["仓日类"]):
        c = str(row["仓日类"])
        if "a" in c or "b" in c: s += 10
        else: s += 5
    elif row["仓日类"] == "无": s -= 10

    # 日层段(5)
    if row["日层段"] == "持主": s += 5
    elif row["日层段"] == "买初": s += 3
    elif row["日层段"] == "持被": s += 2
    elif row["日层段"] == "卖浮": s -= 5

    return s, ""

# Compute scores
big["WXZC"] = big["BTZC"]
big["DXZE"] = big["ZE"]
big["分数"], big["否决原因"] = zip(*big.apply(calc_score, axis=1))

# Next day returns
big["次涨"] = big.groupby("代码")["涨幅"].shift(-1)
big["次盈"] = big["次涨"] > 0

# Filter 多长 periods for 长基仓 analysis
duo_chang = big[big["周四域"] == "多长"].copy()
passed = big[big["否决原因"] == ""].copy()

print(f"\n=== 计分卡回测结果 ===")
print(f"总样本: {len(big)}行")
print(f"通过一票否决: {len(passed)}行 ({len(passed)/len(big)*100:.1f}%)")
print(f"其中周四域=多长: {len(duo_chang)}行 ({len(duo_chang)/len(big)*100:.1f}%)")

# Score brackets vs next-day win rate
print(f"\n=== 分数段 vs 次日胜率 ===")
brackets = [(0,0), (1,25), (26,40), (41,55), (56,65), (66,75), (76,85), (86,100)]
for lo, hi in brackets:
    mask = (passed["分数"] >= lo) & (passed["分数"] <= hi) & passed["次涨"].notna()
    n = mask.sum()
    if n > 0:
        win = passed.loc[mask, "次盈"].sum()
        avg_ret = passed.loc[mask, "次涨"].mean()
        print(f"  {lo:3d}-{hi:3d}分: {n:>5}次 胜率{win/n*100:>5.1f}% 均收益{avg_ret:>+6.3f}%")

# 长基仓策略: 多长+分数 threshold
print(f"\n=== <长基仓>策略（周四域=多长）分数阈值分析 ===")
for threshold in [50, 60, 70, 75, 80]:
    mask = (duo_chang["分数"] >= threshold) & (duo_chang["次涨"].notna())
    n = mask.sum()
    if n > 0:
        win = duo_chang.loc[mask, "次盈"].sum()
        avg_ret = duo_chang.loc[mask, "次涨"].mean()
        print(f"  分数≥{threshold}: {n:>5}次 胜率{win/n*100:>5.1f}% 均收益{avg_ret:>+6.3f}%")

# Optimal threshold detection
print(f"\n=== 分数阈值优化（最大化胜率）===")
best_score = 0
best_win = 0
for score in range(40, 95, 5):
    mask = (duo_chang["分数"] >= score) & (duo_chang["次涨"].notna())
    n = mask.sum()
    if n > 30:  # 最少30个样本
        win = duo_chang.loc[mask, "次盈"].sum()
        wr = win/n*100
        if wr > best_win:
            best_win = wr
            best_score = score
        print(f"  分数≥{score}: {n:>5}次 胜率{wr:>5.1f}%")

print(f"\n最佳阈值: 分数≥{best_score}, 胜率{best_win:.1f}%")