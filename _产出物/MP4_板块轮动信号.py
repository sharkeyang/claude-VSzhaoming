"""
MP4_板块轮动信号.py — 板块轮动分析引擎

数据源：MMMM{日期}.xlsx → .轮 sheet（50个板块日频排名）
分析维度：
  - 短期热点（1-3天）：Hn排名 + #H10
  - 中期趋势（5-10天）：#H30 + #H100
  - 当日预测：Hv强度 + Hn排名变化

输出：板块轮动信号表 + 热点持续概率

用法：
  python "_产出物/MP4_板块轮动信号.py"
  需要先打开 MMMM{日期}.xlsx
"""

import datetime
import os
from collections import defaultdict

# ============================================================
# 读取 .轮 sheet
# ============================================================

def read_轮动数据(wb):
    """从 .轮 sheet 读取50个板块数据"""
    ws = wb.Sheets(".轮")
    sectors = []
    for r in range(2, 200):
        name = ws.Cells(r, 1).value
        if not name:
            break
        # 基础排名
        hv = _f(ws.Cells(r, 2).value)   # 今日H值（强度）
        hn = _f(ws.Cells(r, 3).value)   # 今日H排名
        pv = _f(ws.Cells(r, 4).value)   # 今日P值
        pn = _f(ws.Cells(r, 5).value)   # 今日P排名
        lv = _f(ws.Cells(r, 6).value)   # 今日L值
        ln = _f(ws.Cells(r, 7).value)   # 今日L排名

        # H/L 频次
        h10 = _f(ws.Cells(r, 8).value)  # 10天H次数
        l10 = _f(ws.Cells(r, 9).value)  # 10天L次数
        h30 = _f(ws.Cells(r, 10).value) # 30天H次数
        l30 = _f(ws.Cells(r, 11).value) # 30天L次数
        h100 = _f(ws.Cells(r, 12).value) # 100天H次数
        l100 = _f(ws.Cells(r, 13).value) # 100天L次数

        # H排名历史（最近10天，H1=昨日...H10=10天前）
        h_hist = []
        for c in range(13, 23):  # Col13(H1)~Col22(H10)
            v = _f(ws.Cells(r, c).value)
            if v:
                h_hist.append(v)
            else:
                h_hist.append(99)

        sectors.append({
            "name": str(name).strip(),
            "hv": hv, "hn": hn,
            "pv": pv, "pn": pn,
            "lv": lv, "ln": ln,
            "h10": h10, "l10": l10,
            "h30": h30, "l30": l30,
            "h100": h100, "l100": l100,
            "h_hist": h_hist,  # [H1(昨日), H2, ... H10(10天前)]
        })
    return sectors


def _f(v):
    """安全转float"""
    try:
        return float(v) if v else 0.0
    except (ValueError, TypeError):
        return 0.0


# ============================================================
# 轮动分析引擎
# ============================================================

def analyze_sectors(sectors):
    """对50个板块做多维度评分"""
    results = []
    for s in sectors:
        # 短期动量（1-3天）：今日排名 + 10天H次数 - 10天L次数
        short_momentum = (50 - s["hn"]) * 0.4 + s["h10"] * 3 - s["l10"] * 2

        # 中期趋势（5-10天）：30天H/L净胜
        mid_trend = s["h30"] - s["l30"]

        # 长期趋势（10天+）：100天H/L净胜
        long_trend = s["h100"] - s["l100"]

        # 排名趋势（最近3天排名变化）
        try:
            h1 = s["h_hist"][0] if len(s["h_hist"]) > 0 else 99  # 昨日
            h2 = s["h_hist"][1] if len(s["h_hist"]) > 1 else 99  # 前日
            h3 = s["h_hist"][2] if len(s["h_hist"]) > 2 else 99  # 3天前
            # 今日排名vs昨日排名vs3天前排名
            rank_trend = (h3 - s["hn"]) + (h2 - s["hn"])
        except (IndexError, TypeError):
            rank_trend = 0

        # 综合评分（满分100）
        score = min(100, max(0, short_momentum + mid_trend * 1.5 + rank_trend * 0.5))

        # 热度标签
        if s["hn"] <= 5 and rank_trend > 0:
            tag = "🔥 近期热门"
        elif s["hn"] <= 10 and s["h10"] >= 3:
            tag = "📈 持续活跃"
        elif rank_trend > 5 and s["h10"] >= 2:
            tag = "🚀 新崛起"
        elif s["hn"] > 40 and s["h30"] < 3:
            tag = "❄️ 长期冷淡"
        elif s["hn"] > 30 and rank_trend < -5:
            tag = "📉 快速降温"
        else:
            tag = "➖ 平稳"

        results.append({
            **s,
            "short_momentum": round(short_momentum, 1),
            "mid_trend": mid_trend,
            "long_trend": long_trend,
            "rank_trend": round(rank_trend, 1),
            "score": round(score),
            "tag": tag,
        })

    # 按综合评分排序
    results.sort(key=lambda x: -x["score"])
    return results


# ============================================================
# 预测输出
# ============================================================

def print_report(results, wb_name=""):
    """打印板块轮动报告"""
    print("=" * 90)
    print(f"  板块轮动分析报告 — {wb_name}")
    print(f"  生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 90)
    print(f"{'排名':>3} {'板块':14s} {'Hv':>6} {'Hn':>2} {'#H10':>4} {'#H30':>4} {'#H100':>4} {'短期':>6} {'中期':>4} {'长期':>4} {'趋势':>5} {'评分':>3}  标签")
    print("-" * 90)

    for i, s in enumerate(results, 1):
        print(f"{i:>3} {s['name']:14s} {s['hv']:>6.1f} {s['hn']:>2.0f} {s['h10']:>4.0f} {s['h30']:>4.0f} {s['h100']:>4.0f} {s['short_momentum']:>6.1f} {s['mid_trend']:>4.0f} {s['long_trend']:>4.0f} {s['rank_trend']:>5.1f} {s['score']:>3d}  {s['tag']}")

    # 热点预测
    print()
    print("=" * 90)
    print("  📊 热点预测")
    print("=" * 90)

    hot = [s for s in results if "🔥" in s["tag"] or "🚀" in s["tag"]]
    if hot:
        print(f"  🔥 今日热门（排名前5+上升趋势）：")
        for s in hot[:5]:
            print(f"    {s['name']:14s} 评分={s['score']} Hn={s['hn']:.0f} #{s['tag']}")
    else:
        print("  🔥 今日无明显新热点")

    active = [s for s in results if "📈" in s["tag"]]
    if active:
        print(f"  📈 持续活跃板块（排名前10+10天H≥3）：")
        for s in active[:5]:
            print(f"    {s['name']:14s} 评分={s['score']} #H10={s['h10']:.0f}")

    # 1天/3天/5天/10天预测
    print()
    print("  📅 短期预测（1-3天）：")
    top5 = results[:5]
    for s in top5:
        # 基于#H10和排名趋势预测持续概率
        p1d = min(90, 50 + s["h10"] * 5 + s["rank_trend"] * 2)
        p3d = min(85, 40 + s["h30"] * 2 + s["h10"] * 3)
        print(f"    {s['name']:14s} 1日↑{p1d:.0f}% 3日↑{p3d:.0f}%  (Hn={s['hn']:.0f} #H10={s['h10']:.0f} #H30={s['h30']:.0f})")

    print()
    print("  📅 中期预测（5-10天）：")
    # 中期趋势最好的板块
    mid_sorted = sorted(results, key=lambda x: -x["mid_trend"])[:5]
    for s in mid_sorted:
        p5d = min(80, 30 + s["mid_trend"] * 3)
        p10d = min(75, 20 + s["long_trend"] * 1.5)
        print(f"    {s['name']:14s} 5日↑{p5d:.0f}% 10日↑{p10d:.0f}%  (H30净={s['mid_trend']:.0f} H100净={s['long_trend']:.0f})")

    # 板块轮动总结
    print()
    print("=" * 90)
    print("  💡 轮动策略")
    print("=" * 90)
    print(f"  当前热点数量: {len(hot)}  |  活跃板块: {len(active)}  |  总板块: {len(results)}")
    hots = ", ".join(s['name'] for s in hot[:5])
    print(f"  关注: {hots}")
    print(f"  策略: 短期强者恒强优先，中期趋势确认后加仓")


# ============================================================
# 主入口
# ============================================================

def main():
    import win32com.client

    # 找最近的MMMM文件
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except Exception:
        print("❌ 需要先打开Excel")
        return

    # 找MMMM工作簿
    target = None
    for wb in excel.Workbooks:
        if "MMMM" in wb.Name:
            target = wb
            break

    if not target:
        # 尝试打开最新的
        mmm_dir = os.path.join(os.path.dirname(__file__), "..", "昭明MMMM")
        files = sorted([f for f in os.listdir(mmm_dir) if f.endswith(".xlsx") and "MMMM" in f])
        if files:
            latest = os.path.join(mmm_dir, files[-1])
            target = excel.Workbooks.Open(latest)
            print(f"📂 打开: {latest}")
        else:
            print("❌ 找不到MMMM文件")
            return

    print(f"📊 分析: {target.Name}")
    ws = target.Sheets(".轮")
    sectors = read_轮动数据(target)
    results = analyze_sectors(sectors)
    print_report(results, target.Name)


if __name__ == "__main__":
    main()