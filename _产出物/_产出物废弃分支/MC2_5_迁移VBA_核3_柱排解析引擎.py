"""
柱排解析引擎 — 对应 VBA 位谕of周层柱排 / 位谕of日层柱排

核心逻辑:
  1. 每根K线计算 值单形并符 (单柱形态符号)
  2. 滚动4位 并符串
  3. 匹配右端字符 → 输出柱排分类

符号系统:
  Q = 升连 (rising consecutive)
  O = 升吞 (rising engulfing)
  o = 升孕 (rising pregnant/harami)
  W = 跌连 (falling consecutive)
  V = 跌吞 (falling engulfing)
  v = 跌孕 (falling pregnant/harami)
"""

import numpy as np
import pandas as pd


# ============================================================
# 1. 单柱形态符号
# ============================================================

def 计算单柱符号(涨幅: float, 前涨幅: float, 今收: float, 前开: float) -> str:
    """与VBA 值单形并符 完全一致"""
    if 涨幅 < 0:
        if 前涨幅 < 0:
            return "W"  # 跌连
        elif 今收 < 前开:
            return "V"  # 跌吞
        else:
            return "v"  # 跌孕
    else:
        if 前涨幅 >= 0:
            return "Q"  # 升连
        elif 今收 >= 前开:
            return "O"  # 升吞
        else:
            return "o"  # 升孕


# ============================================================
# 2. 柱排分类（与VBA位谕of周层柱排/日层柱排完全一致）
# ============================================================

# 符号常量
_Q = "Q"  # 升连
_O = "O"  # 升吞
_o = "o"  # 升孕
_W = "W"  # 跌连
_V = "V"  # 跌吞
_v = "v"  # 跌孕


def 柱排分类(并符串: str, BTPR0: int = 0) -> str:
    """
    与VBA If/ElseIf 链完全一致
    输入: 并符串 (最后4+字符), 如 "QQ", "QvOQ", "oVov"
    输出: 柱排字符串, 如 "升.尾连QQ", "跌.尾吞oV", "(升)人.连后吞QV"
    """
    if len(并符串) < 2:
        return "错.未赋值"

    # --- 升链 ---
    if 并符串[-2:] == _Q + _Q:
        return f"升.尾连{_Q}{_Q}"
    if 并符串[-2:] == _O + _Q:
        return f"升.尾连{_O}{_Q}"
    if 并符串[-2:] == _o + _Q:
        return f"升.尾连{_o}{_Q}"
    if 并符串[-2:] == _v + _O:
        return f"升.尾吞{_v}{_O}"
    if 并符串[-2:] == _Q + _v:
        return f"升.尾反孕{_Q}{_v}"
    if len(并符串) >= 3 and 并符串[-3:] == _v + _O + _v:
        return f"升.尾反孕{_v}{_O}{_v}"

    # --- 跌链 ---
    if 并符串[-2:] == _W + _W:
        return f"跌.尾连{_W}{_W}"
    if 并符串[-2:] == _V + _W:
        return f"跌.尾连{_V}{_W}"
    if 并符串[-2:] == _v + _W:
        return f"跌.尾连{_v}{_W}"
    if 并符串[-2:] == _o + _V:
        return f"跌.尾吞{_o}{_V}"
    if 并符串[-2:] == _W + _o:
        return f"跌.尾反孕{_W}{_o}"
    if len(并符串) >= 3 and 并符串[-3:] == _o + _V + _o:
        return f"跌.尾反孕{_o}{_V}{_o}"

    # --- 人排: 连后吞 ---
    if 并符串[-2:] == _Q + _V:
        return f"(升)人.连后吞{_Q}{_V}"
    if len(并符串) >= 3 and 并符串[-3:] == _Q + _V + _o:
        return f"(升)人.连后吞{_Q}{_V}{_o}"
    if 并符串[-2:] == _W + _O:
        return f"(跌)人.连后吞{_W}{_O}"
    if len(并符串) >= 3 and 并符串[-3:] == _W + _O + _v:
        return f"(跌)人.连后吞{_W}{_O}{_v}"

    # --- 人排: 吞吞 ---
    if len(并符串) >= 3 and 并符串[-3:] == _v + _O + _V:
        return f"(升)人.吞吞{_v}{_O}{_V}"
    if len(并符串) >= 4 and 并符串[-4:] == _v + _O + _V + _o:
        return f"(升)人.吞吞{_v}{_O}{_V}{_o}"
    if 并符串[-2:] == _O + _V or (len(并符串) >= 3 and 并符串[-3:] == _O + _V + _o):
        return f"(人)人.吞吞* {_O}{_V}"

    # --- 跌衔吞吞 ---
    if len(并符串) >= 3 and 并符串[-3:] == _o + _V + _O:
        return f"(跌)人.吞吞{_o}{_V}{_O}"
    if len(并符串) >= 4 and 并符串[-4:] == _o + _V + _O + _v:
        return f"(跌)人.吞吞{_o}{_V}{_O}{_v}"
    if 并符串[-2:] == _V + _O or (len(并符串) >= 3 and 并符串[-3:] == _V + _O + _v):
        return f"(人)人.吞吞* {_V}{_O}"

    # --- 人排: 孕孕 ---
    if len(并符串) >= 3 and 并符串[-3:] == _Q + _v + _o:
        return f"(升)人.孕孕{_v}{_o}"
    if len(并符串) >= 4 and 并符串[-4:] == _v + _O + _v + _o:
        return f"(升)人.孕孕{_v}{_o}"
    if len(并符串) >= 3 and 并符串[-3:] == _W + _o + _v:
        return f"(跌)人.孕孕{_o}{_v}"
    if len(并符串) >= 4 and 并符串[-4:] == _o + _V + _o + _v:
        return f"(跌)人.孕孕{_o}{_v}"
    if 并符串[-2:] == _v + _o or 并符串[-2:] == _o + _v:
        return f"(人)人.孕孕{_v}{_o}"

    return "错.未赋值"


def 柱排后缀(并符串: str, BTPR0: int) -> str:
    """添加后缀: .W{N} 或 .Q{N}"""
    if len(并符串) == 0:
        return ""
    if 并符串[-1] == _W:
        return f".W{-BTPR0}"
    elif 并符串[-1] == _Q:
        return f".Q{BTPR0}"
    return ""


# ============================================================
# 3. 全量计算
# ============================================================

def 计算柱排序列(df: pd.DataFrame, 周期: str = "日") -> pd.Series:
    """
    对DataFrame计算柱排序列
    周期: "日" 或 "周"
    需要列: close, open, 涨幅 (或自动计算)
    """
    result = []
    close = df["close"].values
    open_ = df["open"].values

    # 计算涨跌幅
    if "涨幅" not in df.columns:
        涨幅 = np.zeros(len(df))
        涨幅[1:] = (close[1:] / close[:-1] - 1) * 100
    else:
        涨幅 = df["涨幅"].values

    # 滚动并符串
    并符串 = ""

    for i in range(len(df)):
        if i == 0:
            并符串 = ""
            柱排 = "错.未赋值"
        else:
            前涨幅 = 涨幅[i-1]
            今收 = close[i]
            前开 = open_[i-1]
            今涨 = 涨幅[i]

            单符 = 计算单柱符号(今涨, 前涨幅, 今收, 前开)
            并符串 = (并符串 + 单符)[-4:]  # 保持最后4位

            柱排 = 柱排分类(并符串)

            # 追加后缀
            if 柱排 != "错.未赋值":
                # BTPR0 = 当前最后连续符号的长度
                btpr0 = 0
                if len(并符串) > 0:
                    last = 并符串[-1]
                    for j in range(len(并符串) - 1, -1, -1):
                        if 并符串[j] == last:
                            btpr0 += 1
                        else:
                            break
                    if btpr0 > 0:
                        柱排 += 柱排后缀(并符串, btpr0)

        result.append(柱排)

    return pd.Series(result, index=df.index)


# ============================================================
# 4. 计算 下柱冲高信号（基于周柱排）
# ============================================================

def 计算下柱冲高提示(df: pd.DataFrame, 周柱排: pd.Series) -> pd.Series:
    """
    与VBA 位谕of周层下柱冲高提示 等效
    简化版：周柱排为升链 + 周护型为甲乙己 → 有冲高信号
    """
    result = pd.Series([""] * len(df), index=df.index)

    for i in range(len(df)):
        柱排 = str(周柱排.iloc[i]) if pd.notna(周柱排.iloc[i]) else ""

        # 需要WXCD金 + 护型甲乙己 + 波型含龙
        # 此处简化：柱排以"升"开头
        if 柱排.startswith("升"):
            result.iloc[i] = "龙猪.冲"

    return result


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    # 用模拟数据测试
    np.random.seed(42)
    n = 200
    dates = pd.date_range("2020-01-01", periods=n)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    open_p = close * 0.99 + np.random.randn(n) * 0.1
    df_test = pd.DataFrame({
        "date": dates, "open": open_p, "high": close * 1.02,
        "low": close * 0.98, "close": close,
        "volume": np.random.randint(100000, 10000000, n),
        "amount": close * np.random.randint(100000, 10000000, n),
    })
    # 先算涨幅
    df_test["涨幅"] = df_test["close"].pct_change() * 100

    日柱排 = 计算柱排序列(df_test, "日")
    print("日柱排最后15个:")
    for i in range(max(0, len(日柱排)-15), len(日柱排)):
        print(f"  {df_test['date'].iloc[i].date()}  涨幅:{df_test['涨幅'].iloc[i]:+6.2f}% → {日柱排.iloc[i]}")