#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
贝叶斯因子验证脚本 — 把"pp差距"转成"证据强度"

目标：对每个特征B，算 P(次日冲高≥2% | 特征B) 相对全样本基线的贝叶斯因子(BF)，
     用客观标准判断"这个特征到底有没有用"，终结"这个pp差距算不算结论"的纠结。

核心公式（对数似然比，等价于贝叶斯因子，数值更稳定）：
    LLR = nA·[pA·ln(pA/q) + (1-pA)·ln((1-pA)/(1-q))]
        + nB·[pB·ln(pB/q) + (1-pB)·ln((1-pB)/(1-q))]
    其中 q = (nA·pA + nB·pB)/(nA+nB) 为条件内合并基线
    BF = exp(LLR)

证据强度分级（Jeffreys 标准）：
    BF 1~3      LLR 0~1.1    无价值（噪声）
    BF 3~10     LLR 1.1~2.3  中等证据
    BF 10~30    LLR 2.3~3.4  强证据
    BF >30      LLR >3.4     极强证据

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [8] DXCD 护级   [9] 护型   [13] 日ZA   [14] 日ZC   [15] 日ZE
    [26] 次日高幅   [43] 顶型   [44] 日等型

用法：
    python _产出物/_工具/vba表贝叶斯因子.py
"""
import csv, os, math, io
from collections import defaultdict

# ---------- 配置 ----------
TARGET_THRESHOLD = 2.0          # 目标：次日冲高≥2%
MIN_SAMPLE = 30                 # 样本量下限，低于此标注"样本不足"
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/贝叶斯因子结果.csv'

# 护型映射（首字符）
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
DXCD_ORDER = ['上', '中', '下', '忐', '忠', '忑']


def hx_key(dxab):
    """护型首字符 → 中文护型；无效返回 None"""
    if not dxab or len(dxab) < 1:
        return None
    return HX_MAP.get(dxab[0])


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def classify(row):
    """
    对一行数据做特征分类，返回特征标签列表（一个样本可属多个特征）。
    特征：
      - 门开/门关：ZC>0 且 DXCD=上 → 门开；否则门关
      - 顶型：龙 / 非龙
      - 日等型：等1~等8（取 row[44] 首字符）
      - 护型：甲/乙/丙/丁/戊/己
    """
    tags = []
    try:
        zc = float(row[14])
    except (ValueError, IndexError):
        zc = 0.0
    cd = row[8].strip() if len(row) > 8 else ''
    # 门状态
    if zc > 0 and cd == '上':
        tags.append('门开')
    else:
        tags.append('门关')
    # 顶型
    top = row[43].strip() if len(row) > 43 else ''
    if top.startswith('a') or top.startswith('b'):
        tags.append('顶型_龙')
    else:
        tags.append('顶型_非龙')
    # 日等型（如 '等1'~'等8'，取数字部分）
    deng = row[44].strip() if len(row) > 44 else ''
    if deng and deng[0] == '等' and len(deng) > 1:
        tags.append(f'等型_等{deng[1]}')
    # 护型
    hx = hx_key(row[9]) if len(row) > 9 else None
    if hx:
        tags.append(f'护型_{hx}')
    return tags


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计：feature -> [n_present, hit_present]
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
                for tag in classify(row):
                    feat_stat[tag][0] += 1
                    feat_stat[tag][1] += hit

    # 全局基线
    p_prior = global_hit / global_total if global_total else 0.0
    print(f'\n全样本: n={global_total}, 次日冲高≥{TARGET_THRESHOLD}% 基线 P(A)={p_prior:.4f}')

    # 计算每个特征的 BF（特征出现 vs 特征不出现，互补组对比）
    # 互补组用恒等式 O(1) 求：n_absent = 全局n - 特征n，hit_absent = 全局hit - 特征hit
    results = []
    for feat, (n_p, hit_p) in feat_stat.items():
        n_a = global_total - n_p
        if n_p == 0 or n_a == 0:
            continue
        hit_a = global_hit - hit_p
        p_present = hit_p / n_p
        p_absent = hit_a / n_a
        # 合并基线 q = (n_p·p_present + n_a·p_absent)/(n_p+n_a)
        q = (hit_p + hit_a) / (n_p + n_a)
        # 对数似然比（两组的似然比之和）
        def _llr(p, n, q):
            if p <= 0 or p >= 1 or q <= 0 or q >= 1:
                return 0.0
            return n * (p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q)))
        llr = _llr(p_present, n_p, q) + _llr(p_absent, n_a, q)
        # BF = exp(LLR)，超大样本下 LLR 极大，exp 会溢出 → 用 inf 表示"极强证据"
        try:
            bf = math.exp(llr)
        except OverflowError:
            bf = float('inf')
        # 证据分级：超大样本(1115万行)下，任何微小差异都会让 LLR 巨大，
        # 用绝对 LLR 分级会全部爆表失去区分度。
        # 改用"每样本平均证据" LLR/n（样本量无关），衡量每个样本贡献的证据量，
        # 再结合方向性（Δpp 正负）判断特征是否提升概率。
        per_sample = llr / (n_p + n_a) if (n_p + n_a) else 0.0
        if p_present < p_absent:
            grade = '反向(特征反而降低概率)'
        elif per_sample < 0.0001:
            grade = '无价值(噪声)'
        elif per_sample < 0.001:
            grade = '弱证据'
        elif per_sample < 0.005:
            grade = '中等证据'
        else:
            grade = '强证据'
        insufficient = n_p < MIN_SAMPLE
        results.append({
            'feature': feat, 'n': n_p, 'hit': hit_p,
            'p_obs': p_present, 'p_prior': p_prior,
            'p_absent': p_absent,
            'delta_pp': (p_present - p_absent) * 100,
            'bf': bf, 'llr': llr, 'per_sample': per_sample,
            'grade': grade,
            'insufficient': insufficient,
        })

    # 排序：按 Δpp 降序（特征提升概率的幅度）
    results.sort(key=lambda x: x['delta_pp'], reverse=True)

    # 控制台输出
    print(f'\n{"特征":<14} {"n":>8} {"P(A|B)":>8} {"P(A|¬B)":>8} {"Δpp":>7} {"每样本证据":>9} {"证据强度":<12}')
    print('-' * 76)
    for r in results:
        flag = ' ⚠样本不足' if r['insufficient'] else ''
        bf_str = 'inf' if r['bf'] == float('inf') else f'{r["bf"]:.1f}'
        print(f'{r["feature"]:<14} {r["n"]:>8} {r["p_obs"]:>8.4f} {r["p_absent"]:>8.4f} '
              f'{r["delta_pp"]:>+7.2f} {r["per_sample"]:>9.5f} {r["grade"]:<12}{flag}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['feature', 'n', 'hit', 'P(A|B)', 'P(A|notB)', 'delta_pp',
                    'BF', 'LLR', 'per_sample_evidence', 'evidence_grade', 'insufficient'])
        for r in results:
            bf_str = 'inf' if r['bf'] == float('inf') else f"{r['bf']:.2f}"
            w.writerow([r['feature'], r['n'], r['hit'], f"{r['p_obs']:.4f}",
                        f"{r['p_absent']:.4f}", f"{r['delta_pp']:+.2f}",
                        bf_str, f"{r['llr']:.2f}", f"{r['per_sample']:.5f}",
                        r['grade'], r['insufficient']])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
