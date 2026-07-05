"""
M2.4 run_backtest.py — 回测运行器

整合 data_loader + strategy + metrics 跑完整回测
"""

import sys
sys.path.insert(0, "_回测框架")

from MC2_1_数据加载 import load_ld_data
from MC2_2_策略引擎 import 运行回测
from MC2_3_评价指标 import 计算完整指标, 打印指标报告
import pandas as pd
import numpy as np


def run_full_backtest(excel_path: str, 股票名: str = None):
    """完整回测流水线（使用真实P&L）"""

    # 1. 加载数据
    df = load_ld_data(excel_path)
    if 股票名 is None:
        股票名 = excel_path.replace("算展D.", "").replace(".xlsx", "")

    print(f"\n{'='*60}")
    print(f"  启动回测: {股票名}")
    print(f"  数据范围: {df['日期'].min()} ~ {df['日期'].max()}")
    print(f"  总行数:   {len(df)}")
    print(f"{'='*60}")

    # 2. 运行策略（含真实P&L）
    结果 = 运行回测(df, 股票名)

    # 3. 从策略引擎拿真实净值
    净值序列 = 结果.get("每日净值", [])
    交易记录 = 结果.get("交易记录", [])

    # 4. 计算指标
    天数 = 结果.get("数据天数", len(df))
    if len(净值序列) > 1:
        指标 = 计算完整指标(净值序列, 交易记录, 天数)
    else:
        指标 = {}

    # 5. 打印报告
    打印指标报告(指标, f"回测报告: {股票名}")
    结果["指标"] = 指标
    结果["净值"] = 净值序列

    return 结果


def run_three_stocks():
    """跑3只股票的回测"""
    股票池 = [
        ("算展D.sz300304.xlsx", "sz300304 云意电气"),
        ("算展D.sz000510.xlsx", "sz000510 新金路"),
        ("算展D.sh600155.xlsx", "sh600155 华创阳安"),
    ]

    汇总 = []
    for 文件, 名字 in 股票池:
        try:
            结果 = run_full_backtest(文件, 名字)
            指标 = 结果.get("指标", {})
            汇总.append({
                "标的": 名字,
                "年化收益率": 指标.get("年化收益率", 0),
                "最大回撤": 指标.get("最大回撤", 0),
                "夏普比率": 指标.get("夏普比率", 0),
                "胜率": 指标.get("胜率", 0),
                "总次数": 指标.get("总次数", 0),
            })
        except Exception as e:
            print(f"\n❌ {文件} 回测失败: {e}")

    # 汇总对比
    print(f"\n{'='*70}")
    print(f"  三股对比汇总")
    print(f"{'='*70}")
    print(f"  {'标的':<20} {'年化':>8} {'回撤':>8} {'夏普':>8} {'胜率':>8} {'次数':>6}")
    print(f"  {'─'*60}")
    for r in 汇总:
        print(f"  {r['标的']:<20} {r['年化收益率']:>7.1%} {r['最大回撤']:>7.1%} {r['夏普比率']:>7.2f} {r['胜率']:>7.1%} {r['总次数']:>5}")
    print(f"{'='*70}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_full_backtest(sys.argv[1])
    else:
        run_three_stocks()
