"""
神谕策略计算引擎 — 对应 VBA IQQQ跨码_D据擎2神谕.bas 策略列

输入：含BTZ均线数据的 DataFrame（由 数据加载引擎.py 生成）
输出：策略列（日层联动、猪操作、冲高信号）

数据流:
  原始CSV → 数据加载引擎.全量结算(df)
           → 策略计算引擎.执行神谕(df)
           → 含全部策略列的 DataFrame
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple

# ============================================================
# 辅助函数
# ============================================================

def 提取WXCD前缀(df: pd.DataFrame) -> pd.Series:
    """从BTZ条件推导WXCD（金/银/唏/嘘/屎/尿）
    与VBA 位谕of周层三鳄 第一部分等效"""
    result = pd.Series(["?"] * len(df), index=df.index)

    # 金: BTZC>0 AND BTCD>0 AND BTAB>0 AND BTZA>0
    金条件 = (df["BTZC"] > 0) & (df["BTCD"] > 0) & (df["BTAB"] > 0) & (df["BTZA"] > 0)
    result[金条件] = "金"

    # 银: BTZC>0 AND BTCD>0 AND BTAB>0 但 BTZA≤0
    银条件 = (df["BTZC"] > 0) & (df["BTCD"] > 0) & (df["BTAB"] > 0) & (df["BTZA"] <= 0)
    result[银条件] = "银"

    # 唏: BTZC>0 AND BTCD<=0
    唏条件 = (df["BTZC"] > 0) & (df["BTCD"] <= 0)
    result[唏条件] = "唏"

    # 嘘: BTZC>0 AND BTCD>0 AND BTAB<=0
    嘘条件 = (df["BTZC"] > 0) & (df["BTCD"] > 0) & (df["BTAB"] <= 0)
    result[嘘条件] = "嘘"

    # 尿: BTZC<=0 AND BTZB<0 (price below DJC)
    尿条件 = (df["BTZC"] <= 0)  # 最基本：DJC之下
    result[尿条件] = "尿"

    # 屎: BTZC<=0 (与尿重叠，但屎有更深条件)
    屎条件 = (df["BTZC"] <= 0)
    result[屎条件] = "屎"

    # 金覆盖应有更高优先级
    result[金条件] = "金"
    result[银条件] = "银"

    return result


def DXAB护型分类(df: pd.DataFrame) -> pd.Series:
    """日层护型判断（甲乙己=可持有，丙=被，其他=警）
    与VBA InStr(谕组(X, 位谕of日层护型), "甲") > 0 等效"""
    result = pd.Series("警", index=df.index)

    # 甲/乙/己: BTAB>0 时的细分
    甲条件 = (df["BTAB"] > 0) & (df["BTZA"] > 0)  # BTAB正+站上A
    乙条件 = (df["BTAB"] > 0) & (df["BTZA"] <= 0) & (df["BTZB"] > 0)  # BTAB正+未站A+站上B
    己条件 = (df["BTAB"] > 0) & (df["BTZB"] <= 0)  # BTAB正+未站B
    丙条件 = (df["BTAB"] <= 0)  # BTAB负交

    result[甲条件] = "甲"
    result[乙条件] = "乙"
    result[己条件] = "己"
    result[丙条件] = "丙"

    return result


# ============================================================
# 日层联动（V/E等级码）
# ============================================================

def 计算日层联动系列(btze: np.ndarray, btcd: np.ndarray, btzc: np.ndarray,
                       btbc: np.ndarray, btab: np.ndarray, btza: np.ndarray,
                       btzb: np.ndarray, btzd: np.ndarray) -> pd.Series:
    """对应 VBA 位谕of日层联动 第2位: V0~V9 / E0~E9 等级码
    不含WXCD前缀（由外部添加）"""
    grades = []
    for i in range(len(btze)):
        if btze[i] > 0:
            # E系列: DJE之上
            if btcd[i] > 0:
                if btzc[i] > 0:
                    if btbc[i] > 0 and btab[i] > 0:
                        if btza[i] > 0:
                            grades.append("E0上")
                        elif btzb[i] > 0:
                            grades.append("E2上")
                        else:
                            grades.append("E1上")
                    elif btbc[i] > 0:
                        grades.append("E3上")
                    else:
                        grades.append("E4上")
                elif btzd[i] > 0:
                    grades.append("E5中")
                else:
                    grades.append("E6下")
            elif btzc[i] <= 0:
                grades.append("E7忑")
            elif btzc[i] > 0 and btzd[i] <= 0:
                grades.append("E8忠")
            elif btzd[i] > 0:
                grades.append("E9忐")
            else:
                grades.append(">转空")
        else:
            # V系列: DJE之下
            if btcd[i] > 0:
                if btzc[i] > 0:
                    grades.append("V7上")
                elif btzd[i] > 0:
                    grades.append("V8中")
                else:
                    grades.append("V9下")
            elif btzd[i] > 0:
                grades.append("V6忐")
            elif btzc[i] > 0:
                grades.append("V5忠")
            elif btbc[i] > 0:
                grades.append("V4忑")
            elif btab[i] > 0:
                grades.append("V3忑")
            elif btzb[i] > 0:
                grades.append("V2忑")
            elif btza[i] > 0:
                grades.append("V1忑")
            else:
                grades.append("V0忑")
    return pd.Series(grades)


# ============================================================
# 猪操作（长策/清仓决策）
# ============================================================

def 计算猪操作(btze: np.ndarray, btzc: np.ndarray, btza: np.ndarray,
                btzd: np.ndarray, btzb: np.ndarray, 日层联动: pd.Series) -> pd.Series:
    """对应 VBA 位谕of周层猪操作
    格式: 长策/基仓:E0上 / 清仓/空仓:V0忑 / 长策/基仓/止盈:E0上"""

    # 从日层联动提取等级串
    等级串 = 日层联动.str.extract(r'([VE][0-9].)', expand=False)
    等级串 = 日层联动.str.extract(r'([VEve><][0-9].*?)(?:$|\.)', expand=False)

    result = []
    for i in range(len(btze)):
        等级 = str(等级串.iloc[i]) if pd.notna(等级串.iloc[i]) else "?"

        if btze[i] > 0:
            # DJE之上 → 长策
            if btzc[i] > 0:
                if btza[i] > 0:
                    result.append(f"长策/基仓:{等级}")
                else:
                    result.append(f"长策/浮仓:{等级}")
            else:
                result.append(f"长策/减仓:{等级}")
        else:
            # DJE之下 → 清仓
            if btzc[i] > 0 or btzd[i] > 0:
                result.append(f"清仓/基仓:{等级}")
            elif btzb[i] > 0:
                result.append(f"清仓/减仓:{等级}")
            else:
                result.append(f"清仓/空仓:{等级}")

    return pd.Series(result)


# ============================================================
# 冲高信号
# ============================================================

def 计算下周冲高信号(btze: np.ndarray, 下柱冲高提示: pd.Series) -> pd.Series:
    """对应 VBA 位谕of周层下周冲高"""
    result = []
    for i in range(len(btze)):
        if btze[i] > 0:
            if pd.notna(下柱冲高提示.iloc[i]) and "冲" in str(下柱冲高提示.iloc[i]):
                result.append("下周可冲")
            else:
                result.append("禁入")
        else:
            result.append("禁入")
    return pd.Series(result)


def 计算下日冲高信号(btze: np.ndarray, btza: np.ndarray,
                     日柱排: pd.Series, 下柱冲高提示: pd.Series,
                     日层护型: pd.Series) -> pd.Series:
    """对应 VBA 位谕of周层下日冲高"""
    result = []
    for i in range(len(btze)):
        if btze[i] > 0:
            日机符合 = (
                pd.notna(日柱排.iloc[i])
                and str(日柱排.iloc[i]).startswith("升")
                and btza[i] >= 0
                and pd.notna(下柱冲高提示.iloc[i])
                and "冲" in str(下柱冲高提示.iloc[i])
            )
            防日诱 = str(日层护型.iloc[i]) in ["甲", "乙", "己"]

            if 日机符合 and 防日诱:
                result.append("下日可冲")
            else:
                result.append("禁入")
        else:
            result.append("禁入")
    return pd.Series(result)


# ============================================================
# 止盈预警
# ============================================================

def 计算止盈(日层盈提示: pd.Series, 猪操作: pd.Series) -> pd.Series:
    """对猪操作添加止盈后缀"""
    result = 猪操作.copy()
    mask = 日层盈提示.notna() & (日层盈提示 != "")
    if mask.any():
        策略前缀 = 猪操作.str.extract(r'^([^:]+)', expand=False)
        result[mask] = 策略前缀[mask] + "/止盈" + 猪操作[mask].str.extract(r'(:.*$)', expand=False)[mask]
    return result


# ============================================================
# 主入口
# ============================================================

def 执行神谕(df: pd.DataFrame) -> pd.DataFrame:
    """完整神谕策略列计算"""
    result = df.copy()

    # 提取基础数据
    btze = result["BTZE"].values
    btzc = result["BTZC"].values
    btzd = result["BTZD"].values
    btzb = result["BTZB"].values
    btza = result["BTZA"].values
    btcd = result["BTCD"].values
    btbc = result["BTBC"].values
    btab = result["BTAB"].values

    # 1. WXCD前缀
    result["WXCD"] = 提取WXCD前缀(result)

    # 2. 日层护型（DXAB分类）
    result["日层护型"] = DXAB护型分类(result)

    # 3. 日层联动等级码
    result["日层联动"] = result["WXCD"] + 计算日层联动系列(
        btze, btcd, btzc, btbc, btab, btza, btzb, btzd
    )

    # 4. 猪操作
    result["猪操作"] = 计算猪操作(btze, btzc, btza, btzd, btzb, result["日层联动"])

    # 5. 下周冲高信号
    result["下周冲高"] = 计算下周冲高信号(btze, result.get("下柱冲高提示", pd.Series([""]*len(result))))

    # 6. 下日冲高信号
    result["下日冲高"] = 计算下日冲高信号(
        btze, btza, result.get("日柱排", pd.Series([""]*len(result))),
        result.get("下柱冲高提示", pd.Series([""]*len(result))), result["日层护型"]
    )

    # 7. 止盈（暂用简单占位）
    result["日层盈提示"] = ""

    return result


def 全量神谕(df: pd.DataFrame) -> pd.DataFrame:
    """从原始OHLCV到完整神谕策略列的全量流水线"""
    from 数据加载引擎 import 全量结算
    df = 全量结算(df)
    df = 执行神谕(df)
    return df


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    # 生成测试数据
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2020-01-01", periods=n)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    df_test = pd.DataFrame({
        "date": dates,
        "open": close * 0.99,
        "high": close * 1.02,
        "low": close * 0.98,
        "close": close,
        "volume": np.random.randint(100000, 10000000, n),
        "amount": close * np.random.randint(100000, 10000000, n),
    })

    result = 全量神谕(df_test)
    print("\n=== 最后10行策略列 ===")
    cols = ["date", "日层联动", "猪操作", "下周冲高", "下日冲高"]
    print(result[cols].tail(10).to_string(index=False))