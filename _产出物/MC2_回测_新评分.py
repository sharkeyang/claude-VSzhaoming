"""
回测_新评分.py — 三周期独立评分 + 回测验证

评分设计：
  - 短期（1-3天）：排名趋势动量 = (H3-H1) + (H2-H1)
  - 中期（5-20天）：频次净胜 = #H10 - #L10
  - 长期（20-100天）：累计覆盖 = #H100

先各自独立算分，再尝试两种组合方式：
  A) 等权组合：短期×0.3 + 中期×0.3 + 长期×0.4
  B) 三层过滤：先过长期→中期→短期筛选
"""

import os
from collections import defaultdict

MMM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "昭明MMMM"))


def _f(v, default=0):
    try:
        return float(v) if v else default
    except:
        return default


def read_轮动(wb):
    ws = wb.Sheets(".轮")
    sectors = []
    for r in range(2, 200):
        name = ws.Cells(r, 1).value
        if not name:
            break
        hn = _f(ws.Cells(r, 3).value, 99)
        h10 = _f(ws.Cells(r, 8).value, 0)
        l10 = _f(ws.Cells(r, 9).value, 0)
        h30 = _f(ws.Cells(r, 10).value, 0)
        l30 = _f(ws.Cells(r, 11).value, 0)
        h100 = _f(ws.Cells(r, 12).value, 0)
        hh = [_f(ws.Cells(r, c).value, 99) for c in range(13, 16)]
        sectors.append({
            "name": str(name).strip(), "hn": hn,
            "h10": h10, "l10": l10, "h30": h30, "l30": l30, "h100": h100,
            "h1": hh[0], "h2": hh[1], "h3": hh[2],
        })
    return sectors


# ═══════════════════════════════════════════════════════════
# 三个周期独立指标
# ═══════════════════════════════════════════════════════════

def score_short(s):
    """短期：排名趋势动量（正=排名在上升）"""
    return (s["h3"] - s["h1"]) + (s["h2"] - s["h1"])


def score_mid(s):
    """中期：10天频次净胜（正=高排位比低排位多）"""
    return s["h10"] - s["l10"]


def score_long(s):
    """长期：100天累计覆盖度"""
    return s["h100"]


def score_combo_equal(s):
    """组合A：等权"""
    return score_short(s) * 0.3 + score_mid(s) * 0.3 + score_long(s) * 0.4


def score_combo_filter(s):
    """组合B：三层过滤（先长后短）"""
    # 长期不过关直接0分
    if score_long(s) < 10:
        return 0
    # 中期一般
    if score_mid(s) < 1:
        return score_short(s) * 0.3 + 10
    # 全部通过
    return score_short(s) * 0.5 + score_mid(s) * 0.3 + score_long(s) * 0.2


# ═══════════════════════════════════════════════════════════
# 回测引擎
# ═══════════════════════════════════════════════════════════

def backtest(all_data, dates, score_func, name):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")

    for n_days, label in [(1, "1天"), (3, "3天"), (5, "5天"), (10, "10天")]:
        th, tl, hi, li = 0, 0, 0, 0
        for i, d in enumerate(dates):
            if i + n_days >= len(dates):
                break
            d_next = dates[i + n_days]
            today, future = all_data[d], all_data[d_next]
            common = [s for s in today if s in future]
            if len(common) < 5:
                continue
            scored = sorted(common, key=lambda s: score_func(today[s]), reverse=True)
            n = max(1, len(scored) // 3)
            for s in scored[:n]:
                th += 1
                if future[s]["hn"] < today[s]["hn"]:
                    hi += 1
            for s in scored[-n:]:
                tl += 1
                if future[s]["hn"] < today[s]["hn"]:
                    li += 1
        hr = hi / th * 100 if th else 0
        lr = li / tl * 100 if tl else 0
        diff = hr - lr
        tag = "有效" if diff > 5 else ("弱" if diff > 0 else "反指")
        print(f"  {label}: 高分组{hi}/{th}({hr:.0f}%) 低分组{li}/{tl}({lr:.0f}%) 差值{diff:+.0f}% [{tag}]")


# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════

def main():
    import win32com.client
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False

    files = sorted([f for f in os.listdir(MMM_DIR) if f.endswith(".xlsx") and "MMMM" in f])
    print(f"文件数: {len(files)}")

    all_data = {}
    dates = []
    for fname in files:
        date_str = fname.replace("MMMM", "").replace(".xlsx", "")
        path = os.path.join(MMM_DIR, fname)
        try:
            wb = excel.Workbooks.Open(path)
            sectors = read_轮动(wb)
            wb.Close(False)
            all_data[date_str] = {s["name"]: s for s in sectors}
            dates.append(date_str)
        except Exception as e:
            print(f"  {fname}: {e}")

    print(f"成功读取: {len(all_data)}个文件")

    # 回测各个指标
    backtest(all_data, dates, lambda s: score_short(s), "短期：排名趋势动量")
    backtest(all_data, dates, lambda s: score_mid(s), "中期：频次净胜(#H10-#L10)")
    backtest(all_data, dates, lambda s: score_long(s), "长期：累计覆盖#H100")
    backtest(all_data, dates, lambda s: score_combo_equal(s), "组合A：等权(短3+中3+长4)")
    backtest(all_data, dates, lambda s: score_combo_filter(s), "组合B：三层过滤(先长后短)")

    print("\n✅ 回测完成")


if __name__ == "__main__":
    main()