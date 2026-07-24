#!/usr/bin/env python3
"""基于周线谕组数据，近似分析DXEF-DXCD框架各状态的下周概率"""
import csv, glob, os, sys, re
from collections import defaultdict, Counter
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = sorted(glob.glob(os.path.join(DIR, "谕组_*.csv")))
print(f"全量: {len(files)} 只股票\n")

def wxab_max(s):
    if not s: return -1
    for c in '甲乙己丙戊':
        if c in s: return {'甲':4,'乙':3,'己':2,'丙':1,'戊':0}[c]
    return -1

def wxcd_label(s):
    """从WXCD字符串中提取首字"""
    if not s: return '?'
    for c in '金银铜铁屎尿唏嘘':
        if c in s: return c
    return '?'

def wxcd_is_good(s):
    """金银=True, 其他=False"""
    l = wxcd_label(s)
    return l in ('金','银')

def wxcd_is_bad(s):
    l = wxcd_label(s)
    return l in ('屎','尿')

def wxcd_is_xi(s):
    l = wxcd_label(s)
    return l in ('唏','嘘')

# 状态统计
# 按当前周的状态，统计下周转为各种状态的概率
# 状态定义(近似DXEF框架):
# DXEF>0, DXZE>0 ≈ WXCD=金/银, WXZC>0
# DXEF<0, DXZE>0 ≈ WXCD=唏/嘘, WXZC>0 (但WXCD不好)
# DXEF<0, DXZE<0 ≈ WXCD=屎/尿, WXZC<0 (或WXCD=金/银但WXZC<0)
# DXEF>0, DXZE<0 ≈ WXCD=金/银, WXZC<0

# 由于周线数据没有DXCD，用WXAB和ZA周近似
# DXCD>0 ≈ WXAB在甲乙己中
# DXCD<0 ≈ WXAB在丙戊中
# ZA周>0 ≈ 周级别站上DJA
# ZC周>0 ≈ 周级别站上DJC
# ZE周>0 ≈ 周级别站上DJE

stats = defaultdict(lambda: {'n':0, 'next_ze_pos':0, 'next_zc_pos':0, 'next_za_pos':0})

count_files = 0
for f in files:
    code = os.path.basename(f)
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))

    for i in range(len(rows) - 1):
        row = rows[i]
        next_row = rows[i + 1]

        # 当前周状态
        wxcd = row.get('WXCD', '')
        wxab = row.get('WXAB', '')
        za_str = row.get('ZA周', '0').strip()
        zc_str = row.get('ZC周', '0').strip()
        ze_str = row.get('ZE周', '') if 'ZE周' in row else '0'

        # 解析数值
        za = int(za_str) if za_str.lstrip('-').isdigit() else 0
        zc = int(zc_str) if zc_str.lstrip('-').isdigit() else 0
        # 注：谕组CSV没有ZE周列，用ZC周近似ZE
        ze = zc

        # 下周状态
        next_wxcd = next_row.get('WXCD', '')
        next_za_str = next_row.get('ZA周', '0').strip()
        next_zc_str = next_row.get('ZC周', '0').strip()
        next_za = int(next_za_str) if next_za_str.lstrip('-').isdigit() else 0
        next_zc = int(next_zc_str) if next_zc_str.lstrip('-').isdigit() else 0
        # 注：谕组CSV没有ZE周列，用ZC周近似ZE（站上DJC≈站上DJE）
        next_ze = next_zc

        # 确定当前状态分组
        wxcd_l = wxcd_label(wxcd)
        ab_s = wxab_max(wxab)

        # 近似DXEF框架
        is_good = wxcd_is_good(wxcd)  # 金银
        is_bad = wxcd_is_bad(wxcd)    # 屎尿
        is_xi = wxcd_is_xi(wxcd)      # 唏嘘
        ze_pos = zc > 0  # 用ZC近似ZE
        zc_pos = zc > 0
        za_pos = za > 0
        ab_pos = ab_s >= 2  # WXAB>=己

        # 构建状态key (近似DXEF框架)
        if is_good and ze_pos:
            dxef_group = '金银'
            if zc_pos and za_pos: sub = '主动'
            elif zc_pos and ab_pos: sub = '被动'
            elif zc_pos: sub = '持有'
            else: sub = '可暂退'
        elif is_good and not ze_pos:
            dxef_group = '嘘'
            sub = '退出'
        elif is_xi and ze_pos:
            dxef_group = '唏'
            if ab_s >= 2: sub = '可试仓'
            elif ab_s >= 0: sub = '可警惕'
            else: sub = '仅观察'
        else:
            # 屎尿
            dxef_group = '屎尿'
            if zc_pos and za_pos: sub = '主动'
            elif zc_pos and ab_pos: sub = '被动'
            elif zc_pos: sub = '持有'
            elif za_pos and not zc_pos: sub = '试仓'
            elif zc_pos: sub = '观察'
            else: sub = '禁止'

        key = f'{dxef_group}/{sub}'
        s = stats[key]
        s['n'] += 1
        if next_ze > 0: s['next_ze_pos'] += 1
        if next_ze > 0 and next_zc > 0: s['next_zc_pos'] += 1
        if next_ze > 0 and next_zc > 0 and next_za > 0: s['next_za_pos'] += 1

    count_files += 1
    if count_files % 1000 == 0:
        print(f"  已处理: {count_files}/{len(files)}", file=sys.stderr)

# 输出
print("="*80)
print("DXEF-DXCD框架近似分析（基于周线数据，7463只）")
print("="*80)
print(f"\n{'状态':20s} {'样本':>8s} {'→ZE>0':>10s} {'→ZE>0-ZC>0':>14s} {'→ZE>0-ZC>0-ZA>0':>18s}")
print(f"{'-'*70}")

# 按DXEF战场分组输出
for group in ['屎尿', '唏', '金银', '嘘', '其他']:
    group_keys = [k for k in stats.keys() if k.startswith(group)]
    if not group_keys: continue
    print(f"\n[{group}战场]")
    for k in sorted(group_keys):
        s = stats[k]
        if s['n'] == 0: continue
        p1 = s['next_ze_pos'] / s['n'] * 100
        p2 = s['next_zc_pos'] / s['n'] * 100
        p3 = s['next_za_pos'] / s['n'] * 100
        print(f"  {k.split('/')[1]:10s} {s['n']:>8,} {p1:>8.1f}% {p2:>12.1f}% {p3:>16.1f}%")

print("\n" + "="*80)
print("分析完成")