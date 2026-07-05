"""
MC5.2 每日选股入口 — CLI一键选股

用法：
    python MC5_2_每日选股.py                  # 默认3只测试股
    python MC5_2_每日选股.py 算展D.sz300304.xlsx  # 指定个股
    python MC5_2_每日选股.py --all             # 扫描所有算展D文件
"""

import sys
import os
sys.path.insert(0, "_回测框架")

from MC2_1_数据加载 import load_ld_data
from MC5_1_选股引擎 import 选股, 打印选股结果, 操作模式


def 选股单股(excel_path: str):
    """对单个股票运行选股"""
    df = load_ld_data(excel_path)
    名称 = excel_path.replace("算展D.", "").replace(".xlsx", "")
    结果 = 选股(df, 名称, top_n=5)
    打印选股结果(结果)
    return 结果


def 选股全部():
    """扫描所有算展D文件，批量选股"""
    算展目录 = "."
    算展文件 = [f for f in os.listdir(算展目录) if f.startswith("算展D.") and f.endswith(".xlsx")]

    if not 算展文件:
        print("未找到算展D.*.xlsx 文件")
        return

    print(f"\n发现 {len(算展文件)} 只股票数据")
    print(f"{'='*60}")

    全部推荐 = []
    for 文件 in sorted(算展文件):
        try:
            df = load_ld_data(文件)
            名称 = 文件.replace("算展D.", "").replace(".xlsx", "")
            结果 = 选股(df, 名称, top_n=3)  # 每只最多3个推荐
            全部推荐.extend(结果)
        except Exception as e:
            print(f"  ❌ {文件}: {e}")

    # 按评分排序取Top 5
    全部推荐.sort(key=lambda x: x.综合评分, reverse=True)
    最终推荐 = 全部推荐[:5]

    print(f"\n{'='*60}")
    print(f"  全市场选股汇总 — Top 5 推荐")
    print(f"{'='*60}")
    打印选股结果(最终推荐)

    return 最终推荐


if __name__ == "__main__":
    if "--all" in sys.argv:
        选股全部()
    elif len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                continue
            选股单股(arg)
    else:
        # 默认跑3只测试股
        测试股 = [
            "算展D.sz300304.xlsx",
            "算展D.sz000510.xlsx",
            "算展D.sh600155.xlsx",
        ]
        for 文件 in 测试股:
            print(f"\n{'#'*60}")
            print(f"# 选股: {文件}")
            print(f"{'#'*60}")
            选股单股(文件)
