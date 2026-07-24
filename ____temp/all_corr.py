#!/usr/bin/env python3
"""提取核心大盘+核心行业标的，计算相关系数矩阵"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys, re

sys.stdout.reconfigure(encoding='utf-8')

# 从BAS文件提取未注释标的（只取指定函数）
bas_path = "D:/@VSwork/VS昭明计划VBA优化/昭明计划VS优化_vba/SET_设9核心指基1.bas"
with open(bas_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 只取两个函数之间的内容
func_names = ["后台族非票精分调程_WA_设置典核心大盘", "后台族非票精分调程_WA_设置典核心行业"]
tickers = []
in_func = False
for line in lines:
    stripped = line.strip()
    # 检查是否进入目标函数
    for fn in func_names:
        if fn in stripped:
            in_func = True
            break
    if not in_func:
        continue
    # 遇到 End Function 退出
    if stripped.startswith("End Function"):
        in_func = False
        continue
    # 跳过注释行
    if stripped.startswith("'") or stripped.startswith("'"):
        continue
    # 匹配未注释的 .Add
    m = re.search(r'\.Add\s+[Kk]ey:="([^"]+)"', stripped)
    if m:
        code = m.group(1)
        m2 = re.search(r'Item:="([^"]+)"', stripped)
        name = m2.group(1) if m2 else code
        tickers.append((code, name))

print(f"共提取 {len(tickers)} 个未注释标的\n")

def fetch_data(code, name):
    try:
        df = ak.stock_zh_index_daily(symbol=code)
        df = df[['date', 'close']].copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['ret'] = df['close'].pct_change()
        df = df.rename(columns={'ret': name})
        return df[['date', name]]
    except Exception as e:
        return None

all_data = None
success = 0
for code, name in tickers:
    df = fetch_data(code, name)
    if df is not None:
        success += 1
        if all_data is None:
            all_data = df
        else:
            all_data = all_data.merge(df, on='date', how='outer')

print(f"获取成功: {success}/{len(tickers)}")
if all_data is None:
    print("无数据")
    exit()

all_data = all_data.sort_values('date').reset_index(drop=True)
cutoff = datetime.now() - timedelta(days=180)
recent = all_data[all_data['date'] >= cutoff]
ret_cols = [c for c in all_data.columns if c not in ('date', 'close') and c in recent.columns]
recent_ret = recent[ret_cols].dropna()

print(f"数据范围: {recent['date'].min().date()} ~ {recent['date'].max().date()}")
print(f"有效天数: {len(recent_ret)}")
print()

corr = recent_ret.corr().round(4)

# 按板块分组的低相关配对
print("="*70)
print("低相关系数配对 (|r| < 0.3, 适合组合分散)")
print("="*70)
n = len(ret_cols)
pairs = []
for i in range(n):
    for j in range(i+1, n):
        r = corr.iloc[i, j]
        if abs(r) < 0.3:
            pairs.append((ret_cols[i], ret_cols[j], r))
            print(f"  {ret_cols[i]:12s} vs {ret_cols[j]:12s}  r={r:+.4f}")

# 按板块分组
print("\n" + "="*70)
print("各板块间平均相关系数")
print("="*70)
# 手动分组
groups = {
    "消费": ["创新药ETF","医疗ETF","酒ETF","食品ETF","旅游ETF","畜牧ETF","农业ETF"],
    "金融": ["金融ETF","证券保险ETF","银行ETF","房地产ETF","建材ETF"],
    "科技": ["人工智能AIETF","半导体ETF","电子50ETF","通信ETF","数据ETF","云计算ETF","信息安全ETF","软件ETF"],
    "制造": ["机床ETF","机器人ETF","高端装备ETF","航空航天ETF","军工ETF","光伏50ETF","中证新能","电池ETF"],
    "周期": ["煤炭ETF","国证有色","稀土ETF","钢铁ETF","基建ETF","绿色电力ETF","国证油气"],
    "宽基": ["B股指数","上证转债","上证指数","深次新股","创业板50ETF","科创50ETF","红利ETF"],
    "传媒": ["影视ETF","传媒ETF","游戏ETF"],
    "港股": ["恒生ETF","恒生互联","中概互联","纳指ETF"],
}

for g1 in groups:
    for g2 in groups:
        if g1 >= g2: continue
        g1_cols = [c for c in groups[g1] if c in ret_cols]
        g2_cols = [c for c in groups[g2] if c in ret_cols]
        if not g1_cols or not g2_cols: continue
        rs = []
        for c1 in g1_cols:
            for c2 in g2_cols:
                if c1 in corr.index and c2 in corr.columns:
                    rs.append(corr.loc[c1, c2])
        if rs:
            avg = np.mean(rs)
            flag = " 低相关" if avg < 0.3 else " 高相关" if avg > 0.7 else ""
            print(f"  {g1:6s} vs {g2:6s}  r={avg:.3f}{flag}")

# 组合建议
print("\n" + "="*70)
print("组合构建建议 (从低相关板块中各选1-2只)")
print("="*70)
print("  核心: 宽基ETF 1-2只 (跟住大盘)")
print("  卫星: 消费 + 科技 + 制造 + 周期 各1只")
print("  可选: 港股/传媒 视时机配置")
print("="*70)