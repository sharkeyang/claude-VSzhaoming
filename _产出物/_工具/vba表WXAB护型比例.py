#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：WXAB 护型比例（乙/戊按 WXZA 区分）+ 甲乙己 vs 丙丁戊 分组对比
================================================================
用户猜想（2026-10-01）：
1. 甲乙己、丙丁戊 比例类似
2. 己、丙 持续时间短
3. 结论：可以等到主升条件（WXAB>0且WXZB>0）或主升前置再操作

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型  [14] WXZA  [20] AB周

护型字符串：首字母(a甲/b乙/c丙/z丁/y戊/r己) + 方向(J=ZA>0/K=ZA<0) + 护级 + 持续
乙/戊 按 WXZA[14] 拆分 ZA>0/ZA<0

用法：
    python _产出物/_工具/vba表WXAB护型比例.py
"""
import csv, os, io, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXAB护型比例结果.csv'

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

    # 统计：护型 -> [周数, 段数, 持续周数和]
    stat = defaultdict(lambda: [0, 0, 0])
    total_weeks = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            with open(os.path.join(DATA_DIR, fname), encoding='gbk') as f:
                r = csv.reader(f)
                next(r)
                rows = list(r)
        except Exception:
            continue

        # 识别连续段
        prev = None
        run_len = 0
        for row in rows:
            if len(row) <= 20:
                continue
            hx = row[4]
            za = to_f(row[14])
            if not hx or hx[0] not in HX_MAP:
                continue
            h = HX_MAP[hx[0]]
            if h in ('乙', '戊'):
                if za is None:
                    continue
                h = f'{h}(ZA{"<0" if za < 0 else ">0"})'
            total_weeks += 1
            stat[h][0] += 1
            if h == prev:
                run_len += 1
            else:
                if prev is not None and run_len > 0:
                    stat[prev][1] += 1
                    stat[prev][2] += run_len
                prev = h
                run_len = 1
        if prev is not None and run_len > 0:
            stat[prev][1] += 1
            stat[prev][2] += run_len

    # 输出
    print(f'总周数: {total_weeks}')
    print()
    print('=== WXAB 护型比例（乙/戊按 WXZA 区分）===')
    print(f'{"护型":<12}{"周数":>10}{"占比":>8}{"段数":>8}{"平均持续(周)":>12}')
    print('-' * 55)
    results = []
    for h, s in stat.items():
        if s[0] == 0:
            continue
        weeks = s[0]
        segs = s[1]
        avg = s[2] / segs if segs else 0
        results.append((h, weeks, segs, avg))
    # 按周数降序
    results.sort(key=lambda x: -x[1])
    for h, weeks, segs, avg in results:
        print(f'{h:<12}{weeks:>10,}{weeks/total_weeks*100:>7.1f}%{segs:>8,}{avg:>11.2f}')

    # 分组对比
    print()
    print('=== 分组对比 ===')
    group_abj = ['甲', '乙(ZA>0)', '己']
    group_cdy = ['丙', '丁', '戊(ZA<0)']
    g1 = sum(stat[h][0] for h in group_abj if h in stat)
    g2 = sum(stat[h][0] for h in group_cdy if h in stat)
    print(f'甲乙己（升管/正交组）: {g1:,} 周 = {g1/total_weeks*100:.1f}%')
    print(f'丙丁戊（负向组）: {g2:,} 周 = {g2/total_weeks*100:.1f}%')
    print(f'比例比: {g1/g2:.2f} : 1')

    # 过渡态 vs 稳定态
    print()
    print('=== 稳定态 vs 过渡态 ===')
    stable = ['甲', '乙(ZA>0)', '丁', '戊(ZA<0)']
    trans = ['丙', '己', '乙(ZA<0)', '戊(ZA>0)']
    s_weeks = sum(stat[h][0] for h in stable if h in stat)
    t_weeks = sum(stat[h][0] for h in trans if h in stat)
    print(f'稳定态（甲/乙ZA>0/丁/戊ZA<0）: {s_weeks:,} 周 = {s_weeks/total_weeks*100:.1f}%')
    print(f'过渡态（丙/己/乙ZA<0/戊ZA>0）: {t_weeks:,} 周 = {t_weeks/total_weeks*100:.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['护型', '周数', '占比%', '段数', '平均持续(周)'])
        for h, weeks, segs, avg in results:
            w.writerow([h, weeks, f'{weeks/total_weeks*100:.1f}', segs, f'{avg:.2f}'])
        w.writerow([])
        w.writerow(['分组', '周数', '占比%'])
        w.writerow(['甲乙己', g1, f'{g1/total_weeks*100:.1f}'])
        w.writerow(['丙丁戊', g2, f'{g2/total_weeks*100:.1f}'])
        w.writerow(['稳定态', s_weeks, f'{s_weeks/total_weeks*100:.1f}'])
        w.writerow(['过渡态', t_weeks, f'{t_weeks/total_weeks*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
