#!/usr/bin/env python3
"""计算核心大盘ETF/指数的相关系数矩阵"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 未注释的核心标的
TICKERS = [
    ("sh000003", "B股指数"),
    ("sh510880", "红利ETF"),
    ("sh000139", "上证转债"),
    ("sh000001", "上证指数"),
    ("sz159949", "创业板50ETF"),
    ("sh588000", "科创50ETF"),
    ("sz399678", "深次新股"),
    ("sz159920", "恒生ETF"),
    ("sh513330", "恒生互联"),
    ("sh513050", "中概互联"),
    ("sh513100", "纳指ETF"),
]

def fetch_data(code, name):
    try:
        if code.startswith("sh000") or code.startswith("sz399"):
            df = ak.stock_zh_index_daily(symbol=code)
        else:
            df = ak.fund_etf_hist_em(symbol=code, period="daily",
                                      start_date="20250101",
                                      end_date=datetime.now().strftime("%Y%m%d"))
        df = df[['date', 'close']].copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['ret'] = df['close'].pct_change()
        df = df.rename(columns={'ret': name})
        return df[['date', name]]
    except Exception as e:
        print(f"  X {name}({code}): {str(e)[:50]}")
        return None

print("="*70)
print("核心大盘标的相关系数矩阵")
print("="*70)

all_data = None
for code, name in TICKERS:
    print(f"  下载: {name}({code})...")
    df = fetch_data(code, name)
    if df is not None:
        if all_data is None:
            all_data = df
        else:
            all_data = all_data.merge(df, on='date', how='outer')

if all_data is None:
    print("无数据")
    exit()

all_data = all_data.sort_values('date').reset_index(drop=True)

# 近180天
cutoff = datetime.now() - timedelta(days=180)
recent = all_data[all_data['date'] >= cutoff]
ret_cols = [name for _, name in TICKERS if name in recent.columns]
recent_ret = recent[ret_cols].dropna()

print(f"\n数据范围: {recent['date'].min().date()} ~ {recent['date'].max().date()}")
print(f"有效天数: {len(recent_ret)}")
print()

corr = recent_ret.corr().round(4)

print("="*70)
print("相关系数矩阵（近180天）")
print("="*70)
print(corr.to_string())
print()

# 低相关配对
print("="*70)
print("低相关系数配对 (|r| < 0.5, 适合组合分散)")
print("="*70)
n = len(ret_cols)
for i in range(n):
    for j in range(i+1, n):
        r = corr.iloc[i, j]
        if abs(r) < 0.5:
            print(f"  {ret_cols[i]:12s} vs {ret_cols[j]:12s}  r={r:+.4f}")

# 高相关配对
print()
print("="*70)
print("高相关系数配对 (|r| > 0.8, 避免同时持有)")
print("="*70)
for i in range(n):
    for j in range(i+1, n):
        r = corr.iloc[i, j]
        if abs(r) > 0.8:
            print(f"  {ret_cols[i]:12s} vs {ret_cols[j]:12s}  r={r:+.4f}  X 高相关")

print()
print("="*70)
print("组合建议: 从低相关配对中各选1只, 构建分散组合")
print("="*70)