#!/usr/bin/env python3
"""WXAB分层回测 — 周冲评分表在各WXAB等级下的表现"""
import csv, glob, os, sys
from collections import defaultdict, Counter

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = sorted(glob.glob(os.path.join(DIR, "谕组_*.csv")))
print(f"全量: {len(files)} 只股票")

# ====== 工具函数 ======
def wxab_max(s):
    if not s: return -1
    for c in '甲乙己丙戊':
        if c in s: return {'甲':4,'乙':3,'己':2,'丙':1,'戊':0}[c]
    return -1

def wxab_label(s):
    for c in '甲乙己丙戊':
        if c in s: return c
    return '?'

def wxcd_best(s):
    if not s: return -1
    for c in '金银铜铁屎尿唏嘘':
        if c in s:
            return {'金':3,'银':2,'铜':1,'铁':0,'屎':0,'尿':0,'唏':0,'嘘':0}[c]
    return -1

# 周冲条件判断
def is_多长(wxcd, wxab):
    if not wxcd or not wxab: return False
    return '金' in wxcd and ('甲' in wxab or '乙' in wxab or '己' in wxab)

def is_升排(zp):
    if not zp: return False
    return '升' in zp

def is_盈有(yt):
    if not yt: return False
    return len(yt.strip()) > 0

def is_龙猪(bo):
    if not bo: return False
    return '龙猪' in bo or '龙管' in bo

def is_震正(bo):
    if not bo: return False
    return '震正' in bo

# ====== 统计结构 ======
# WXAB等级 → 条件组合 → 统计
# 条件组合: 基础 / +ZA5~10 / +升排 / +盈有 / +龙猪
wxab_levels = {'甲': 4, '乙': 3, '己': 2, '丙': 1, '戊': 0}
stats = defaultdict(lambda: defaultdict(lambda: {'n':0, 'hr_sum':0, 'hr3':0, 'hr5':0, 'pos':0}))

count_files = 0
for f in files:
    code = os.path.basename(f)
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))

    for i in range(len(rows) - 1):
        row = rows[i]
        next_row = rows[i + 1]

        # 读取WXAB
        wxab = row.get('WXAB', '')
        ab_s = wxab_max(wxab)
        if ab_s < 0: continue
        ab_l = wxab_label(wxab)

        # 读取周冲条件
        wxcd = row.get('WXCD', '')
        za_str = row.get('ZA周', '0').strip()
        za_val = int(za_str) if za_str.lstrip('-').isdigit() else 0
        bo = row.get('波型', '')
        zp = row.get('柱排周', '')
        yt = row.get('盈提示', '')

        # 下一周冲高数据
        hr_str = next_row.get('HR', '0').strip()
        hr = float(hr_str) if hr_str else 0
        pr_str = next_row.get('PR', '0').strip()
        pr = float(pr_str) if pr_str else 0
        pos = 1 if pr > 0 else 0  # 真冲高

        # 条件组合（递进）
        conditions = [
            ('基础', True),
            ('多长', is_多长(wxcd, wxab)),
            ('ZA5~10', is_多长(wxcd, wxab) and 5 <= za_val <= 10),
            ('+升排', is_多长(wxcd, wxab) and 5 <= za_val <= 10 and is_升排(zp)),
            ('+盈有', is_多长(wxcd, wxab) and 5 <= za_val <= 10 and is_升排(zp) and is_盈有(yt)),
            ('+龙猪', is_多长(wxcd, wxab) and 5 <= za_val <= 10 and is_升排(zp) and is_盈有(yt) and is_龙猪(bo)),
        ]

        for cond_name, cond_ok in conditions:
            if cond_ok:
                s = stats[ab_l][cond_name]
                s['n'] += 1
                s['hr_sum'] += hr
                if hr >= 3: s['hr3'] += 1
                if hr >= 5: s['hr5'] += 1
                s['pos'] += pos

    count_files += 1
    if count_files % 1000 == 0:
        print(f"  已处理: {count_files}/{len(files)}", file=sys.stderr)

# ====== 输出结果 ======
print("\n" + "="*80)
print("WXAB分层 → 周冲评分表条件表现")
print("="*80)

cond_order = ['基础', '多长', 'ZA5~10', '+升排', '+盈有', '+龙猪']
for ab_l in ['乙', '甲', '己', '丙', '戊']:
    if ab_l not in stats: continue
    print(f"\n{'─'*80}")
    print(f"  WXAB = {ab_l}  (金银率参考: 月基数据)")
    print(f"{'─'*80}")
    print(f"  {'条件':<12} {'样本':>8} {'真冲高':>8} {'真均幅':>8} {'HR≥3%':>8} {'HR≥5%':>8}")
    print(f"  {'─'*12} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for cond in cond_order:
        s = stats[ab_l].get(cond)
        if not s or s['n'] == 0: continue
        zcg = s['pos'] / s['n'] * 100
        avg_hr = s['hr_sum'] / s['n']
        hr3 = s['hr3'] / s['n'] * 100
        hr5 = s['hr5'] / s['n'] * 100
        print(f"  {cond:<12} {s['n']:>8,} {zcg:>7.1f}% {avg_hr:>7.2f}% {hr3:>7.1f}% {hr5:>7.1f}%")

# ====== 对比总结 ======
print("\n" + "="*80)
print("WXAB各等级对比 — 多长+ZA5~10+升排+盈有+龙猪（最强条件）")
print("="*80)
print(f"  {'WXAB':<8} {'样本':>8} {'真冲高':>10} {'真均幅':>10} {'HR≥3%':>10} {'HR≥5%':>10} {'金银率':>8}")
print(f"  {'─'*8} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*8}")
for ab_l in ['乙', '甲', '己', '丙', '戊']:
    s = stats.get(ab_l, {}).get('+龙猪')
    if not s or s['n'] == 0: continue
    zcg = s['pos'] / s['n'] * 100
    avg_hr = s['hr_sum'] / s['n']
    hr3 = s['hr3'] / s['n'] * 100
    hr5 = s['hr5'] / s['n'] * 100
    print(f"  {ab_l:<8} {s['n']:>8,} {zcg:>9.1f}% {avg_hr:>9.2f}% {hr3:>9.1f}% {hr5:>9.1f}%")

# ====== 也输出基础条件的对比 ======
print("\n" + "="*80)
print("WXAB各等级对比 — 基础（全量，无任何条件过滤）")
print("="*80)
print(f"  {'WXAB':<8} {'样本':>8} {'真冲高':>10} {'真均幅':>10} {'HR≥3%':>10} {'HR≥5%':>10}")
print(f"  {'─'*8} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
for ab_l in ['乙', '甲', '己', '丙', '戊']:
    s = stats.get(ab_l, {}).get('基础')
    if not s or s['n'] == 0: continue
    zcg = s['pos'] / s['n'] * 100
    avg_hr = s['hr_sum'] / s['n']
    hr3 = s['hr3'] / s['n'] * 100
    hr5 = s['hr5'] / s['n'] * 100
    print(f"  {ab_l:<8} {s['n']:>8,} {zcg:>9.1f}% {avg_hr:>9.2f}% {hr3:>9.1f}% {hr5:>9.1f}%")

print("\n\n====== 分析完成 ======")