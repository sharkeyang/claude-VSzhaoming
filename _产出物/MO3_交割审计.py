"""
MO3 交割单合规审计 — 对照四域规则审计历史交易

审计规则：
1. 区划=_空长时是否执行清仓
2. DJE之下是否开仓
3. 浮仓是否超过基仓
"""

from dataclasses import dataclass
from typing import List


@dataclass
class 交易记录:
    日期: str
    标的: str
    方向: str       # "买入" / "卖出"
    数量: int
    价格: float
    金额: float


@dataclass
class 审计结果:
    交易: 交易记录
    合规: bool
    违规原因: str = ""
    严重程度: str = ""  # "严重" / "警告" / "提示"


def 审计单笔交易(交易: 交易记录, 当日区划: str,
                当日DJE: float, 当日收盘: float,
                当前浮仓: int, 当前基仓: int) -> 审计结果:
    """审计单笔交易"""
    违规 = []

    # 规则1：空长区开仓
    if 交易.方向 == "买入" and 当日区划 == "空长":
        违规.append("空长区开仓（严重违规）")

    # 规则2：DJE之下开仓
    if 交易.方向 == "买入" and 当日收盘 < 当日DJE:
        违规.append("DJE之下开仓（严重违规）")

    # 规则3：浮仓超过基仓
    if 当前浮仓 > 当前基仓:
        违规.append(f"浮仓{当前浮仓}超过基仓{当前基仓}（仓位违规）")

    if 违规:
        return 审计结果(
            交易=交易, 合规=False,
            违规原因="；".join(违规),
            严重程度="严重" if "严重" in "".join(违规) else "警告")
    return 审计结果(交易=交易, 合规=True)


def 批量审计(交易列表: List[交易记录],
            区划数据: dict, DJE数据: dict) -> list:
    """批量审计多笔交易"""
    return [审计单笔交易(t, "", 0, 0, 0, 0) for t in 交易列表]