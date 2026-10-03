#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 §8.1.5.11 两条注释的数据支持（2026-10-01）：
1. 降转(WXAB<0 且 WXZB>0) 不稳定——"失败变降主"的转移概率
2. 主升(WXAB>0 且 WXZB>0) 只是"涨多涨少、冲高是否回落"——下周涨跌分布

数据：谕组周 CSV（高波池 Qic/Qim/Qit），GBK，53 列
列：[1]周涨 [3]HR [14]WXZA [15]WXZB [16]WXZC [20]WXAB
"""
import csv, os, io, json, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/降转主升转移验证结果.csv'


def load_board_map():
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def to_f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 状态统计：本周状态 -> 下周状态计数
    # 状态: 降转(ab<0,zb>0) / 升主(ab>0,zb>0) / 降主(ab<0,zb<0) / 升转(ab>0,zb<0)
    # 下周状态: 升主 / 降转 / 降主 / 升转
    trans = defaultdict(lambda: defaultdict(int))
    # 主升下周涨跌分布
    zhsheng_next = defaultdict(int)   # 下周状态
    zhsheng_zhang = []                # 下周周涨
    zhsheng_hr = []                   # 下周HR
    zhsheng_hr3 = 0
    zhsheng_n = 0

    for i, fname in enumerate(files):
        if i % 2000 == 0:
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

        n = len(rows)
        for idx in range(n):
            row = rows[idx]
            if len(row) <= 20:
                continue
            ab = to_f(row[20]); zb = to_f(row[15])
            if ab is None or zb is None:
                continue
            if idx + 1 >= n:
                continue
            nxt = rows[idx + 1]
            if len(nxt) <= 20:
                continue
            nxt_ab = to_f(nxt[20]); nxt_zb = to_f(nxt[15])
            nxt_zhang = to_f(nxt[1]); nxt_hr = to_f(nxt[3])
            if nxt_ab is None or nxt_zb is None or nxt_zhang is None or nxt_hr is None:
                continue

            def state(a, b):
                if a > 0 and b > 0: return '升主'
                if a < 0 and b > 0: return '降转'
                if a < 0 and b < 0: return '降主'
                if a > 0 and b < 0: return '升转'
                return '其他'

            cur = state(ab, zb)
            nxt_s = state(nxt_ab, nxt_zb)
            trans[cur][nxt_s] += 1

            if cur == '升主':
                zhsheng_n += 1
                zhsheng_next[nxt_s] += 1
                zhsheng_zhang.append(nxt_zhang)
                zhsheng_hr.append(nxt_hr)
                if nxt_hr > 3:
                    zhsheng_hr3 += 1

    # ===== 输出 =====
    print(f'\n=== 降转/主升 转移验证 ===')
    states = ['升主', '降转', '降主', '升转']
    print(f'\n【1】本周状态 → 下周状态 转移矩阵（行=本周，列=下周，%）')
    hdr = '本周\\下周'.ljust(6) + ''.join(f'{s:>8}' for s in states) + f'{"n":>10}'
    print(hdr)
    for cur in states:
        row = trans[cur]
        tot = sum(row.values())
        if tot == 0:
            continue
        line = f'{cur:<6}'
        for s in states:
            line += f'{row[s]/tot*100:>7.1f}%'
        line += f'{tot:>10}'
        print(line)

    print(f'\n【2】降转(WXAB<0 且 WXZB>0) 下周去向（验证"失败变降主"）')
    jz = trans['降转']
    jz_tot = sum(jz.values())
    if jz_tot:
        for s in states:
            print(f'  降转→{s}: {jz[s]/jz_tot*100:.1f}%  (n={jz[s]})')
        print(f'  降转→降主(失败): {jz["降主"]/jz_tot*100:.1f}%')
        print(f'  降转→升主(成功): {jz["升主"]/jz_tot*100:.1f}%')
        print(f'  降转→仍降转: {jz["降转"]/jz_tot*100:.1f}%')

    print(f'\n【3】主升(WXAB>0 且 WXZB>0) 下周去向（验证"涨多涨少、冲高是否回落"）')
    zs = trans['升主']
    zs_tot = sum(zs.values())
    if zs_tot:
        for s in states:
            print(f'  升主→{s}: {zs[s]/zs_tot*100:.1f}%  (n={zs[s]})')
        print(f'  升主→仍升主(维持): {zs["升主"]/zs_tot*100:.1f}%')
        print(f'  升主→降主(转坏): {zs["降主"]/zs_tot*100:.1f}%')

    if zhsheng_n:
        import statistics
        zhang = sorted(zhsheng_zhang)
        hr = sorted(zhsheng_hr)
        print(f'\n【4】主升下周周涨分布（n={zhsheng_n}）')
        print(f'  下周均涨: {sum(zhsheng_zhang)/zhsheng_n:.3f}%')
        print(f'  下周正涨%: {sum(1 for z in zhsheng_zhang if z>0)/zhsheng_n*100:.1f}%')
        print(f'  下周周涨 分位: P10={zhang[int(zhsheng_n*0.1)]:.2f}% P50={zhang[int(zhsheng_n*0.5)]:.2f}% P90={zhang[int(zhsheng_n*0.9)]:.2f}%')
        print(f'  下周均HR: {sum(zhsheng_hr)/zhsheng_n:.2f}%  P(HR>3%): {zhsheng_hr3/zhsheng_n*100:.1f}%')
        print(f'  下周HR 分位: P10={hr[int(zhsheng_n*0.1)]:.2f}% P50={hr[int(zhsheng_n*0.5)]:.2f}% P90={hr[int(zhsheng_n*0.9)]:.2f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['本周状态', '下周状态', 'n', '占比%'])
        for cur in states:
            row = trans[cur]
            tot = sum(row.values())
            if tot == 0:
                continue
            for s in states:
                w.writerow([cur, s, row[s], f'{row[s]/tot*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
