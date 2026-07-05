"""
MP5 止损/再平衡触发器 — 区划变化时自动触发预警

规则：
- 基仓退出：WXZC<0（等价于DJE跌破）
- 浮仓退出：下破DJC
- 板块超限：触发再平衡
"""


def 检查基仓止损(日类BTZE: float, 周类BTZC: float) -> dict:
    """
    检查基仓是否需要止损

    Returns:
        {"需止损": bool, "原因": str}
    """
    if 周类BTZC <= 0:
        return {"需止损": True, "原因": "WXZC<0，基仓强制清仓"}
    if 日类BTZE <= 0:
        return {"需止损": True, "原因": "DJE跌破，全部清仓"}
    return {"需止损": False, "原因": ""}


def 检查浮仓止损(日类BTZC: float) -> dict:
    """
    检查浮仓是否需要止损

    Returns:
        {"需止损": bool, "原因": str}
    """
    if 日类BTZC <= 0:
        return {"需止损": True, "原因": "下破DJC，浮仓退出"}
    return {"需止损": False, "原因": ""}


def 检查板块再平衡(板块仓位: dict, 上限: float = 30.0) -> list:
    """
    检查各板块是否超限，触发再平衡

    Args:
        板块仓位: {板块名称: 仓位比例}
        上限: 单板块上限（默认30%）

    Returns:
        [(板块名称, 当前仓位, 超限量)]
    """
    超限板块 = []
    for 板块, 仓位 in 板块仓位.items():
        if 仓位 > 上限:
            超限板块.append((板块, 仓位, 仓位 - 上限))
    return 超限板块