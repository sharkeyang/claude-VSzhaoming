#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DXAB>0 升势判定深化验证 — 稳健性/等型叠加/阴柱叠加/护型关系

背景：已确认 DXZB 边际贡献小（+0.20pp），升势判定可简化为"DXAB>0"。
     本脚本深化验证 DXAB>0 的适用范围与叠加方式：
     方向1: DXAB>0 在不同 DXCD（上/忐/忠）下的稳健性
     方向3: DXAB>0 叠加等型（等1/等2/等3/等7）
     方向4: DXAB>0 叠加阴柱/阳柱
     方向2: DXAB>0 与护型（甲乙己 vs 丙丁戊）

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD   [9] 护型   [13] 日ZA   [14] 日ZC
    [26] 次日高幅   [44] 日等型   [64] DTAB

用法：
    python _产出物/_工具/vba表DXAB深化.py
"""
import csv, os, io
from collections import defaultdict

# ---------- 配置 ----------
TARGET = 2.0
MIN_SAMPLE = 1000
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/DXAB深化结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    stat = defaultdict(lambda: [0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 66:
                    continue
                try:
                    next_high = float(row[26])
                    zc = float(row[14])
                    ab = float(row[64])
                    chg = float(row[5])
                except ValueError:
                    continue
                cd = row[8].strip()
                hx = HX_MAP.get(row[9][0]) if row[9] else None
                deng = row[44].strip() if len(row) > 44 else ''
                deng_num = deng[1] if (deng and deng[0] == '等' and len(deng) > 1) else ''
                hit = 1 if next_high >= TARGET else 0

                # 只在 DXZC>0 下统计（基本条件）
                if zc <= 0:
                    continue

                # ===== 方向1: DXAB>0 在不同 DXCD 下 =====
                if ab > 0:
                    stat[f'DXAB>0_CD={cd}'][0] += 1
                    stat[f'DXAB>0_CD={cd}'][1] += hit
                    # 方向3: 叠加等型
                    if deng_num:
                        stat[f'DXAB>0_等{deng_num}'][0] += 1
                        stat[f'DXAB>0_等{deng_num}'][1] += hit
                    # 方向4: 叠加阴柱/阳柱
                    if chg < 0:
                        stat['DXAB>0_阴柱'][0] += 1
                        stat['DXAB>0_阴柱'][1] += hit
                    else:
                        stat['DXAB>0_阳柱'][0] += 1
                        stat['DXAB>0_阳柱'][1] += hit
                    # 方向2: 护型
                    if hx in ('甲', '乙', '己'):
                        stat['DXAB>0_甲乙己'][0] += 1
                        stat['DXAB>0_甲乙己'][1] += hit
                    elif hx in ('丙', '丁', '戊'):
                        stat['DXAB>0_丙丁戊'][0] += 1
                        stat['DXAB>0_丙丁戊'][1] += hit
                else:
                    stat[f'DXAB<=0_CD={cd}'][0] += 1
                    stat[f'DXAB<=0_CD={cd}'][1] += hit

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
