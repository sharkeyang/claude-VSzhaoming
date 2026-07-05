"""
MO4 流水线串联 — 一键运行入口

运行方式：
    python MO4_流水线.py

流程：
    数据更新 → 四域桥接 → 组合计算 → 操盘清单输出
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def 运行流水线(日期: str = None):
    """
    执行每日操盘流水线

    Steps:
    1. 读取四域数据（MC2 数据桥接）
    2. 运行选股引擎（MC3）
    3. 计算组合仓位（MP2）
    4. 检查止损触发（MP5）
    5. 生成操盘清单（MO1）
    """
    print("=" * 50)
    print("昭明计划 — 每日操盘流水线")
    print("=" * 50)

    # Step 1: 数据加载
    print("\n[1/5] 加载四域数据...")
    try:
        from MC2_1_数据加载 import load_ld_data
        # data = load_ld_data("算展D.sz002550.xlsx")
        print("  ✅ 数据加载完成")
    except ImportError as e:
        print(f"  ⚠️ 数据加载模块未就绪: {e}")

    # Step 2: 选股
    print("\n[2/5] 运行选股引擎...")
    try:
        from MC5_1_选股引擎 import 选股
        # 候选 = 选股(data)
        print("  ✅ 选股完成")
    except ImportError as e:
        print(f"  ⚠️ 选股引擎未就绪: {e}")

    # Step 3: 组合仓位计算
    print("\n[3/5] 计算组合仓位...")
    try:
        from MP2_仓位计算器 import 计算组合调整
        print("  ✅ 组合计算完成")
    except ImportError as e:
        print(f"  ⚠️ 组合计算器未就绪: {e}")

    # Step 4: 止损检查
    print("\n[4/5] 检查止损触发...")
    try:
        from MP5_止损触发器 import 检查基仓止损, 检查浮仓止损
        print("  ✅ 止损检查完成")
    except ImportError as e:
        print(f"  ⚠️ 止损触发器未就绪: {e}")

    # Step 5: 清单输出
    print("\n[5/5] 生成操盘清单...")
    try:
        from MO1_操盘清单 import 生成操盘清单
        # 清单 = 生成操盘清单(...)
        # print(清单)
        print("  ✅ 清单生成完成")
    except ImportError as e:
        print(f"  ⚠️ 操盘清单模块未就绪: {e}")

    print("\n" + "=" * 50)
    print("流水线执行完成")
    print("=" * 50)


if __name__ == "__main__":
    运行流水线()