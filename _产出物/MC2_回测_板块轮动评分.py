"""
回测_板块轮动评分.py — 验证三因子评分对1/3/5/10/30天的预测能力

方法：遍历20个MMMM文件，每个文件计算板块评分，
      看高评分板块在后续N天后的排名变化。
"""

import datetime
import os
import sys
from collections import defaultdict

MMM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "昭明MMMM"))


def read_轮动(wb):
    """从 .轮 sheet 读取板块数据"""
    ws = wb.Sheets(".轮")
    sectors = []
    for r in range(2, 200):
        name = ws.Cells(r, 1).value
        if not name:
            break
        hn = _f(ws.Cells(r, 3).value, 99)
        hv = _f(ws.Cells(r, 2).value, 0)
        h10 = _f(ws.Cells(r, 8).value, 0)
        l10 = _f(ws.Cells(r, 9).value, 0)
        h30 = _f(ws.Cells(r, 10).value, 0)
        l30 = _f(ws.Cells(r, 11).value, 0)
        h100 = _f(ws.Cells(r, 12).value, 0)
        l100 = _f(ws.Cells(r, 13).value, 0)
        # H1~H3排名历史
        hh = [_f(ws.Cells(r, c).value, 99) for c in range(13, 16)]
        sec = {"name": str(name).strip(), "hn": hn, "hv": hv,
               "h10": h10, "l10": l10, "h30": h30, "l30": l30,
               "h100": h100, "l100": l100, "h1": hh[0], "h2": hh[1], "h3": hh[2]}
        sectors.append(sec)
    return sectors


def calc_score(s):
    """三因子评分（同MP4逻辑）"""
    short = (50 - s["hn"]) * 0.4 + s["h10"] * 3 - s["l10"] * 2
    mid = (s["h30"] - s["l30"]) * 1.5
    rank_trend = (s["h3"] - s["h1"]) + (s["h2"] - s["h1"])
    return short + mid + rank_trend * 0.5


def _f(v, default=0):
    try:
        return float(v) if v else default
    except:
        return default


def main():
    import win32com.client
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False

    # 收集所有文件的数据
    dates = []
    files = sorted([f for f in os.listdir(MMM_DIR) if f.endswith(".xlsx") and "MMMM" in f])
    print(f"共 {len(files)} 个文件")

    all_data = {}  # {date_str: {sector_name: score, hn, ...}}
    for fname in files:
        date_str = fname.replace("MMMM", "").replace(".xlsx", "")
        path = os.path.join(MMM_DIR, fname)
        try:
            wb = excel.Workbooks.Open(path)
            sectors = read_轮动(wb)
            wb.Close(False)
            scores = {}
            for s in sectors:
                scores[s["name"]] = {"score": calc_score(s), "hn": s["hn"]}
            all_data[date_str] = scores
            dates.append(date_str)
        except Exception as e:
            print(f"  ⚠️ {fname}: {e}")

    print(f"成功读取 {len(all_data)} 个文件")

    # 回测：对每个日期，按评分分组，看后续N天的排名变化
    for n_days, label in [(1, "1天"), (3, "3天"), (5, "5天"), (10, "10天")]:
        total_high = 0
        total_low = 0
        high_improve = 0  # 高评分组排名提升的次数
        low_improve = 0   # 低评分组排名提升的次数

        for i, d in enumerate(dates):
            if i + n_days >= len(dates):
                break
            d_next = dates[i + n_days]
            today = all_data[d]
            future = all_data[d_next]

            # 找共同的板块
            common = [s for s in today if s in future]
            if len(common) < 5:
                continue

            # 按今日评分排序，取前30%和后30%
            scored = sorted(common, key=lambda s: today[s]["score"], reverse=True)
            n = max(1, len(scored) // 3)
            high_group = scored[:n]
            low_group = scored[-n:]

            for s in high_group:
                total_high += 1
                if future[s]["hn"] < today[s]["hn"]:
                    high_improve += 1  # hn减小=排名提升
            for s in low_group:
                total_low += 1
                if future[s]["hn"] < today[s]["hn"]:
                    low_improve += 1

        if total_high > 0:
            hr = high_improve / total_high * 100
            lr = low_improve / total_low * 100 if total_low > 0 else 0
            diff = hr - lr
            star = "✅" if diff > 5 else ("⚠️" if diff > 0 else "❌")
            print(f"\n{label}预测:")
            print(f"  高评分组: {total_high}次, 排名提升 {high_improve}次 ({hr:.0f}%)")
            print(f"  低评分组: {total_low}次, 排名提升 {low_improve}次 ({lr:.0f}%)")
            print(f"  差值: {diff:+.0f}% {star}")

    print("\n✅ 回测完成")


if __name__ == "__main__":
    main()