#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日主升区域升势/跌势验证 — 用真实 DTZB[62]/DTAB[64] 重跑 §6.7.2 框架

背景：§6.7.2 旧验证用代理 DXZB（护级 in 上/中/忐），未用 2026-09-24 新增的真实
      DTZB 列62（JZ vs JB 交叉天数）和 DTAB 列64（JA vs JB 交叉天数）。
      本脚本用真实列重跑，验证"（DXAB>0 且 DXZB>0）是升势"等判定是否成立。

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD 护级   [9] 护型   [13] 日ZA   [14] 日ZC
    [26] 次日高幅   [62] DTZB(JZ vs JB)   [64] DTAB(JA vs JB)

用法：
    python _产出物/_工具/vba表主升升势验证.py
"""
import csv, os, io
from collections import defaultdict

# ---------- 配置 ----------
TARGET = 2.0                     # 目标：次日冲高≥2%
MIN_SAMPLE = 1000
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升升势验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
DXCD_MAIN = {'上', '忐'}          # 主升区域


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计：标签 -> [n, hit]
    stat = defaultdict(lambda: [0, 0])
    # 三类入口需要前一柱状态，用 prev 记录
    prev = None  # (cd, hx, za, zc, zb, ab)

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            prev = None
            for row in r:
                if len(row) < 66:
                    continue
                try:
                    next_high = float(row[26])
                    za = float(row[13])
                    zc = float(row[14])
                    zb = float(row[62])
                    ab = float(row[64])
                    chg = float(row[5])
                except ValueError:
                    prev = None
                    continue
                cd = row[8].strip()
                hx = HX_MAP.get(row[9][0]) if row[9] else None
                hit = 1 if next_high >= TARGET else 0

                # 只在主升区域（DXCD=上/忐）且 DXZC>0 下统计
                in_main = (cd in DXCD_MAIN) and (zc > 0)

                # ===== 1. 升势判定：DXAB>0 且 DXZB>0 =====
                if in_main:
                    if ab > 0 and zb > 0:
                        stat['升势_DXAB>0且DXZB>0'][0] += 1
                        stat['升势_DXAB>0且DXZB>0'][1] += hit
                    elif ab > 0 and zb <= 0:
                        stat['DXAB>0但DXZB<=0'][0] += 1
                        stat['DXAB>0但DXZB<=0'][1] += hit
                    elif ab <= 0 and zb > 0:
                        stat['DXAB<=0但DXZB>0'][0] += 1
                        stat['DXAB<=0但DXZB>0'][1] += hit
                    else:
                        stat['DXAB<=0且DXZB<=0'][0] += 1
                        stat['DXAB<=0且DXZB<=0'][1] += hit

                # ===== 2. 三类入口（需前一柱）=====
                if prev and in_main:
                    p_cd, p_hx, p_za, p_zc, p_zb, p_ab = prev
                    # DJC入口：ZC 由 ≤0 转 >0（初/储）
                    if p_zc <= 0 and zc > 0:
                        stat['入口_DJC(ZC转正)'][0] += 1
                        stat['入口_DJC(ZC转正)'][1] += hit
                    # DJB入口：ZB 由 ≤0 转 >0（上破DJB）
                    if p_zb <= 0 and zb > 0:
                        stat['入口_DJB(ZB转正)'][0] += 1
                        stat['入口_DJB(ZB转正)'][1] += hit
                    # DJA入口：ZA 由 ≤0 转 >0（上破DJA）
                    if p_za <= 0 and za > 0:
                        stat['入口_DJA(ZA转正)'][0] += 1
                        stat['入口_DJA(ZA转正)'][1] += hit

                # ===== 3. 丙丁戊（DXZC>0 下）=====
                if in_main and hx in ('丙', '丁', '戊'):
                    stat['丙丁戊_DXZC>0'][0] += 1
                    stat['丙丁戊_DXZC>0'][1] += hit

                # ===== 4. 阴柱介入（主升区）=====
                if in_main:
                    if chg < 0:
                        stat['主升_阴柱'][0] += 1
                        stat['主升_阴柱'][1] += hit
                    else:
                        stat['主升_阳柱'][0] += 1
                        stat['主升_阳柱'][1] += hit

                prev = (cd, hx, za, zc, zb, ab)

    # 输出
    print(f'\n{"标签":<24} {"n":>8} {"P(≥2%)":>8}')
    print('-' * 45)
    results = []
    for tag, (n, hit) in stat.items():
        if n == 0:
            continue
        p = hit / n
        results.append((tag, n, p))
    results.sort(key=lambda x: -x[2])
    for tag, n, p in results:
        flag = ' ⚠样本不足' if n < MIN_SAMPLE else ''
        print(f'{tag:<24} {n:>8} {p:>8.4f}{flag}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tag', 'n', 'hit', 'P(>=2%)'])
        for tag, n, p in results:
            w.writerow([tag, n, int(n * p), f'{p:.4f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
