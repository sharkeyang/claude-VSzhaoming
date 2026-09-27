#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DXZB 边际贡献验证 — 用真实 DTZB[62]/DTAB[64] 检验升势判定

核心问题：§6.7.2 框架判定"（DXAB>0 且 DXZB>0）是升势"。
         本脚本验证 DXZB>0 相对 DXAB>0 的边际贡献——如果 DXZB 增量小，
         则升势判定可简化为"DXAB>0"。

同时验证 DJA 入口分合顶/离顶（用 ≥2% 目标，§6.7.2 旧数据是 ≥3%）。

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD   [9] 护型   [13] 日ZA   [14] 日ZC
    [26] 次日高幅   [30] 上符串   [62] DTZB   [64] DTAB

用法：
    python _产出物/_工具/vba表DXZB边际贡献.py
"""
import csv, os, io
from collections import defaultdict

# ---------- 配置 ----------
TARGET = 2.0
MIN_SAMPLE = 1000
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/DXZB边际贡献结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
DXCD_MAIN = {'上', '忐'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])
    prev = None  # (za, zc, zb, ab)

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
                except ValueError:
                    prev = None
                    continue
                cd = row[8].strip()
                shangfu = row[30].strip() if len(row) > 30 else ''
                hit = 1 if next_high >= TARGET else 0
                in_main = (cd in DXCD_MAIN) and (zc > 0)

                if in_main:
                    # ===== DXZB 边际贡献 =====
                    if ab > 0:
                        stat['DXAB>0(不管ZB)'][0] += 1
                        stat['DXAB>0(不管ZB)'][1] += hit
                        if zb > 0:
                            stat['DXAB>0且DXZB>0'][0] += 1
                            stat['DXAB>0且DXZB>0'][1] += hit
                        else:
                            stat['DXAB>0但DXZB<=0'][0] += 1
                            stat['DXAB>0但DXZB<=0'][1] += hit
                    else:
                        stat['DXAB<=0(不管ZB)'][0] += 1
                        stat['DXAB<=0(不管ZB)'][1] += hit

                    # ===== DJA 入口分合顶/离顶 =====
                    if prev:
                        p_za, p_zc, p_zb, p_ab = prev
                        if p_za <= 0 and za > 0:  # ZA转正 = DJA入口
                            if shangfu.endswith('A'):
                                stat['DJA入口_合顶'][0] += 1
                                stat['DJA入口_合顶'][1] += hit
                            else:
                                stat['DJA入口_离顶'][0] += 1
                                stat['DJA入口_离顶'][1] += hit

                prev = (za, zc, zb, ab)

    # 输出
    print(f'\n{"标签":<24} {"n":>8} {"P(≥2%)":>8}')
    print('-' * 45)
    results = []
    for tag, (n, hit) in stat.items():
        if n == 0:
            continue
        results.append((tag, n, hit / n))
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
