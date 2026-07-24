#!/usr/bin/env python3
"""通过COM从VBA藏库提取ETF日线数据，计算相关系数"""
import sys, os, re, time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import win32com.client as win32

sys.stdout.reconfigure(encoding='utf-8')

# 1. 从BAS文件提取未注释标的
bas_path = "D:/@VSwork/VS昭明计划VBA优化/昭明计划VS优化_vba/SET_设9核心指基1.bas"
with open(bas_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

func_names = ["后台族非票精分调程_WA_设置典核心大盘", "后台族非票精分调程_WA_设置典核心行业"]
tickers = []
in_func = False
for line in lines:
    s = line.strip()
    for fn in func_names:
        if fn in s:
            in_func = True
            break
    if not in_func:
        continue
    if s.startswith("End Function"):
        in_func = False
        continue
    if s.startswith("'"):
        continue
    m = re.search(r'\.Add\s+[Kk]ey:="([^"]+)"', s)
    if m:
        code = m.group(1)
        m2 = re.search(r'Item:="([^"]+)"', s)
        name = m2.group(1) if m2 else code
        # 过滤掉纯指数（sh000/sz399开头，在藏库中不存为个股）
        if not code.startswith("sh000") and not code.startswith("sz399"):
            tickers.append((code, name))

print(f"共提取 {len(tickers)} 个ETF标的")

# 2. 连接Excel，从藏库读取日线数据
print("连接Excel...")
try:
    excel = win32.GetActiveObject("Excel.Application")
except:
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False

wb = None
for w in excel.Workbooks:
    if "昭明" in w.Name:
        wb = w
        break

if wb is None:
    print("未找到昭明工作簿")
    excel.Quit()
    sys.exit()

# 读取藏库数据
# 藏库sheet命名规则: 藏库_日_{市场}
# 先找藏库sheet
藏库sheets = [s.Name for s in wb.Sheets if "藏库" in s.Name]
print(f"找到藏库: {藏库sheets}")

# 尝试读取花册获取数据
# 花册中有所有标的的日线数据
ws = None
for s in wb.Sheets:
    if s.Name == "花天":
        ws = s
        break

if ws is None:
    print("未找到花天sheet")
    excel.Quit()
    sys.exit()

print("从花册读取数据...")

# 读取所有代码列
last_row = ws.UsedRange.Rows.Count
codes = ws.Range(f"A2:A{last_row}").Value
codes = [c[0] for c in codes if c[0]]

# 建立代码→行号字典
code_to_row = {}
for i, c in enumerate(codes):
    cid = str(c).strip()
    if cid:
        code_to_row[cid] = i + 2

# 查找每个ETF在花册中的位置，读取日线数据
# 花册中，日线数据从第1列开始，每只股票占据花宽单道列
# 日线数据包括: 日期, 开, 高, 低, 收, 量, 额, ...
# 需要找到日线数据区域

# 从花天读取每个ETF的日线数据
# 先找到花宽单道等常量
# 实际上，花册的日线数据是按列排列的，每只股票占用花宽单道列
# 花宽单道 = 24 (从SET_设0常量1.bas)

# 读取花宽单道
花宽单道 = 24  # 默认值
try:
    花宽单道 = int(excel.Run("SET_设0常量1.花宽单道"))
except:
    pass

print(f"花宽单道={花宽单道}")

# 读取每个ETF最近180天的收盘价
# 从花册的日线数据区域读取
# 日线数据在花册中位于第1行之后，每只股票占据花宽单道列
# 每只股票的日线数据从基列开始，包含：日期, 开, 高, 低, 收, 量, 额, ...

# 尝试另一种方法：从藏库直接读取
# 藏库_日_中股 包含所有A股日线数据
藏库名 = None
for s in 藏库sheets:
    if "日" in s:
        藏库名 = s
        break

if 藏库名:
    ws藏库 = wb.Sheets(藏库名)
    print(f"使用藏库: {藏库名}")

    # 藏库结构: 第1行是代码, 第1列是日期
    # 每列是一个标的的日线数据

    # 获取所有代码
    last_col = ws藏库.UsedRange.Columns.Count
    藏库codes = ws藏库.Range("A1").Resize(1, last_col).Value
    藏库codes = [str(c).strip() if c else "" for c in 藏库codes[0]]

    # 建立代码→列号映射
    code_to_col = {}
    for i, c in enumerate(藏库codes):
        if c:
            code_to_col[c] = i + 1

    # 获取日期列
    last_row_zk = ws藏库.UsedRange.Rows.Count
    dates = ws藏库.Range(f"A2:A{last_row_zk}").Value
    dates = [d[0] for d in dates if d[0]]

    # 读取每个ETF的收盘价
    all_data = {}
    cutoff_date = datetime.now() - timedelta(days=180)

    for code, name in tickers:
        # 尝试多种代码格式
        for try_code in [code, code.replace("sh", ""), code.replace("sz", ""),
                         code.replace("sh", "SH"), code.replace("sz", "SZ")]:
            if try_code in code_to_col:
                col = code_to_col[try_code]
                vals = ws藏库.Range(f"{chr(64+col)}2:{chr(64+col)}{last_row_zk}").Value
                prices = []
                for j, d in enumerate(dates):
                    if j < len(vals) and vals[j] and vals[j][0]:
                        try:
                            p = float(vals[j][0])
                            prices.append((d, p))
                        except:
                            pass
                if prices:
                    df = pd.DataFrame(prices, columns=['date', 'close'])
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    df['ret'] = df['close'].pct_change()
                    df = df.rename(columns={'ret': name})
                    all_data[name] = df[['date', name]]
                    print(f"  OK {name}({code})")
                break
        else:
            print(f"  X {name}({code}) 未在藏库中找到")

    print(f"\n成功获取: {len(all_data)}/{len(tickers)}")

    if len(all_data) >= 2:
        # 合并数据
        merged = None
        for name, df in all_data.items():
            if merged is None:
                merged = df
            else:
                merged = merged.merge(df, on='date', how='outer')

        merged = merged.sort_values('date').reset_index(drop=True)
        recent = merged[merged['date'] >= cutoff_date]
        ret_cols = [c for c in merged.columns if c != 'date']
        recent_ret = recent[ret_cols].dropna()

        print(f"数据范围: {recent['date'].min().date()} ~ {recent['date'].max().date()}")
        print(f"有效天数: {len(recent_ret)}")

        corr = recent_ret.corr().round(4)

        print("\n" + "="*70)
        print("相关系数矩阵")
        print("="*70)
        print(corr.to_string())

        print("\n" + "="*70)
        print("低相关系数配对 (|r| < 0.3, 适合组合分散)")
        print("="*70)
        n = len(ret_cols)
        for i in range(n):
            for j in range(i+1, n):
                r = corr.iloc[i, j]
                if abs(r) < 0.3:
                    print(f"  {ret_cols[i]:12s} vs {ret_cols[j]:12s}  r={r:+.4f}")

        print("\n" + "="*70)
        print("高相关系数配对 (|r| > 0.7, 避免同时持有)")
        print("="*70)
        for i in range(n):
            for j in range(i+1, n):
                r = corr.iloc[i, j]
                if abs(r) > 0.7:
                    print(f"  {ret_cols[i]:12s} vs {ret_cols[j]:12s}  r={r:+.4f}  X")
    else:
        print("数据不足，无法计算相关系数")
else:
    print("未找到日线藏库")

excel.Quit()
print("\n完成")