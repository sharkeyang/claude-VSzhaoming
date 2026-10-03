#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：<WXAB将正交陷阱> 定义 + 三种应对方式
================================================================
用户观察（2026-10-01）：
WXAB己或WXAB刚正交时，主力没有持续的愿望，就逐渐回落WJA(EMA5)，
一般不是大阴柱，而是连阴，然后再次跌破WJA或WJB，这就构成了
<WXAB将正交陷阱>。

应对方式：
① 继续保持WJA之上的稳定升排 → 延续成为WXAB甲
② 快速大阴柱寻找WJA支撑 → 然后再次贴附于WJA继续上升
③ 等待回落至WJA得到支撑

陷阱定义（操作化）：
起点 = WXAB 己（护型首字母r）或 刚正交（AB周由负转正）
回落 = 柱排为跌柱排
陷阱 = 连阴回落（跌.尾连）且 后续1-3周内跌破WJA(WXZA<0)或WJB(WXZB<0)
应对① = 连阴回落 且 后续未跌破WJA/WJB（保持WJA之上，延续成甲）
应对② = 大阴柱回落（周涨≤-3%），后续WXZA>0（找到WJA支撑）
应对③ = 回落至WJA后WXZA>0（得到支撑）

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR  [4] WXAB护型  [6] 柱排周  [14] WXZA  [15] WXZB  [20] AB周

用法：
    python _产出物/_工具/vba表WXAB将正交陷阱验证.py
"""
import csv, os, io, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB将正交陷阱验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)


def to_f(v):
    try:
        return float(v)
    except Exception:
        return None


def main():
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 场景 -> [n, 周涨和, 正周涨数, HR和, HR>3数, 下周主升数, 下周WXZA>0数]
    stat = defaultdict(lambda: [0, 0.0, 0, 0.0, 0, 0, 0])

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
            wxzb = to_f(row[15])
            ab = to_f(row[20])
            if hx is None or not hx or zhang is None or hr is None or wxza is None or wxzb is None or ab is None:
                continue

            # 起点：己 或 刚正交
            is_ji = (hx[0] == 'r')
            is_just_turn = False
            if idx > 0 and len(rows[idx - 1]) > 20:
                prev_ab = to_f(rows[idx - 1][20])
                if prev_ab is not None and prev_ab < 0 and ab > 0:
                    is_just_turn = True
            if not (is_ji or is_just_turn):
                continue

            # 回落 = 跌柱排
            if not zp.startswith('跌'):
                continue

            # 后续1-3周是否跌破WJA/WJB
            broke = False
            for k in range(1, 4):
                if idx + k < n and len(rows[idx + k]) > 15:
                    nza = to_f(rows[idx + k][14])
                    nzb = to_f(rows[idx + k][15])
                    if nza is not None and nza < 0:
                        broke = True
                    if nzb is not None and nzb < 0:
                        broke = True

            # 场景分类
            is_dielian = '连' in zp
            is_dayin = zhang <= -3

            if is_dielian and broke:
                scene = '陷阱_连阴回落后续跌破WJA/WJB'
            elif is_dielian and not broke:
                scene = '应对①_连阴回落未跌破(延续成甲)'
            elif is_dayin:
                scene = '应对②_大阴柱回落'
            else:
                scene = '应对③_单根小阴回落'

            s = stat[scene]
            s[0] += 1
            s[1] += zhang
            if zhang > 0:
                s[2] += 1
            s[3] += hr
            if hr > 3:
                s[4] += 1

            # 下周表现
            if idx + 1 < n and len(rows[idx + 1]) > 20:
                nxt = rows[idx + 1]
                nxt_ab = to_f(nxt[20])
                nxt_wxzb = to_f(nxt[15])
                nxt_wxza = to_f(nxt[14])
                if nxt_ab is not None and nxt_wxzb is not None:
                    if (nxt_ab > 0) and (nxt_wxzb > 0):
                        s[5] += 1
                if nxt_wxza is not None and nxt_wxza > 0:
                    s[6] += 1

    # 输出
    print(f'高波池文件: {n_files}')
    print()
    print('=== <WXAB将正交陷阱> 验证（起点：己 或 刚正交，回落）===')
    print(f'{"场景":<30}{"n":>9}{"平均周涨":>9}{"正周涨%":>8}{"P(HR>3%)":>9}{"下周主升%":>9}{"下周WXZA>0%":>11}')
    print('-' * 90)
    order = ['陷阱_连阴回落后续跌破WJA/WJB', '应对①_连阴回落未跌破(延续成甲)',
             '应对②_大阴柱回落', '应对③_单根小阴回落']
    for sc in order:
        s = stat[sc]
        if s[0] == 0:
            continue
        n = s[0]
        print(f'{sc:<30}{n:>9,}{s[1]/n:>8.3f}%{s[2]/n*100:>7.1f}%{s[4]/n*100:>8.1f}%{s[5]/n*100:>8.1f}%{s[6]/n*100:>10.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '平均周涨', '正周涨%', 'P(HR>3%)', '下周主升%', '下周WXZA>0%'])
        for sc in order:
            s = stat[sc]
            if s[0] == 0:
                continue
            n = s[0]
            w.writerow([sc, n, f'{s[1]/n:.3f}', f'{s[2]/n*100:.1f}', f'{s[4]/n*100:.1f}', f'{s[5]/n*100:.1f}', f'{s[6]/n*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
