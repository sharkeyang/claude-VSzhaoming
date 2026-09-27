#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
贝叶斯逐级更新 — 组合特征分析（案例5气象预报模式）

核心思想：不是单看一个特征，而是逐级叠加，看概率能推到多高。
    P(冲高≥2%) = 37.2% (基线)
    → 门开 → 43.4%
    → 门开 + 顶型龙 → ?
    → 门开 + 顶型龙 + 护型乙 → ?

这告诉你"门开之后，再叠加什么最有用"，是真正能指导仓位/介入决策的部分。

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [8] DXCD 护级   [9] 护型   [13] 日ZA   [14] 日ZC   [15] 日ZE
    [26] 次日高幅   [43] 顶型   [44] 日等型

用法：
    python _产出物/_工具/vba表贝叶斯组合.py
"""
import csv, os, math, io
from collections import defaultdict

# ---------- 配置 ----------
TARGET_THRESHOLD = 2.0          # 目标：次日冲高≥2%
MIN_SAMPLE = 1000               # 组合样本量下限（组合会稀释样本，用1000）
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/贝叶斯组合结果.csv'

# 护型映射（首字符）
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def combo_tags(row):
    """
    返回该样本所属的组合特征标签（逐级叠加）。
    组合路径（从门开出发，逐级叠加）：
      - 门开
      - 门开+顶型龙
      - 门开+护型X
      - 门开+等型等N
      - 门开+顶型龙+护型X
      - 门开+顶型龙+等型等N
      - 门开+护型X+等型等N
      - 门开+顶型龙+护型X+等型等N
    """
    tags = []
    try:
        zc = float(row[14])
    except (ValueError, IndexError):
        zc = 0.0
    cd = row[8].strip() if len(row) > 8 else ''
    is_open = (zc > 0 and cd == '上')

    top = row[43].strip() if len(row) > 43 else ''
    is_long = top.startswith('a') or top.startswith('b')

    deng = row[44].strip() if len(row) > 44 else ''
    deng_num = deng[1] if (deng and deng[0] == '等' and len(deng) > 1) else ''

    hx = HX_MAP.get(row[9][0]) if (len(row) > 9 and row[9]) else None

    if not is_open:
        return tags  # 只分析门开条件下的组合

    tags.append('门开')
    if is_long:
        tags.append('门开+顶型龙')
    if hx:
        tags.append(f'门开+护型{hx}')
    if deng_num:
        tags.append(f'门开+等型等{deng_num}')
    if is_long and hx:
        tags.append(f'门开+顶型龙+护型{hx}')
    if is_long and deng_num:
        tags.append(f'门开+顶型龙+等型等{deng_num}')
    if hx and deng_num:
        tags.append(f'门开+护型{hx}+等型等{deng_num}')
    if is_long and hx and deng_num:
        tags.append(f'门开+顶型龙+护型{hx}+等型等{deng_num}')
    return tags


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    feat_stat = defaultdict(lambda: [0, 0])
    global_total = 0
    global_hit = 0

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
                if len(row) < 27:
                    continue
                try:
                    next_high = float(row[26])
                except ValueError:
                    continue
                hit = 1 if next_high >= TARGET_THRESHOLD else 0
                global_total += 1
                global_hit += hit
                for tag in combo_tags(row):
                    feat_stat[tag][0] += 1
                    feat_stat[tag][1] += hit

    p_prior = global_hit / global_total if global_total else 0.0
    print(f'\n全样本: n={global_total}, 次日冲高≥{TARGET_THRESHOLD}% 基线 P(A)={p_prior:.4f}')

    # 计算每个组合的 P(A|B) 和相对基线的提升
    results = []
    for feat, (n, hit) in feat_stat.items():
        if n == 0:
            continue
        p_obs = hit / n
        delta_prior = (p_obs - p_prior) * 100
        insufficient = n < MIN_SAMPLE
        results.append({
            'feature': feat, 'n': n, 'hit': hit,
            'p_obs': p_obs, 'p_prior': p_prior,
            'delta_prior': delta_prior,
            'insufficient': insufficient,
        })

    # 排序：按 P(A|B) 降序（概率越高越值得介入）
    results.sort(key=lambda x: x['p_obs'], reverse=True)

    # 控制台输出
    print(f'\n{"组合特征":<28} {"n":>8} {"P(A|B)":>8} {"基线":>7} {"Δpp":>7}')
    print('-' * 62)
    for r in results:
        flag = ' ⚠样本不足' if r['insufficient'] else ''
        print(f'{r["feature"]:<28} {r["n"]:>8} {r["p_obs"]:>8.4f} {r["p_prior"]:>7.4f} '
              f'{r["delta_prior"]:>+7.2f}{flag}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['combo', 'n', 'hit', 'P(A|B)', 'P(A)_prior', 'delta_pp', 'insufficient'])
        for r in results:
            w.writerow([r['feature'], r['n'], r['hit'], f"{r['p_obs']:.4f}",
                        f"{r['p_prior']:.4f}", f"{r['delta_prior']:+.2f}",
                        r['insufficient']])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
