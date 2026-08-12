#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.8_全量周等型验证.py
=====================
全量周等型(ZA周)验证，对标 MC3.1 §3.1/§四/§五。

功能：
1. ZA周正/负区分度（全量确认 §3.1 的 +2.7pp）
2. ZA周极值区分度（>3 vs -1, >5 vs -1 等）
3. AB末位 vs CDEF末位 在不同阈值下的区分力（§五阈值优化）
4. 简化为3等决策：等1(ZA=1)/等2(ZA≥2)/等5(ZA<0) 对比原8等

用法：
    python _产出物/MC3.8_全量周等型验证.py

输出：
    - 控制台打印结构化表
    - 同时写入 _分析输出/MC3.8_周等型验证.txt
"""

import csv, os, sys
from collections import defaultdict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
os.makedirs(OUTDIR, exist_ok=True)

# ──────────────────────────────────────────────────────────
# 数据加载
# ──────────────────────────────────────────────────────────
def load_data():
    """加载所有周CSV，附加下周HR（下一条周线的HR）"""
    files = sorted([f for f in os.listdir(DATADIR) if f.endswith('.csv')])
    total_rows = 0
    all_rows = []
    for fi, fn in enumerate(files):
        fp = os.path.join(DATADIR, fn)
        with open(fp, 'r', encoding='gbk') as f:
            rows = list(csv.DictReader(f))
        # 每条记录（除最后一行）附加下周HR
        for i in range(len(rows) - 1):
            r = dict(rows[i])
            try:
                r['_下周HR'] = float(rows[i + 1].get('HR', 0) or 0)
            except:
                continue
            all_rows.append(r)
            total_rows += 1
        if (fi + 1) % 1000 == 0:
            print(f'  [加载] 已处理 {fi + 1}/{len(files)} 个文件, {total_rows} 行...', flush=True)
    print(f'  [加载] 完成: {len(files)} 文件, {total_rows} 行')
    return all_rows

# ──────────────────────────────────────────────────────────
# 统计工具
# ──────────────────────────────────────────────────────────
def p3(rows, cond_fn, label=''):
    """计算符合条件行的下周P3 = P(HR≥3%)"""
    matched = [r for r in rows if cond_fn(r)]
    n = len(matched)
    if n < MIN_SAMPLE:
        return None, n, 0
    surge = sum(1 for r in matched if r['_下周HR'] >= 3)
    return surge / n * 100, n, surge

def print_table(title, rows, items, label_width=22):
    """打印格式化表：条件 | 样本 | P3% | vs基线 | 说明"""
    # 计算基线
    total = len(rows)
    baseline = sum(1 for r in rows if r['_下周HR'] >= 3) / total * 100 if total > 0 else 0

    lines = [f'\n{"=" * 80}', f'{title}', f'{"=" * 80}',
             f'基线: 全样本 {total} 行, 下周P3={baseline:.1f}%', '']
    header = f'{"条件":<{label_width}s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>7s}  {"说明"}'
    lines.append(header)
    lines.append('-' * len(header))

    for name, cond_fn, note in items:
        p, n, s = p3(rows, cond_fn)
        if p is None:
            lines.append(f'{name:<{label_width}s}  {n:>8,d}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            diff = p - baseline
            lines.append(f'{name:<{label_width}s}  {n:>8,d}  {p:>6.1f}%  {diff:>+7.1f}pp  {note}')
    lines.append('')
    return '\n'.join(lines)

# ──────────────────────────────────────────────────────────
# 条件函数
# ──────────────────────────────────────────────────────────
def get_za(row):
    try:
        return int(float(row.get('ZA周', 0) or 0))
    except:
        return 0

def get_lc(row):
    """中符串周末位字符"""
    lc = str(row.get('中符串周', '') or '')
    return lc[-1] if lc else ''

# ZA周范围条件
def za_range(lo, hi):
    return lambda r: lo <= get_za(r) <= hi

def za_gt(v):
    return lambda r: get_za(r) > v

def za_lt(v):
    return lambda r: get_za(r) < v

def za_eq(v):
    return lambda r: get_za(r) == v

# 末位条件
def lc_is(*chars):
    return lambda r: get_lc(r) in chars

def lc_is_ab():
    return lambda r: get_lc(r) in ('A', 'B')

def lc_is_cdef():
    return lambda r: get_lc(r) in ('C', 'D', 'E', 'F')

# 组合条件
def and_(*fns):
    return lambda r: all(f(r) for f in fns)

# ──────────────────────────────────────────────────────────
# 主分析
# ──────────────────────────────────────────────────────────
def main():
    print('=' * 80)
    print('MC3.8 全量周等型验证')
    print('=' * 80)
    print()

    rows = load_data()
    total = len(rows)
    baseline = sum(1 for r in rows if r['_下周HR'] >= 3) / total * 100
    print(f'\n{"=" * 80}')
    print(f'全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
    print(f'{"=" * 80}')

    output = []

    # ── 1. ZA周正/负区分度 ──
    items = [
        ('ZA周>0 (站上WJA)', za_gt(0), '上侧'),
        ('ZA周<0 (跌破WJA)', za_lt(0), '下侧'),
        ('ZA周=1 (刚站上)', za_eq(1), '等1'),
        ('ZA周=-1 (刚跌破)', za_eq(-1), '等5'),
        ('ZA周>3 (远离WJA)', za_gt(3), ''),
        ('ZA周<-3 (远离WJA下方)', za_lt(-3), ''),
        ('ZA周>5', za_gt(5), ''),
        ('ZA周<-5', za_lt(-5), ''),
    ]
    out = print_table('1. ZA周正/负区分度', rows, items)
    print(out)
    output.append(out)

    # ── 2. ZA周逐值P3 ──
    # 收集ZA周各值
    za_groups = defaultdict(list)
    for r in rows:
        z = get_za(r)
        # 合并极端值
        if z > 30:
            z = 30
        elif z < -30:
            z = -30
        za_groups[z].append(r)

    lines = ['\n' + '=' * 80, '2. ZA周逐值P3（ZA周=-30~30, 含极端值合并）', '=' * 80]
    lines.append(f'{"ZA周":>6s}  {"样本":>8s}  {"P3%":>7s}  {"vs基线":>7s}')
    lines.append('-' * 40)
    for z in sorted(za_groups.keys()):
        grp = za_groups[z]
        n = len(grp)
        if n < MIN_SAMPLE:
            continue
        s = sum(1 for r in grp if r['_下周HR'] >= 3)
        pct = s / n * 100
        diff = pct - baseline
        lines.append(f'{z:>6d}  {n:>8,d}  {pct:>6.1f}%  {diff:>+7.1f}%')
    lines.append('')
    out = '\n'.join(lines)
    print(out)
    output.append(out)

    # ── 3. AB末位 vs CDEF末位 阈值优化 ──
    lines = ['\n' + '=' * 80,
             '3. AB末位 vs CDEF末位 阈值优化（仿 §五）',
             '=' * 80,
             '思路：在不同ZA阈值下，比较AB末位与CDEF末位的下周P3区分度',
             '']
    header = f'{"阈值t":>8s}  {"AB末位P3":>10s}  {"CDEF末位P3":>12s}  {"差pp":>6s}  {"说明"}'
    lines.append(header)
    lines.append('-' * 60)
    for t in [0, 1, 2, 3, 4, 5, 6, 8, 10]:
        rows_ab = [r for r in rows if get_za(r) > t and lc_is_ab()(r)]
        rows_cdef = [r for r in rows if get_za(r) > t and lc_is_cdef()(r)]
        rows_cdef_eq = [r for r in rows if get_za(r) == t and lc_is_cdef()(r)]
        rows_ab_eq = [r for r in rows if get_za(r) == t and lc_is_ab()(r)]
        p_ab = sum(1 for r in rows_ab if r['_下周HR'] >= 3) / len(rows_ab) * 100 if len(rows_ab) >= MIN_SAMPLE else None
        p_cdef = sum(1 for r in rows_cdef if r['_下周HR'] >= 3) / len(rows_cdef) * 100 if len(rows_cdef) >= MIN_SAMPLE else None
        p_ab_eq = sum(1 for r in rows_ab_eq if r['_下周HR'] >= 3) / len(rows_ab_eq) * 100 if len(rows_ab_eq) >= MIN_SAMPLE else None
        p_cdef_eq = sum(1 for r in rows_cdef_eq if r['_下周HR'] >= 3) / len(rows_cdef_eq) * 100 if len(rows_cdef_eq) >= MIN_SAMPLE else None

        n_ab = len(rows_ab)
        n_cdef = len(rows_cdef)
        if p_ab is not None and p_cdef is not None:
            diff = p_ab - p_cdef
            note = f'末位区分: AB{n_ab:,d} vs CDEF{n_cdef:,d}'
            lines.append(f'ZA>={t:>4d}  {p_ab:>7.1f}%({n_ab:>6,d})  {p_cdef:>7.1f}%({n_cdef:>6,d})  {diff:>+5.1f}pp  {note}')
        else:
            lines.append(f'ZA>={t:>4d}  {"-":>10s}  {"-":>12s}  {"-":>6s}  (样本不足)')

        n_ab_eq = len(rows_ab_eq)
        n_cdef_eq = len(rows_cdef_eq)
        if p_ab_eq is not None and p_cdef_eq is not None:
            diff_eq = p_ab_eq - p_cdef_eq
            lines.append(f'ZA=={t:>4d}  {p_ab_eq:>7.1f}%({n_ab_eq:>6,d})  {p_cdef_eq:>7.1f}%({n_cdef_eq:>6,d})  {diff_eq:>+5.1f}pp  (精确值)')

    # 下侧末位区分度
    lines.append(f'\n{"下侧(ZA<0):":-^60s}')
    for t in [0, -1, -2, -3, -5, -8]:
        rows_ab = [r for r in rows if get_za(r) < t and lc_is_ab()(r)]
        rows_cdef = [r for r in rows if get_za(r) < t and lc_is_cdef()(r)]
        if len(rows_ab) >= MIN_SAMPLE and len(rows_cdef) >= MIN_SAMPLE:
            p_ab = sum(1 for r in rows_ab if r['_下周HR'] >= 3) / len(rows_ab) * 100
            p_cdef = sum(1 for r in rows_cdef if r['_下周HR'] >= 3) / len(rows_cdef) * 100
            diff = p_ab - p_cdef
            lines.append(f'ZA<{t:>4d}  {p_ab:>7.1f}%({len(rows_ab):>6,d})  {p_cdef:>7.1f}%({len(rows_cdef):>6,d})  {diff:>+5.1f}pp')
    lines.append('')
    out = '\n'.join(lines)
    print(out)
    output.append(out)

    # ── 4. 简化为3等决策 ──
    # 原8等 vs 简化3等
    items_8 = [
        ('等1 (ZA=1)', za_eq(1), ''),
        ('等2 (ZA≥2+CDEF=原等2+等4)', and_(za_gt(1), lc_is_cdef()), ''),
        ('等3 (ZA≥2+AB)', and_(za_gt(1), lc_is_ab()), ''),
        ('等5 (ZA=-1)', za_eq(-1), ''),
        ('等6 (ZA≤-2+ABCD=原等6+等8)', and_(za_lt(-1), lc_is('A', 'B', 'C', 'D')), ''),
        ('等7 (ZA≤-2+EF)', and_(za_lt(-1), lc_is('E', 'F')), ''),
    ]
    items_3 = [
        ('等1 (ZA=1)', za_eq(1), '刚站上WJA'),
        ('等2 (ZA≥2)', za_gt(1), '站上WJA（含等3+等2原等4）'),
        ('等5 (ZA<0)', za_lt(0), '跌破WJA（含等7+等6原等8）'),
    ]
    out = print_table('4a. 原8等分区', rows, items_8, label_width=26)
    print(out)
    output.append(out)

    out = print_table('4b. 简化3等', rows, items_3, label_width=16)
    print(out)
    output.append(out)

    # 简化3等 vs 原8等 区分度汇总
    # 原8等最佳 vs 最差
    items_8_best_worst = [
        ('原8等最佳', items_8[2][1], '等3'),  # 等3
        ('原8等最差', items_8[4][1], '等5'),  # 等5
        ('原8等区分度', None, ''),
        ('简化3等最佳', items_3[1][1], '等2'),
        ('简化3等最差', items_3[2][1], '等5'),
        ('简化3等区分度', None, ''),
        ('简化 vs 原8 区分度损失', None, ''),
    ]
    lines = ['\n' + '=' * 80, '4c. 简化3等 vs 原8等 区分度对比', '=' * 80]
    # 计算
    def calc_pp(items, idx_best, idx_worst):
        p_best, n_best, _ = p3(rows, items[idx_best][1])
        p_worst, n_worst, _ = p3(rows, items[idx_worst][1])
        if p_best and p_worst:
            return p_best - p_worst, p_best, p_worst, n_best, n_worst
        return None, None, None, 0, 0

    diff8, p8b, p8w, n8b, n8w = calc_pp(items_8, 2, 4)
    diff3, p3b, p3w, n3b, n3w = calc_pp(items_3, 1, 2)

    lines.append(f'  原8等: 最佳={p8b:.1f}%(n={n8b:,d}) 最差={p8w:.1f}%(n={n8w:,d}) 区分度={diff8:+.1f}pp')
    lines.append(f'  简化3等: 最佳={p3b:.1f}%(n={n3b:,d}) 最差={p3w:.1f}%(n={n3w:,d}) 区分度={diff3:+.1f}pp')
    if diff8 and diff3:
        loss = diff8 - diff3
        lines.append(f'  区分度损失: {loss:+.1f}pp (简化3等保留 {diff3/diff8*100:.0f}% 的原区分度)')
        if loss < 2:
            lines.append('  ✅ 建议简化：末位AB/CDEF在周级别区分力不足，简化3等即可')
        else:
            lines.append('  ⚠️ 保留原8等：末位区分力较大，简化损失不可接受')
    lines.append('')
    out = '\n'.join(lines)
    print(out)
    output.append(out)

    # ── 5. 上侧(ZA>0) vs 下侧(ZA<0) 完整对比 ──
    items_side = [
        ('ZA周>0 (上侧)', za_gt(0), ''),
        ('ZA周=1', za_eq(1), ''),
        ('ZA周=2', za_eq(2), ''),
        ('ZA周=3', za_eq(3), ''),
        ('ZA周=4~5', za_range(4, 5), ''),
        ('ZA周=6~10', za_range(6, 10), ''),
        ('ZA周>10', za_gt(10), ''),
        ('ZA周<0 (下侧)', za_lt(0), ''),
        ('ZA周=-1', za_eq(-1), ''),
        ('ZA周=-2', za_eq(-2), ''),
        ('ZA周=-3', za_eq(-3), ''),
        ('ZA周=-4~-5', za_range(-5, -4), ''),
        ('ZA周=-6~-10', za_range(-10, -6), ''),
        ('ZA周<-10', za_lt(-10), ''),
    ]
    out = print_table('5. ZA周上侧/下侧完整分级', rows, items_side, label_width=18)
    print(out)
    output.append(out)

    # ── 6. 合并2/4建议 ──
    items_merge = [
        ('等2 (ZA=2~3+CDEF)', and_(za_range(2, 3), lc_is_cdef()), ''),
        ('等4 (ZA>3+CDEF)', and_(za_gt(3), lc_is_cdef()), ''),
        ('等2+等4合并', and_(za_gt(1), lc_is_cdef()), ''),
        ('等3 (ZA≥2+AB)', and_(za_gt(1), lc_is_ab()), ''),
    ]
    out = print_table('6. 等2/等4合并建议（仿 §四）', rows, items_merge, label_width=22)
    print(out)
    output.append(out)

    # 计算合并 vs 等3差
    p_merge, n_merge, _ = p3(rows, and_(za_gt(1), lc_is_cdef()))
    p_3, n_3, _ = p3(rows, and_(za_gt(1), lc_is_ab()))
    if p_merge and p_3:
        diff = p_3 - p_merge
        lines = [f'  等2+等4合并P3={p_merge:.1f}%(n={n_merge:,d}) vs 等3P3={p_3:.1f}%(n={n_3:,d})']
        lines.append(f'  差 = {diff:+.1f}pp')
        if diff < 3:
            lines.append('  ✅ 等2/等4合并近等3，可合并')
        else:
            lines.append('  ⚠️ 差较大，维持分开')
        print('\n'.join(lines))
        output.append('\n'.join(lines))

    # ── 写入文件 ──
    outpath = os.path.join(OUTDIR, 'MC3.8_周等型验证.txt')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    print(f'\n结果已写入: {outpath}')

if __name__ == '__main__':
    main()