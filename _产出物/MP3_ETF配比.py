"""
MP3 ETF自动配比 — 单板块超限时超额部分转配ETF

规则：
- 超额部分按比例分配到沪深300ETF/中证500ETF
- ETF本身不计入板块仓位限制
"""


def 计算ETF配比(板块名称: str, 超额比例: float) -> dict:
    """
    计算超额部分的ETF配置方案

    Args:
        板块名称: 超限板块名称
        超额比例: 超出的仓位百分比

    Returns:
        {ETF代码: 建议配置比例}
    """
    # ETF配置模板
    etf_配置 = {
        "510300.SH": 0.6,   # 沪深300ETF — 60%
        "510500.SH": 0.4,   # 中证500ETF — 40%
    }

    return {代码: 比例 * 超额比例 for 代码, 比例 in etf_配置.items()}


def 生成ETF建议(超限板块列表: list) -> str:
    """生成ETF配置建议文本"""
    建议 = []
    for 板块, 超额 in 超限板块列表:
        etf配比 = 计算ETF配比(板块, 超额)
        建议.append(f"{板块}超限{超额:.1f}%，建议转配：")
        for 代码, 比例 in etf配比.items():
            建议.append(f"  {代码}: {比例:.1f}%")
    return "\n".join(建议)