"""
MC3_策传_看板.py — 实时策传看板 v4 (Flask + ECharts)

数据流:
  VBA → Z sheet → Python读取 → AKShare行情+分时
  → Flask REST API → ECharts前端渲染

启动:
  python "_产出物/MC3_策传_看板.py"
  浏览器打开 http://127.0.0.1:5000

配置: MC3_策传_看板_配置.py
"""

import datetime
import os
import re
import time
import threading
from collections import defaultdict

from flask import Flask, jsonify, render_template_string

from MC3_策传_看板_配置 import (
    EXCEL_PATH, HTML_REFRESH_SECONDS, VBA_REFRESH_SECONDS, VBA_宏名称,
    COL_CODE, COL_NAME, COL_CANGZHU, COL_HANGLANG, COL_AMOUNT, COL_SHARES, COL_COST, COL_PROFIT,
    COL_SIYU_ZHOU, COL_SIYU_RI, COL_RI_CENGDUAN, COL_RI_JIJING,
    COL_CE_CHANGJICANG, COL_CE_ZHOUFUCANG, COL_CE_RIFUCANG, COL_CECHUAN,
    SIYU_COLORS, KEY_INDUSTRIES, AMOUNT_WAN_THRESHOLD,
    INTRADAY_LOOKBACK_DAYS, INTRADAY_FETCH_TOP, BROAD_INDEX_TOP, INDUSTRY_TOP,
    SCORE_四域, SCORE_日段, SCORE_仓日_有值, SCORE_MAX,
)

app = Flask(__name__)

# ============================================================
# 全局缓存（避免每次请求重复读Excel+AKShare）
# ============================================================
_cache = {"data": None, "timestamp": None}
_cache_lock = threading.Lock()

# ============================================================
# Excel连接与数据读取（原样保留）
# ============================================================

def connect_excel():
    import win32com.client
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
    except Exception:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
    target_lower = EXCEL_PATH.lower()
    for wb in excel.Workbooks:
        try:
            fn = str(wb.FullName)
            if fn.lower() == target_lower:
                return excel, wb
        except Exception:
            continue
    wb = excel.Workbooks.Open(EXCEL_PATH)
    return excel, wb


def call_vba_update(excel, wb):
    ws = wb.Sheets("Z")
    ws.Activate()
    excel.Application.Run(VBA_宏名称)
    excel.Application.CalculateUntilAsyncQueriesDone()
    time.sleep(1)


def read_echuan_data(ws):
    positions = []
    indices = {}
    current_section = None
    row = 2
    max_row = ws.UsedRange.Rows.Count
    while row <= max_row:
        c1 = ws.Cells(row, 1).value
        if c1 is None:
            break
        val = str(c1).strip()
        if row == 2 and val in ("sSCC", "sSSC", "sSSS", "cCCC"):
            row += 1
            continue
        if "核心" in val:
            current_section = val
            indices[current_section] = indices.get(current_section, [])
            row += 1
            continue
        name = ws.Cells(row, COL_NAME).value or ""
        cangzhu = ws.Cells(row, COL_CANGZHU).value
        record = {
            "code": val,
            "name": name,
            "cangzhu": str(cangzhu or ""),
            "hanglang": str(ws.Cells(row, COL_HANGLANG).value or ""),
            "金额": _to_float(ws.Cells(row, COL_AMOUNT).value) / 10.0,
            "股数": _to_float(ws.Cells(row, COL_SHARES).value),
            "成本": _to_float(ws.Cells(row, COL_COST).value),
            "肉垫": _to_float(ws.Cells(row, COL_PROFIT).value),
            "四域周": str(ws.Cells(row, COL_SIYU_ZHOU).value or ""),
            "四域日": str(ws.Cells(row, COL_SIYU_RI).value or ""),
            "日层段": str(ws.Cells(row, COL_RI_CENGDUAN).value or ""),
            "日机警": str(ws.Cells(row, COL_RI_JIJING).value or ""),
            "策长基仓": str(ws.Cells(row, COL_CE_CHANGJICANG).value or ""),
            "策周浮仓": str(ws.Cells(row, COL_CE_ZHOUFUCANG).value or ""),
            "策日浮仓": str(ws.Cells(row, COL_CE_RIFUCANG).value or ""),
            "策传": str(ws.Cells(row, COL_CECHUAN).value or ""),
        }
        if cangzhu:
            positions.append(record)
        elif current_section:
            indices[current_section].append(record)
        row += 1
    return positions, indices


def _to_float(v):
    try:
        return float(v) if v else 0.0
    except (ValueError, TypeError):
        return 0.0


# ============================================================
# AKShare 实时行情（原样保留）
# ============================================================

def fetch_market_prices(codes):
    try:
        import akshare as ak
        spot = ak.stock_zh_a_spot()
    except Exception as e:
        print(f"行情获取失败: {e}")
        return {}
    price_map = {}
    for _, row in spot.iterrows():
        code = str(row["代码"]).strip()
        price_map[code] = {
            "最新价": _to_float(row.get("最新价")),
            "涨跌幅": _to_float(row.get("涨跌幅")),
            "昨收": _to_float(row.get("昨收")),
            "今开": _to_float(row.get("今开")),
            "最高": _to_float(row.get("最高")),
            "最低": _to_float(row.get("最低")),
            "成交量": _to_float(row.get("成交量")),
            "成交额": _to_float(row.get("成交额")),
        }
    result = {}
    for c in codes:
        if c in price_map:
            result[c] = price_map[c]
    return result


def fetch_intraday(symbol):
    """获取某只股票的当日1分钟K线，带重试"""
    for attempt in range(2):
        try:
            import akshare as ak
            df = ak.stock_zh_a_minute(symbol=symbol, period="1")
            if df is None or len(df) == 0:
                if attempt == 0:
                    time.sleep(2)
                continue
            today = datetime.date.today().strftime("%Y-%m-%d")
            for d in range(0, INTRADAY_LOOKBACK_DAYS + 1):
                day = (datetime.date.today() - datetime.timedelta(days=d)).strftime("%Y-%m-%d")
                day_data = df[df["day"].str.startswith(day)]
                if len(day_data) > 0:
                    return [{"t": row["day"], "p": float(row["close"]), "v": float(row["volume"])}
                            for _, row in day_data.iterrows()]
            return []
        except Exception:
            if attempt == 0:
                time.sleep(2)
            continue
    return []


# ============================================================
# 策传解析 + 评分（原样保留）
# ============================================================

def parse_echuan(cc_str):
    result = {}
    if not cc_str:
        return result
    parts = cc_str.split(" | ")
    for i, k in enumerate(["四域", "日级别", "波形", "机阱", "冲高"]):
        if i < len(parts):
            result[k] = parts[i]
    if parts:
        m = re.search(r"四域=(\S+)", parts[0])
        if m:
            result["_四域值"] = m.group(1)
    if len(parts) > 1:
        for k in ["仓日", "日段", "日信号"]:
            m = re.search(rf"{k}=(\S+)", parts[1])
            if m:
                result[f"_{k}"] = m.group(1)
    return result


def calc_score(cc):
    siyu = cc.get("_四域值", "")
    riduan = cc.get("_日段", "")
    cangri = cc.get("_仓日", "")
    s = SCORE_四域.get(siyu, 0)
    s += SCORE_日段.get(riduan, 0)
    if cangri and cangri != "无":
        s += SCORE_仓日_有值
    return min(s, SCORE_MAX)


# ============================================================
# 盯盘规则 + 策略（原样保留）
# ============================================================

def apply_watch_rules(positions, market_prices):
    rules = []
    board_weights = defaultdict(float)
    total_amt = sum(abs(p.get("金额", 0)) for p in positions)
    for p in positions:
        cc = parse_echuan(p.get("策传", ""))
        siyu = cc.get("_四域值", "")
        riduan = cc.get("_日段", "")
        code = p["code"]
        name = p["name"]
        mp = market_prices.get(code, {})
        chg = mp.get("涨跌幅", 0)
        low = mp.get("最低", 0)
        high = mp.get("最高", 0)

        if siyu == "空长" and riduan == "持主":
            rules.append({"type": "策略冲突", "msg": f"{name}: 周级空长但日线持主"})
        if chg > 8:
            rules.append({"type": "涨幅过大", "msg": f"{name}: 涨{chg:.1f}%，猴市见好就收"})
        elif chg < -5:
            rules.append({"type": "跌幅较大", "msg": f"{name}: 跌{chg:.1f}%，触发止损？"})
        if siyu in ("空看", "空长"):
            rules.append({"type": "空头警告", "msg": f"{name}: 四域{siyu}，减仓或止损"})
        cost = p.get("成本", 0)
        if cost > 0 and low > 0 and low <= cost * 0.95:
            rules.append({"type": "破成本", "msg": f"{name}: 最低{low:.1f}破95%成本线"})
        hl = p.get("hanglang", "")
        amt = abs(p.get("金额", 0))
        if hl and total_amt > 0:
            board_weights[hl] += amt / total_amt * 100
    for board, pct in sorted(board_weights.items(), key=lambda x: -x[1]):
        if pct > 30:
            rules.append({"type": "板块集中", "msg": f"{board}占比{pct:.0f}%，超30%风控线"})
    return rules


def generate_trading_strategy(cc, market_price):
    strategies = []
    siyu = cc.get("_四域值", "")
    riduan = cc.get("_日段", "")
    chg = market_price.get("涨跌幅", 0)
    close = market_price.get("最新价", 0)
    open_p = market_price.get("今开", 0)
    strategies.append("🐵 猴市：见好就收")
    if open_p > 0 and close > 0:
        if close > open_p:
            strategies.append(f"📈 收涨{chg:.1f}%，关注持续性")
        else:
            strategies.append(f"📉 收跌{chg:.1f}%，注意支撑")
    if siyu == "多长":
        strategies.append("✅ 多头趋势，持有为主")
    elif siyu == "多被":
        strategies.append("⚠️ 被动跟随，等转强")
    elif siyu == "空看":
        strategies.append("🟣 空头观望，不参与")
    elif siyu == "空长":
        strategies.append("🔴 空头趋势，逢高减仓")
    if riduan == "持主":
        strategies.append("🔹 持主，关注止盈")
    elif riduan == "卖浮":
        strategies.append("🟠 浮仓卖出，执行减仓")
    return strategies


# ============================================================
# 数据采集任务（后台线程）
# ============================================================

def refresh_data():
    """采集全部数据，写入全局缓存"""
    global _cache
    excel = None
    wb = None
    for retry in range(3):
        try:
            excel, wb = connect_excel()
            break
        except Exception as e:
            print(f"  ⚠️ Excel连接失败(第{retry+1}次): {e}")
            if retry < 2:
                time.sleep(3)
            else:
                print("  ❌ Excel连接失败，跳过本轮刷新")
                return
    if excel is None or wb is None:
        return

    try:
        ws = wb.Sheets("Z")

        # 读取策传
        positions, indices = read_echuan_data(ws)
        if not positions:
            print("  ⚠️ 未读取到持仓数据，跳过本轮")
            return

        # 收集代码
        all_codes = [p["code"] for p in positions]
        for sec in indices.values():
            all_codes.extend(i["code"] for i in sec)
        all_codes = list(set(all_codes + ["sh000001", "sh000016"]))

        # 行情
        market_prices = fetch_market_prices(all_codes)

        # 分时（只取前N只持仓+指数）
        need = [p["code"] for p in positions[:INTRADAY_FETCH_TOP]]
        broad = []
        ividx = -1
        # 分时：先拿前5只，其余交给后台线程慢慢补
        need = [p["code"] for p in positions[:5]]
        intraday = {}
        for c in need:
            d = fetch_intraday(c)
            if d:
                intraday[c] = d

        # 后台线程：逐步补齐所有持仓的分时图
        all_pos_codes = [p["code"] for p in positions]
        missing = [c for c in all_pos_codes if c not in intraday]

        def _fill_intraday():
            """后台逐个补齐分时图，每只间隔1.5秒"""
            filled = 0
            for i, c in enumerate(missing):
                print(f"  [补齐{i+1}/{len(missing)}] 获取 {c}...", end=" ", flush=True)
                try:
                    d = fetch_intraday(c)
                    if d:
                        with _cache_lock:
                            if _cache.get("data"):
                                _cache["data"]["intraday"][c] = d
                        filled += 1
                        print(f"✅ {len(d)}条")
                    else:
                        print("❌ 空")
                except Exception as e:
                    print(f"❌ {e}")
                time.sleep(1.5)
            print(f"  后台补齐: {filled}/{len(missing)}只完成")

        if missing:
            print(f"  🚀 启动后台补齐线程: {len(missing)}只")
            t = threading.Thread(target=_fill_intraday, daemon=True)
            t.start()

        # 解析指数分类
        ci = indices.get("核心指数", [])
        ividx2 = -1
        for i, item in enumerate(ci):
            if "行业" in str(item.get("code", "")) and not item.get("name"):
                ividx2 = i
        all_idx2 = [item for item in ci if item.get("code") and "行业" not in str(item.get("code", ""))]
        broad_idx = all_idx2[:ividx2] if ividx2 > 1 else all_idx2[:6]
        industry_idx = all_idx2[ividx2:] if ividx2 > 2 else []

        siyu_order = {"多长": 0, "多被": 1, "空看": 2, "空长": 3}
        positions.sort(key=lambda p: (siyu_order.get(p.get("四域周", ""), 9), p.get("name", "")))

        total_amt = sum(abs(p.get("金额", 0)) for p in positions)
        total_profit = sum(p.get("肉垫", 0) for p in positions)
        watch_rules = apply_watch_rules(positions, market_prices)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with _cache_lock:
            _cache["data"] = {
                "timestamp": timestamp,
                "positions": positions,
                "indices": {
                    "core": broad_idx,
                    "industry": industry_idx,
                    "raw": {k: v for k, v in indices.items()},
                },
                "market_prices": market_prices,
                "intraday": {k: v for k, v in intraday.items()},
                "watch_rules": watch_rules,
                "total_amt": total_amt,
                "total_profit": total_profit,
            }
            _cache["timestamp"] = timestamp
        print(f"[{timestamp}] 数据刷新完成: {len(positions)}仓 {len(market_prices)}行情 {len(intraday)}分时")
    except Exception as e:
        import traceback
        print(f"数据刷新失败: {e}")
        traceback.print_exc()


def _format_amt(amt):
    if amt < AMOUNT_WAN_THRESHOLD:
        return f"{amt * 10000:.0f}"
    return f"{amt:.1f}w"


# ============================================================
# Flask API
# ============================================================

@app.route("/api/data")
def api_data():
    with _cache_lock:
        d = _cache.get("data")
    if not d:
        return jsonify({"loading": True, "msg": "数据采集中，请稍候..."})
    return jsonify(d)


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


# ============================================================
# HTML 模板（ECharts 前端）
# ============================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>昭明计划 · 策传看板 v4</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:#0a0e17; color:#e0e0e0; }
.container { max-width:1500px; margin:0 auto; padding:12px; }

/* 顶栏 */
.header {
    background:linear-gradient(135deg,#1a237e 0%,#0d1b2a 100%); border-radius:10px;
    padding:14px 20px; margin-bottom:12px; border:1px solid #2a3a5e;
}
.header-title { font-size:20px; font-weight:700; color:#fff; display:flex; align-items:center; gap:8px; }
.logo { font-size:22px; }
.version { font-size:10px; color:#546e7a; background:#141b2d; padding:1px 6px; border-radius:3px; }
.header-info { display:flex; flex-wrap:wrap; gap:12px; font-size:12px; color:#90a4ae; margin-top:6px; }
.meta-item { display:inline-flex; align-items:center; gap:3px; }

/* Portfolio行 */
.portfolio-row { display:flex; gap:10px; margin-bottom:12px; }
.pie-card { background:#0d1520; border-radius:8px; padding:8px; border:1px solid #1a2540; flex:1; min-width:0; }
.pie-card-right { flex:1; min-width:0; }
.pie-card-wide { flex:1; min-width:0; }
.pie-title { font-size:13px; font-weight:600; color:#b0bec5; margin-bottom:6px; }
#pieChart { width:100%; height:200px; }
.stats-grid { display:grid; grid-template-columns:1fr 1fr; gap:3px; font-size:10px; }
.s-item { background:#0a0e17; border-radius:3px; padding:2px 6px; display:flex; justify-content:space-between; }
.s-item label { font-size:9px; color:#546e7a; }
.s-item span { font-size:10px; font-weight:600; }
.s-item label { font-size:11px; color:#546e7a; }
.s-item span { font-size:12px; font-weight:600; }

.section { margin-bottom:16px; }
.section-title {
    font-size:13px; font-weight:600; color:#b0bec5; margin-bottom:6px;
    display:flex; align-items:center; gap:8px; padding-bottom:4px; border-bottom:1px solid #1a2540;
}
.section-count { font-size:10px; color:#78909c; background:#141b2d; padding:1px 8px; border-radius:10px; }

/* 策卡 */
.card { background:#0d1520; border-radius:6px; overflow:hidden; border-left:3px solid #333; margin-bottom:0; }
.card-多长 { border-left-color:#00c853; }
.card-多被 { border-left-color:#ffc107; }
.card-空看 { border-left-color:#5c2d82; }
.card-空长 { border-left-color:#d32f2f; }
.card-top { padding:5px 8px 3px; background:#0d1520; }
.row1 { display:flex; flex-wrap:wrap; align-items:center; gap:3px 6px; margin-bottom:2px; }
.row2 { display:flex; flex-wrap:wrap; align-items:center; gap:4px; }
.card-name { font-size:13px; font-weight:700; color:#e8eaf6; }
.card-code { font-size:9px; color:#546e7a; font-family:monospace; }
.card-tag { font-size:9px; padding:0 5px; border-radius:2px; background:#1a2a4a; color:#5c6bc0; white-space:nowrap; }
.score-badge { font-size:10px; padding:0 6px; border-radius:2px; background:#1a2540; color:#ffc107; font-weight:600; }

.card-body { display:flex; gap:0; }
.card-left { flex:1; min-width:0; padding:4px 8px 6px; border-right:1px solid #1a2540; }
.card-right { flex:1; min-width:240px; padding:4px 8px 6px; }

.info-title { font-size:10px; font-weight:600; color:#78909c; margin-bottom:2px; margin-top:4px; }
.info-title:first-child { margin-top:0; }

.quote-table { width:100%; border-collapse:collapse; font-size:10px; }
.quote-table td { padding:1px 4px; color:#90a4ae; }
.quote-table td:nth-child(odd) { color:#546e7a; width:32px; }
.quote-table td:nth-child(even) { font-weight:600; }

.chart-wrap { background:#0a0e17; border-radius:4px; border:1px solid #1a2540; height:140px; width:100%; }

.strat-box { background:#0a0e17; border-radius:3px; padding:3px 5px; border:1px solid #1a2540; }
.strat-item { font-size:10px; color:#90a4ae; line-height:1.5; padding:1px 0; }

.questions { background:#0a0e17; border-radius:3px; padding:3px 5px; border:1px solid #1a2540; }
.q-item { font-size:10px; color:#90a4ae; line-height:1.4; padding:1px 0; display:flex; gap:3px; }
.q-type { font-size:8px; padding:0 3px; border-radius:2px; background:#1a2540; color:#5c6bc0; min-width:40px; text-align:center; flex-shrink:0; }

.cc-table { width:100%; border-collapse:collapse; }
.cc-table tr + tr { border-top:1px solid #0d1520; }
.cc-num { width:16px; font-size:8px; color:#546e7a; padding:1px 0; text-align:center; }
.cc-label { width:26px; font-size:9px; color:#546e7a; padding:1px 2px; vertical-align:top; white-space:nowrap; }
.cc-val { font-size:9px; color:#90a4ae; padding:1px 0; word-break:break-all; font-family:Consolas,monospace; }

.card-divider { height:1px; background:linear-gradient(90deg, transparent, #1a3a5e, transparent); }

.rules-box { background:#0d1520; border-radius:6px; padding:8px 10px; border:1px solid #1a2540; }
.rule-item { font-size:12px; padding:4px 0; display:flex; gap:6px; }
.rule-type { font-size:10px; padding:0 6px; border-radius:2px; background:#1a2540; color:#5c6bc0; min-width:70px; text-align:center; }

.index-block { background:#0d1520; border-radius:6px; padding:8px; border:1px solid #1a2540; }
.index-table { width:100%; border-collapse:collapse; font-size:11px; }
.index-table th { text-align:left; padding:4px 8px; border-bottom:1px solid #1a2540; color:#546e7a; font-weight:500; }
.index-table td { padding:3px 8px; border-bottom:1px solid #0d1520; color:#b0bec5; }

.badge { display:inline-flex; align-items:center; gap:2px; padding:0 6px; border-radius:2px; font-size:10px; font-weight:600; color:#fff; white-space:nowrap; }
.tag-dense { display:inline-block; padding:0 4px; border-radius:2px; font-size:9px; background:#1a2540; color:#78909c; }

.green { color:#4caf50 !important; }
.red { color:#ef5350 !important; }
.footer { text-align:center; padding:16px; font-size:10px; color:#37474f; }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="header-title">
            <span class="logo">📊</span>
            昭明计划 · 策传看板 <span class="version">v4</span>
        </div>
        <div class="header-info" id="headerInfo">
            <span>加载中...</span>
        </div>
        <div id="debugInfo" style="font-size:10px;color:#546e7a;margin-top:4px">初始化中...</div>
    </div>

    <div class="portfolio-row">
        <div class="pie-card"><div class="pie-title">持仓四域分布</div><div id="pieChart"></div></div>
        <div class="pie-card pie-card-right" id="boardSection"><div class="pie-title">板块集中度</div><div id="boardList"></div></div>
        <div class="pie-card pie-card-wide" id="statsSection"><div class="pie-title">组合概览</div><div class="stats-grid" id="statsGrid"></div></div>
    </div>

    <div class="section">
        <div class="section-title">🔔 盯盘注意点 <span class="section-count" id="ruleCount">0 条</span></div>
        <div class="rules-box" id="rulesBox"></div>
    </div>

    <div class="section">
        <div class="section-title">💼 策卡 <span class="section-count" id="posCount">0 只</span></div>
        <div id="posCards"></div>
    </div>

    <div class="section">
        <div class="section-title">📋 核心宽基 <span class="section-count" id="coreCount">0 只</span></div>
        <div id="coreCards"></div>
    </div>

    <div class="section" id="keyIndustrySection" style="display:none">
        <div class="section-title">🎯 重点行业 <span class="section-count" id="keyCount">0 只</span></div>
        <div id="keyCards"></div>
    </div>

    <div class="section" id="otherIdxSection" style="display:none">
        <div class="section-title">📋 其他指数 <span class="section-count" id="otherCount">0 只</span></div>
        <div class="index-block"><table class="index-table"><thead><tr><th>代码</th><th>名称</th><th>四域</th><th>策分</th><th>最新价</th><th>涨跌幅</th></tr></thead><tbody id="otherIdxBody"></tbody></table></div>
    </div>

    <div class="footer">昭明计划 · 策传系统 v4 | 数据: Excel + AKShare | 图表: ECharts</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script>
const SIYU_COLORS = {"多长":"#00c853","多被":"#ffc107","空看":"#5c2d82","空长":"#d32f2f"};
const AMT_WAN_THRESHOLD = 5;

function fmtAmt(amt) {
    return amt < AMT_WAN_THRESHOLD ? (amt*10000).toFixed(0) : amt.toFixed(1)+'w';
}

function badge(siyu) {
    const c = SIYU_COLORS[siyu] || '#666';
    const icon = {'多长':'🟢','多被':'🟡','空看':'🟣','空长':'🔴'}[siyu] || '⚪';
    return '<span class="badge" style="background:'+c+'">'+icon+' '+siyu+'</span>';
}

function parseCC(ccStr) {
    const r = {};
    if (!ccStr) return r;
    const parts = ccStr.split(' | ');
    ['四域','日级别','波形','机阱','冲高'].forEach((k,i)=>{ if(i<parts.length) r[k]=parts[i]; });
    if(parts[0]) { const m=parts[0].match(/四域=(\S+)/); if(m) r._四域=m[1]; }
    if(parts[1]) { ['仓日','日段','日信号'].forEach(k=>{ const m=parts[1].match(new RegExp(k+'=(\\S+)')); if(m) r['_'+k]=m[1]; }); }
    return r;
}

function renderStrategies(strats) {
    return strats.map(s=>'<div class="strat-item">'+s+'</div>').join('');
}

function renderQuestions(cc) {
    const qs = [];
    const sy = cc._四域||'', rd=cc._日段||'', cr=cc._仓日||'';
    if(sy=='多长') qs.push(['四域多长','✅ 趋势完整，持有']);
    else if(sy=='多被') qs.push(['四域多被','⚠️ 被动跟随，等转强']);
    else if(sy=='空看') qs.push(['四域空看','🟣 空头观望']);
    else if(sy=='空长') qs.push(['四域空长','🔴 空头趋势']);
    if(rd=='持主') qs.push(['日段持主','🔹 持主，关注止盈']);
    else if(rd=='卖浮') qs.push(['日段卖浮','🟠 浮仓卖出']);
    else if(!rd&&cr=='无') qs.push(['日段空','⚪ DJE之下']);
    if(cr=='无') qs.push(['仓日无','📉 无均线支撑']);
    return qs.map(q=>'<div class="q-item"><span class="q-type">'+q[0]+'</span> '+q[1]+'</div>').join('');
}

// ECharts 暗色主题
const DARK_THEME = {
    backgroundColor: 'transparent',
    textStyle: {color:'#b0bec5'},
    xAxis: {axisLine:{lineStyle:{color:'#1a2540'}}, axisLabel:{color:'#546e7a',fontSize:9}},
    yAxis: {axisLine:{lineStyle:{color:'#1a2540'}}, axisLabel:{color:'#546e7a',fontSize:9}},
    splitLine: {lineStyle:{color:'#0d1520'}},
};

let pieChart = null;
let intradayCharts = {};

function initCharts() {
    try {
        if (typeof echarts !== 'undefined') {
            pieChart = echarts.init(document.getElementById('pieChart'), 'dark', {renderer:'canvas'});
        }
    } catch(e) { console.log('ECharts init error:', e); }
}

function updatePie(positions) {
    if (!pieChart) return;
    const bySy = {};
    positions.forEach(p => {
        const cc = parseCC(p.策传);
        const sy = cc._四域 || p.四域周 || '其他';
        bySy[sy] = (bySy[sy]||0) + Math.abs(p.金额||0);
    });
    const total = Object.values(bySy).reduce((a,b)=>a+b,0);
    const order = ['多长','多被','空看','空长'];
    const data = order.filter(k => bySy[k]).map(k => ({
        name: k, value: bySy[k],
        itemStyle: {color: SIYU_COLORS[k]||'#666'}
    }));
    pieChart.setOption({
        tooltip: {trigger:'item', formatter:'{b}: {c}万 ({d}%)'},
        legend: {
            orient:'vertical', left:'5%', top:'center',
            textStyle:{color:'#b0bec5',fontSize:10},
            itemWidth:10, itemHeight:10,
            formatter: function(name) {
                const v = bySy[name]||0;
                const pct = total>0 ? (v/total*100).toFixed(0) : 0;
                return name + '  ' + pct + '%(' + v.toFixed(0) + 'w)';
            }
        },
        series: [{
            type:'pie', radius:['30%','65%'],
            center:['65%','50%'],
            data: data,
            label: {show:false},
            labelLine: {show:false},
            itemStyle: {borderColor:'#0a0e17',borderWidth:1},
        }],
        backgroundColor: 'transparent',
    });
}

function updateIntraday(containerId, intradayData, mp) {
    const dom = document.getElementById(containerId);
    if (!dom) return;
    // 清除旧内容
    dom.innerHTML = '';
    let chart = intradayCharts[containerId];
    if (!chart) {
        chart = echarts.init(dom, 'dark', {renderer:'canvas'});
        intradayCharts[containerId] = chart;
    }
    if (!intradayData || intradayData.length === 0) {
        dom.innerHTML = '<div class="chart-placeholder" style="padding:50px 10px;text-align:center;color:#546e7a;font-size:11px">暂无分时数据</div>';
        return;
    }
    const times = intradayData.map(d => d.t.slice(11,16));
    const prices = intradayData.map(d => d.p);
    const volumes = intradayData.map(d => d.v);
    const zs = mp.昨收 || 0;
    const zg = mp.最高 || Math.max(...prices);
    const zd = mp.最低 || Math.min(...prices);
    const lastPx = prices[prices.length-1] || 0;
    const isUp = lastPx >= zs;

    chart.setOption({
        tooltip: {
            trigger:'axis',
            axisPointer:{type:'cross'},
            formatter: function(params) {
                const p = params[0];
                const chg = zs>0 ? ((p.value - zs) / zs * 100) : 0;
                const sign = chg>=0 ? '+' : '';
                return p.axisValue + '<br/>价格: ' + p.value.toFixed(2) +
                    '  <span style="color:'+(chg>=0?'#ef5350':'#26c6da')+'">' + sign + chg.toFixed(2) + '%</span>';
            }
        },
        grid: [{left:'3%',right:'3%',top:'8%',bottom:'8%'}],
        xAxis: [{
            type:'category', data:times,
            axisLabel:{fontSize:8},
            splitLine:{show:false},
        }],
        yAxis: [{
            type:'value',
            splitNumber:3, axisLabel:{fontSize:8, formatter: function(v){return (v - zs).toFixed(1);}},
            splitLine:{lineStyle:{color:'#0d1520'}},
            // 以昨收为基准居中
            min: zs>0 ? Math.min(zd||zs, zs) - Math.abs(zg||zs - (zd||zs)) * 0.03 : undefined,
            max: zs>0 ? Math.max(zg||zs, zs) + Math.abs(zg||zs - (zd||zs)) * 0.03 : undefined,
        }],
        series: [{
            name:'价格', type:'line', data:prices,
            smooth:true, showSymbol:false,
            lineStyle:{width:1.5, color: isUp?'#ef5350':'#26c6da'},
            areaStyle:{color: isUp?'rgba(239,83,80,0.08)':'rgba(38,198,218,0.08)'},
            markLine: zs>0 ? {
                silent:true, data:[{
                    yAxis:zs, label:{formatter:'昨收 '+zs.toFixed(2),fontSize:9,color:'#546e7a'},
                    lineStyle:{color:'#546e7a',type:'dashed',width:0.8}
                }]
            } : undefined,
        }],
        backgroundColor: 'transparent',
    });
    chart.resize();
}

function updateCard(p, mp, intraday) {
    const cc = parseCC(p.策传);
    const sy = cc._四域 || p.四域周 || '';
    const code = p.code;
    const zx = mp.最新价||0, chg = mp.涨跌幅||0;
    const zs = mp.昨收||0, jk= mp.今开||0, zg=mp.最高||0, zd=mp.最低||0;
    const score = (()=>{
        let s=0;
        if(sy=='多长') s=50; else if(sy=='多被') s=25; else if(sy=='空看') s=15; else if(sy=='空长') s=5;
        const rd=cc._日段||'';
        if(rd=='持主') s+=20; else if(rd=='持被') s+=10; else if(rd=='卖浮') s+=5;
        if(cc._仓日&&cc._仓日!='无') s+=15;
        return Math.min(s,100);
    })();
    const qHtml = '<div class="questions">'+renderQuestions(cc)+'</div>';
    const strat = renderStrategies(['🐵 猴市：见好就收',
        zx>jk?'📈 收涨'+chg.toFixed(1)+'%':'📉 收跌'+chg.toFixed(1)+'%',
        sy=='多长'?'✅ 持有':(sy=='空长'?'🔴 逢高减仓':'⚠️ 观望')]);
    const chartId = 'chart_'+code.replace(/[^a-zA-Z0-9]/g,'_');
    const dateStr = intraday && intraday.length>0 ? intraday[0].t.slice(0,10) : '';

    return '<div class="card card-'+sy+'">'+
        '<div class="card-top">'+
            '<div class="row1">'+
                '<span class="card-name">'+p.name+'</span>'+
                '<span class="card-code">'+code+'</span>'+
                '<span class="tag-dense">板块:'+(p.hanglang||'—')+'</span>'+
                '<span class="card-tag">'+p.cangzhu+'</span>'+
                '<span class="tag-dense">金额:'+fmtAmt(p.金额||0)+'</span>'+
                '<span class="tag-dense">股数:'+(p.股数||0).toFixed(0)+'</span>'+
                '<span class="tag-dense">成本:'+(p.成本||0).toFixed(1)+'</span>'+
                '<span class="tag-dense">肉垫:'+(p.肉垫||0).toFixed(0)+'</span>'+
            '</div>'+
            '<div class="row2">'+badge(sy)+'<span class="score-badge">策分:'+score+'</span></div>'+
        '</div>'+
        '<div class="card-body">'+
            '<div class="card-left">'+
                '<div class="info-title">💡 需应对问题</div>'+qHtml+
                '<div class="info-title" style="margin-top:6px">📋 8项策传映射</div>'+
                '<table class="cc-table">'+
                    '<tr><td class="cc-num">①</td><td class="cc-label">四域</td><td class="cc-val">'+(cc.四域||'').slice(0,60)+'</td></tr>'+
                    '<tr><td class="cc-num">②</td><td class="cc-label">日级</td><td class="cc-val">'+(cc.日级别||'').slice(0,55)+'</td></tr>'+
                    '<tr><td class="cc-num">③</td><td class="cc-label">波形</td><td class="cc-val">'+(cc.波形||'').slice(0,65)+'</td></tr>'+
                    '<tr><td class="cc-num">④</td><td class="cc-label">机阱</td><td class="cc-val">'+(cc.机阱||'').slice(0,50)+'</td></tr>'+
                    '<tr><td class="cc-num">⑤</td><td class="cc-label">冲高</td><td class="cc-val">'+(cc.冲高||'').slice(0,55)+'</td></tr>'+
                    '<tr><td class="cc-num">⑥</td><td class="cc-label">策分</td><td class="cc-val">'+score+'分</td></tr>'+
                '</table>'+
                '<div class="info-title" style="margin-top:6px">🎯 走势应对策略</div>'+
                '<div class="strat-box">'+strat+'</div>'+
            '</div>'+
            '<div class="card-right">'+
                '<div class="info-title">📊 走势信息</div>'+
                '<table class="quote-table">'+
                    '<tr><td>昨收</td><td>'+zs.toFixed(2)+'</td><td>今开</td><td>'+jk.toFixed(2)+'</td></tr>'+
                    '<tr><td>最高</td><td class="red">'+zg.toFixed(2)+'</td><td>最低</td><td class="green">'+zd.toFixed(2)+'</td></tr>'+
                    '<tr><td>最新</td><td class="'+(chg>=0?'red':'green')+'">'+zx.toFixed(2)+'</td><td>涨跌</td><td class="'+(chg>=0?'red':'green')+'">'+chg.toFixed(2)+'%</td></tr>'+
                '</table>'+
                '<div class="info-title" style="margin-top:6px">📈 当日分时走势'+(dateStr?' ('+dateStr+')':'')+'</div>'+
                '<div class="chart-wrap" id="'+chartId+'"></div>'+
            '</div>'+
        '</div>'+
    '</div>';
}

function updateIndexCard(p, mp, intraday) {
    const cc = parseCC(p.策传);
    const sy = cc._四域 || p.四域周 || '';
    const code = p.code;
    const zx = mp.最新价||0, chg=mp.涨跌幅||0;
    const chartId = 'idxchart_'+code.replace(/[^a-zA-Z0-9]/g,'_');
    const dateStr = intraday && intraday.length>0 ? intraday[0].t.slice(0,10) : '';

    return '<div class="card card-'+sy+'" style="margin-bottom:6px">'+
        '<div class="card-body">'+
            '<div class="card-left">'+
                '<div class="row1">'+
                    '<span class="card-name">'+p.name+'</span>'+
                    '<span class="card-code">'+code+'</span>'+
                '</div>'+
                '<div class="row2">'+badge(sy)+'</div>'+
                '<table class="quote-table">'+
                    '<tr><td>最新</td><td class="'+(chg>=0?'red':'green')+'">'+zx.toFixed(2)+'</td><td>涨跌</td><td class="'+(chg>=0?'red':'green')+'">'+chg.toFixed(2)+'%</td></tr>'+
                '</table>'+
            '</div>'+
            '<div class="card-right">'+
                '<div class="chart-wrap" id="'+chartId+'" style="height:80px"></div>'+
            '</div>'+
        '</div>'+
    '</div>';
}

function updateDashboard(data) {
    if (!data || !data.positions) return;
    const {positions, indices, market_prices, intraday, watch_rules, total_amt, total_profit, timestamp} = data;
    const mp = market_prices || {};
    const id = intraday || {};

    // 顶栏
    document.getElementById('headerInfo').innerHTML =
        '<span class="meta-item">🕒 '+timestamp+'</span>'+
        '<span class="meta-item">💰 '+(total_amt||0).toFixed(0)+'万</span>'+
        '<span class="meta-item">📊 盈亏: <span class="'+(total_profit<0?'red':'green')+'">'+(total_profit||0).toFixed(0)+'</span></span>'+
        '<span class="meta-item">📈 '+positions.length+' 只</span>';

    // 饼图
    updatePie(positions);

    // 组合概览
    const dailyPnl = positions.reduce((s,p)=>{const m=mp[p.code]||{};return s+Math.abs(p.金额||0)*((m.涨跌幅||0)/100);},0);
    document.getElementById('statsSection').style.display='';
    document.getElementById('statsGrid').innerHTML =
        '<div class="s-item"><label>持仓</label><span>'+positions.length+' 只</span></div>'+
        '<div class="s-item"><label>总市值</label><span class="green">'+(total_amt||0).toFixed(0)+'万</span></div>'+
        '<div class="s-item"><label>累计盈亏</label><span class="'+(total_profit<0?'red':'green')+'">'+(total_profit||0).toFixed(0)+'</span></div>'+
        '<div class="s-item"><label>当日浮动</label><span class="'+(dailyPnl<0?'red':'green')+'">'+dailyPnl.toFixed(1)+'万</span></div>'+
        '<div class="s-item"><label>状态</label><span class="tag-orange" style="background:#e65100;color:#fff;padding:0 6px;border-radius:3px;font-size:11px">猴市 🐵</span></div>'+
        '<div class="s-item"><label>策略</label><span class="tag-blue" style="background:#1565c0;color:#fff;padding:0 6px;border-radius:3px;font-size:11px">见好就收</span></div>';

    // 板块集中度
    const boardW = {};
    positions.forEach(p => {
        const hl = p.hanglang;
        if(!hl) return;
        boardW[hl] = (boardW[hl]||0) + Math.abs(p.金额||0)/(total_amt||1)*100;
    });
    const topBoards = Object.entries(boardW).sort((a,b)=>b[1]-a[1]).slice(0,5);
    document.getElementById('boardSection').style.display='';
    document.getElementById('boardList').innerHTML = topBoards.map(([b,pct])=>
        '<div class="board-item">'+(pct>25?'⚠️':'📊')+' '+b+': '+pct.toFixed(0)+'%</div>'
    ).join('');

    // 策卡
    document.getElementById('posCount').textContent = positions.length+' 只';
    const posCardsHtml = positions.map(p => {
        const ch = updateCard(p, mp[p.code]||{}, id[p.code]||[]);
        return ch + '<div class="card-divider"></div>';
    }).join('');
    document.getElementById('posCards').innerHTML = posCardsHtml;

    // 核心宽基
    const core = (indices&&indices.core) || [];
    document.getElementById('coreCount').textContent = core.length+' 只';
    const coreHtml = core.map(p => {
        const ch = updateIndexCard(p, mp[p.code]||{}, id[p.code]||[]);
        return ch;
    }).join('');
    document.getElementById('coreCards').innerHTML = coreHtml;

    // 重点行业
    const industry = (indices&&indices.industry) || [];
    const keyInds = ['证券','半导体','白酒','银行'];
    const keyEtfs = industry.filter(i => keyInds.some(k=>i.name.includes(k)));
    if (keyEtfs.length > 0) {
        document.getElementById('keyIndustrySection').style.display='';
        document.getElementById('keyCount').textContent = keyEtfs.length+' 只';
        const keyHtml = keyEtfs.map(p => updateIndexCard(p, mp[p.code]||{}, id[p.code]||[])).join('');
        document.getElementById('keyCards').innerHTML = keyHtml;
    }

    // 初始化所有分时图（等DOM渲染完成后统一执行）
    function initAllCharts() {
        // 持仓
        positions.forEach(p => {
            const e = document.getElementById('chart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
        // 宽基
        core.forEach(p => {
            const e = document.getElementById('idxchart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
        // 重点行业
        keyEtfs.forEach(p => {
            const e = document.getElementById('idxchart_'+p.code.replace(/[^a-zA-Z0-9]/g,'_'));
            if(e) updateIntraday(e.id, id[p.code]||[], mp[p.code]||{});
        });
    }
    // 先等200ms让DOM完成，如果还有没渲染的，用requestAnimationFrame轮询
    setTimeout(initAllCharts, 200);
    // 保险：500ms后再检查一次，补漏
    setTimeout(() => {
        document.querySelectorAll('.chart-wrap').forEach(el => {
            // 如果chart-wrap还是空的，尝试初始化
            if(el.children.length === 0 || el.innerHTML.trim() === '') {
                const id = el.id;
                // 从id反查code
                if(id.startsWith('chart_')) {
                    const p = positions.find(p2 => 'chart_'+p2.code.replace(/[^a-zA-Z0-9]/g,'_')===id);
                    if(p) updateIntraday(id, id[p.code]||[], mp[p.code]||{});
                } else if(id.startsWith('idxchart_')) {
                    const allIdx = [...core, ...keyEtfs];
                    const p = allIdx.find(p2 => 'idxchart_'+p2.code.replace(/[^a-zA-Z0-9]/g,'_')===id);
                    if(p) updateIntraday(id, id[p.code]||[], mp[p.code]||{});
                }
            }
        });
    }, 800);

    // 窗口resize时重绘图表
    window.addEventListener('resize', function() {
        Object.values(intradayCharts).forEach(c => { try{c.resize()}catch(e){} });
        try{pieChart.resize()}catch(e){}
    });

    // 盯盘
    if (watch_rules && watch_rules.length > 0) {
        document.getElementById('ruleCount').textContent = watch_rules.length+' 条';
        document.getElementById('rulesBox').innerHTML = watch_rules.map(r =>
            '<div class="rule-item"><span class="rule-type">'+r.type+'</span> '+r.msg+'</div>'
        ).join('');
    }

    // 其他指数
    const otherIdx = (industry||[]).filter(i => !keyInds.some(k=>i.name.includes(k)));
    const bigIdx = (indices&&indices.raw && indices.raw['核心大盘指数']) || [];
    const allOther = [...otherIdx, ...bigIdx];
    if (allOther.length > 0) {
        document.getElementById('otherIdxSection').style.display='';
        document.getElementById('otherCount').textContent = allOther.length+' 只';
        document.getElementById('otherIdxBody').innerHTML = allOther.map(idx=>{
            const c = parseCC(idx.策传);
            const sy = c._四域 || idx.四域周 || '';
            const m = mp[idx.code]||{};
            const sc = (()=>{let s=0;if(sy=='多长')s=50;else if(sy=='多被')s=25;else if(sy=='空看')s=15;else if(sy=='空长')s=5;return s;})();
            return '<tr><td>'+idx.code+'</td><td>'+idx.name+'</td><td>'+badge(sy)+'</td><td>'+sc+'</td><td class="'+(m.涨跌幅>=0?'red':'green')+'">'+(m.最新价||0).toFixed(2)+'</td><td class="'+(m.涨跌幅>=0?'red':'green')+'">'+(m.涨跌幅||0).toFixed(2)+'%</td></tr>';
        }).join('');
    }
}

// 定时刷新
let fetchCount = 0;
function refresh() {
    fetch('/api/data').then(r=>r.json()).then(data=>{
        fetchCount++;
        // 调试信息
        let dbg = document.getElementById('debugInfo');
        if(dbg) dbg.textContent = '#'+fetchCount+' pos='+(data.positions||[]).length+' loading='+(data.loading?'Y':'N');
        console.log('['+new Date().toLocaleTimeString()+'] #'+fetchCount+' 更新');
        if (data.loading) {
            setTimeout(refresh, 5000);
            return;
        }
        try {
            updateDashboard(data);
            if(dbg) dbg.textContent += ' render=OK';
        } catch(e) {
            if(dbg) dbg.textContent += ' ERROR: '+e.message;
            console.error('render error:', e);
        }
    }).catch(e=>{
        let dbg = document.getElementById('debugInfo');
        if(dbg) dbg.textContent = 'fetch ERROR: '+e.message;
        console.error('fetch error:', e);
    });
}

// 初始加载
initCharts();
refresh();
setInterval(refresh, (""" + str(HTML_REFRESH_SECONDS) + r""" || 60)*1000);
</script>
</body>
</html>"""


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  昭明计划 · 策传看板 v4 (Flask + ECharts)")
    print(f"  配置文件: {EXCEL_PATH}")
    print(f"  刷新周期: {HTML_REFRESH_SECONDS}s")
    print(f"  打开浏览器: http://127.0.0.1:5000")
    print("=" * 60)
    print("  ⏳ 首次数据采集中（约20s）...")

    # 先启动后台刷新线程（不阻塞Flask启动）
    def bg_refresh():
        """后台定时刷新数据"""
        while True:
            refresh_data()
            time.sleep(HTML_REFRESH_SECONDS)
    t = threading.Thread(target=bg_refresh, daemon=True)
    t.start()

    # 启动 Flask（threaded=True 支持多请求）
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)