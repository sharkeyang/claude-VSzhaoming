"""DXAB引领WXAB变化量化 — 从算展xlsx提取日级数据"""
import pandas as pd
import glob, os
from collections import defaultdict

DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展"
files = glob.glob(os.path.join(DIR, "算展.*.xlsx"))
print(f"算展xlsx: {len(files)} 个")

# 逐文件提取DXAB和WXAB
总行 = 0
dxab_up_wxab_up = 0  # DXAB升后WXAB升
dxab_up_wxab_flat = 0  # DXAB升后WXAB不变
dxab_up_wxab_down = 0  # DXAB升后WXAB降
dxab_change_total = 0  # DXAB变化总次数
wxab_change_total = 0  # WXAB变化总次数

for f_idx, f in enumerate(files):
    try:
        df = pd.read_excel(f, sheet_name=0, usecols=['护型DXAB', '护型WXAB_x000D_\n周', '日龄'], nrows=500)
        列名 = list(df.columns)
        # 列名可能带后缀，找实际WXAB列
        wxab_col = None
        dxab_col = None
        for c in 列名:
            if 'WXAB' in str(c) and '护' in str(c): wxab_col = c
            if 'DXAB' in str(c) and '护' in str(c): dxab_col = c
        if not wxab_col or not dxab_col:
            continue
        df = df.rename(columns={wxab_col: 'WXAB', dxab_col: '护型DXAB'})
        df = df.dropna(subset=['护型DXAB', 'WXAB'])
        总行 += len(df)

        # 提取WXAB/NXAB的首字（甲乙己丙戊）
        def first_char(s):
            for c in '甲乙己丙戊':
                if c in str(s):
                    return c
            return None

        df['dx'] = df['护型DXAB'].apply(first_char)
        df['wx'] = df['WXAB'].apply(first_char)
        df = df.dropna()

        # 计算变化
        dx_prev = None
        wx_prev = None
        for _, row in df.iterrows():
            dx = row['dx']
            wx = row['wx']
            if dx_prev is not None and dx != dx_prev:
                dxab_change_total += 1
                # WXAB的变化
                if wx != wx_prev:
                    if wx and wx in '甲乙':
                        dxab_up_wxab_up += 1
                    else:
                        dxab_up_wxab_down += 1
                else:
                    dxab_up_wxab_flat += 1
            wx_prev = wx
            dx_prev = dx

    except Exception as e:
        pass

print(f"总行数: {总行}")
print(f"\nDXAB变化总次数: {dxab_change_total}")
print(f"  DXAB升后WXAB升: {dxab_up_wxab_up} ({dxab_up_wxab_up/dxab_change_total*100:.1f}%)")
print(f"  DXAB升后WXAB不变: {dxab_up_wxab_flat} ({dxab_up_wxab_flat/dxab_change_total*100:.1f}%)")
print(f"  DXAB升后WXAB降: {dxab_up_wxab_down} ({dxab_up_wxab_down/dxab_change_total*100:.1f}%)")

# DXAB各等级对应WXAB分布
dx_wx = defaultdict(lambda: defaultdict(int))
for f in files:
    try:
        df = pd.read_excel(f, sheet_name=0, usecols=['护型DXAB', '护型WXAB_x000D_\n周', '日龄'], nrows=500)
        wxab_col = None
        for c in df.columns:
            if 'WXAB' in str(c) and '护' in str(c): wxab_col = c
        if not wxab_col: continue
        df = df.rename(columns={wxab_col: 'WXAB'})
        df = df.dropna(subset=['护型DXAB', 'WXAB'])
        for _, row in df.iterrows():
            dx = first_char(str(row['护型DXAB']))
            wx = first_char(str(row['WXAB']))
            if dx and wx:
                dx_wx[dx][wx] += 1
    except:
        pass

print(f"\nDXAB等级 → WXAB分布:")
for dx in ['甲','乙','己','丙','戊']:
    if dx not in dx_wx: continue
    total = sum(dx_wx[dx].values())
    if total < 10: continue
    wx_good = dx_wx[dx].get('甲',0) + dx_wx[dx].get('乙',0)
    print(f"  DXAB={dx}: WXAB甲乙={wx_good/total*100:.1f}%  戊={dx_wx[dx].get('戊',0)/total*100:.1f}%  (n={total})")