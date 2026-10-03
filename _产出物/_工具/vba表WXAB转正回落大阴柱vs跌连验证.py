#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：WXAB 转正失败/刚转正后回落 —— 大阴柱 vs 跌连 后续表现差异
================================================================
用户猜想（2026-10-01）：
WXAB 由负转正失败，或刚转正后立刻转负的情况（即 WXAB 己 或 WXAB 刚转正后），
柱排没有继续形成升排，而是回落向 WJA(EMA5)。分两种情况：
    (1) 大阴柱 找到 WJA 支撑  → 其实是比较好的情况
    (2) 跌连 逐步跌破 WJA    → 很危险

起点（分开验证）：
    A. 己护型回落：护型首字母 r己（转正失败/忐忑态），且柱排回落（跌柱排）
    B. 刚转正后回落：AB周[20] 由负转正（前周AB<0，本周AB>0），且柱排回落（跌柱排）

回落形态分类（回落周）：
    大阴柱：周涨[1] ≤ -3%，柱排为单根跌形态（跌.尾反孕/跌.尾吞，非连）
    跌连  ：柱排 跌.尾连...（连续阴线）

支撑/跌破代理（用户指定用 WXZA）：
    WXZA[14] = 价格 vs WJA(EMA5) 交叉天数。WXZA>0 = 价格在WJA之上 = 找到支撑；
    WXZA<0 = 价格跌破WJA = 跌破。

结果指标（回落后）：
    回落周后 WXZA 是否仍>0（支撑）还是<0（跌破）
    之后 1/3/5 周平均周涨、正周涨率、P(HR>3%)、是否维持 WXZA>0

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR  [4] WXAB护型  [6] 柱排周  [14] WXZA  [20] AB周

用法：
    python _产出物/_工具/vba表WXAB转正回落大阴柱vs跌连验证.py
"""
import csv, os, io, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB转正回落大阴柱vs跌连验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)


def to_f(v):
    try:
        return float(v)
    except Exception:
        return None


def is_dielian(zp):
    """跌连 = 柱排以跌开头且含'连'"""
    return zp.startswith('跌') and '连' in zp


def is_danyin_die(zp):
    """单根跌形态 = 柱排以跌开头但不含'连'（跌.尾反孕/跌.尾吞等）"""
    return zp.startswith('跌') and '连' not in zp


def main():
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计结构：
    # 起点 -> 形态 -> [n, 支撑数(WXZA>0), 跌破数(WXZA<0),
    #                 后续1周涨和, 后续1周正数, 后续1周HR>3数,
    #                 后续3周涨和, 后续3周正数, 后续3周HR>3数,
    #                 后续5周涨和, 后续5周正数, 后续5周HR>3数,
    #                 维持WXZA>0数(回落周后连续N周)]
    stat = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))

    n_files = 0
    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        n_files += 1
        try:
            with open(os.path.join(DATA_DIR, fname), encoding='gbk') as f:
                r = csv.reader(f)
                next(r)
                rows = list(r)
        except Exception:
            continue

        n = len(rows)
        for idx in range(n):
            row = rows[idx]
            if len(row) <= 20:
                continue
            hx = row[4]
            zp = row[6]
            zhang = to_f(row[1])
            hr = to_f(row[3])
            wxza = to_f(row[14])
            ab = to_f(row[20])
            if hx is None or not hx or zhang is None or hr is None or wxza is None or ab is None:
                continue

            # 回落 = 柱排为跌柱排（大阴柱或跌连）
            if not (is_dielian(zp) or is_danyin_die(zp)):
                continue

            # 判断起点
            start = None
            if hx[0] == 'r':
                start = '己护型回落'
            elif idx > 0 and len(rows[idx - 1]) > 20:
                prev_ab = to_f(rows[idx - 1][20])
                if prev_ab is not None and prev_ab < 0 and ab > 0:
                    start = '刚转正后回落'
            if start is None:
                continue

            # 形态分类
            if is_dielian(zp):
                form = '跌连'
            else:
                form = '大阴柱' if zhang <= -3 else '单根小阴(非大阴)'

            s = stat[start][form]
            s[0] += 1
            # 支撑/跌破：回落周后 WXZA
            if idx + 1 < n:
                nxt_za = to_f(rows[idx + 1][14])
                if nxt_za is not None:
                    if nxt_za > 0:
                        s[1] += 1
                    elif nxt_za < 0:
                        s[2] += 1

            # 后续 1/3/5 周表现（均涨=每周平均，正%=每周正周率，HR3%=每周HR>3率）
            for k, (off, base) in enumerate([(1, 3), (3, 6), (5, 9)]):
                for j in range(1, off + 1):
                    if idx + j < n and len(rows[idx + j]) > 3:
                        zj = to_f(rows[idx + j][1])
                        hj = to_f(rows[idx + j][3])
                        if zj is not None:
                            s[base] += zj
                            if zj > 0:
                                s[base + 1] += 1
                        if hj is not None and hj > 3:
                            s[base + 2] += 1

            # 维持 WXZA>0：回落周后连续 3 周 WXZA>0
            if idx + 3 < n:
                if all(to_f(rows[idx + j][14]) is not None and to_f(rows[idx + j][14]) > 0
                       for j in range(1, 4)):
                    s[12] += 1

    # 输出
    print(f'高波池文件: {n_files}')
    print()
    print('WXAB 转正失败/刚转正后回落 —— 大阴柱 vs 跌连 后续表现')
    print('=' * 100)
    for start in ['己护型回落', '刚转正后回落']:
        if start not in stat:
            continue
        print(f'\n【{start}】')
        print(f'{"形态":<10}{"n":>8}{"支撑%":>8}{"跌破%":>8}{"1周均涨":>9}{"1周正%":>8}{"1周HR3%":>9}{"3周均涨":>9}{"3周正%":>8}{"5周均涨":>9}{"5周正%":>8}{"维持ZA>0%":>10}')
        print('-' * 100)
        for form in ['大阴柱', '跌连', '单根小阴(非大阴)']:
            if form not in stat[start]:
                continue
            s = stat[start][form]
            n = s[0]
            if n == 0:
                continue
            support = s[1] / (s[1] + s[2]) * 100 if (s[1] + s[2]) else 0
            break_pct = s[2] / (s[1] + s[2]) * 100 if (s[1] + s[2]) else 0
            # 1周
            avg1 = s[3] / n
            pos1 = s[4] / n * 100
            hr1 = s[5] / n * 100
            # 3周（每周平均）
            avg3 = s[6] / (n * 3)
            pos3 = s[7] / (n * 3) * 100
            # 5周（每周平均）
            avg5 = s[9] / (n * 5)
            pos5 = s[10] / (n * 5) * 100
            keep = s[12] / n * 100
            print(f'{form:<10}{n:>8}{support:>7.1f}%{break_pct:>7.1f}%{avg1:>8.3f}%{pos1:>7.1f}%{hr1:>8.1f}%{avg3:>8.3f}%{pos3:>7.1f}%{avg5:>8.3f}%{pos5:>7.1f}%{keep:>9.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['起点', '形态', 'n', '支撑%', '跌破%', '1周均涨', '1周正%', '1周HR>3%',
                    '3周均涨', '3周正%', '5周均涨', '5周正%', '维持WXZA>0%'])
        for start in ['己护型回落', '刚转正后回落']:
            if start not in stat:
                continue
            for form in ['大阴柱', '跌连', '单根小阴(非大阴)']:
                if form not in stat[start]:
                    continue
                s = stat[start][form]
                n = s[0]
                if n == 0:
                    continue
                support = s[1] / (s[1] + s[2]) * 100 if (s[1] + s[2]) else 0
                break_pct = s[2] / (s[1] + s[2]) * 100 if (s[1] + s[2]) else 0
                w.writerow([start, form, n, f'{support:.1f}', f'{break_pct:.1f}',
                            f'{s[3]/n:.3f}', f'{s[4]/n*100:.1f}', f'{s[5]/n*100:.1f}',
                            f'{s[6]/(n*3):.3f}', f'{s[7]/(n*3)*100:.1f}',
                            f'{s[9]/(n*5):.3f}', f'{s[10]/(n*5)*100:.1f}', f'{s[12]/n*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
