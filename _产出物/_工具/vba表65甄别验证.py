#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
§6.5 备选介入点甄别验证 — 介入点看"冲高获利"，非"恢复"

对 §6.5.1 介入点汇总表的各备选介入点，计算介入后的获利指标：
- 短期：次日P≥3%、次日均高幅
- 中期：5日P≥3%（5日内冲高）、5日持有收益
- 长期：10日/20日冲高（未来N日内高幅≥3%）

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [5] 涨幅   [8] DXCD   [9] 护型   [10] 柱排   [13] 日ZA   [14] 日ZC
    [19] BSHA   [21] 管宽哼JA   [26] 次日高幅   [30] 上符串   [44] 日等型

用法：
    python _产出物/_工具/vba表65甄别验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

# ---------- 配置 ----------
DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/65甄别验证结果.csv'
MIN_SAMPLE = 1000

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计：备选 -> [n, 次日P3, 次日均高幅, 5日P3, 5日持有收益, 10日P3, 20日P3]
    stat = defaultdict(lambda: [0, 0, 0.0, 0, 0.0, 0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[5, 8, 9, 10, 13, 14, 19, 21, 26, 30, 44])
            df.columns = ['涨幅', 'DXCD', '护型', '柱排', '日ZA', '日ZC', 'BSHA', '管宽', '次日高幅', '上符串', '日等型']
        except Exception:
            continue
        for c in ['涨幅', '日ZA', '日ZC', 'BSHA', '管宽', '次日高幅']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['日ZA', '次日高幅'])
        if df.empty:
            continue

        # 未来N日冲高（未来N日内高幅≥3%）
        df['5日冲高'] = (df['次日高幅'].shift(-1).fillna(0) >= 3) | (df['次日高幅'].shift(-2).fillna(0) >= 3) | \
                       (df['次日高幅'].shift(-3).fillna(0) >= 3) | (df['次日高幅'].shift(-4).fillna(0) >= 3) | \
                       (df['次日高幅'].shift(-5).fillna(0) >= 3)
        df['10日冲高'] = df['5日冲高'] | (df['次日高幅'].shift(-6).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-7).fillna(0) >= 3) | (df['次日高幅'].shift(-8).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-9).fillna(0) >= 3) | (df['次日高幅'].shift(-10).fillna(0) >= 3)
        df['20日冲高'] = df['10日冲高'] | (df['次日高幅'].shift(-11).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-12).fillna(0) >= 3) | (df['次日高幅'].shift(-13).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-14).fillna(0) >= 3) | (df['次日高幅'].shift(-15).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-16).fillna(0) >= 3) | (df['次日高幅'].shift(-17).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-18).fillna(0) >= 3) | (df['次日高幅'].shift(-19).fillna(0) >= 3) | \
                        (df['次日高幅'].shift(-20).fillna(0) >= 3)
        # 5日持有收益（未来5日累计涨幅，用收盘价近似：未来5日涨幅和）
        df['5日收益'] = df['涨幅'].shift(-1).fillna(0) + df['涨幅'].shift(-2).fillna(0) + \
                       df['涨幅'].shift(-3).fillna(0) + df['涨幅'].shift(-4).fillna(0) + df['涨幅'].shift(-5).fillna(0)

        # 护型首字符
        df['护型码'] = df['护型'].astype(str).str[0]
        df['hx'] = df['护型码'].map(HX_MAP)
        # 等型
        df['等型'] = df['日等型'].astype(str).str[1]
        # 触顶（上符串右端A）
        df['触顶'] = df['上符串'].astype(str).str.endswith('A')
        # 升排（柱排以升开头）
        df['升排'] = df['柱排'].astype(str).str.startswith('升')
        # 甲乙己
        df['甲乙己'] = df['hx'].isin(['甲', '乙', '己'])

        # 备选介入点判定
        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += int((sub['次日高幅'] >= 3).sum())
            s[2] += float(sub['次日高幅'].sum())
            s[3] += int(sub['5日冲高'].sum())
            s[4] += float(sub['5日收益'].sum())
            s[5] += int(sub['10日冲高'].sum())
            s[6] += int(sub['20日冲高'].sum())

        # 等1 备选
        mark(df['等型'] == '1', '等1_当天介入')
        mark((df['等型'] == '1') & (df['日ZA'].shift(-1) > 1), '等1_第2柱确认')
        mark((df['等型'] == '1') & (df['BSHA'] >= 5), '等1_BSHA5')
        # 等2 备选
        mark((df['等型'] == '2') & (df['触顶']) & (df['升排']), '等2_触顶升排')
        # 等3 备选
        mark((df['等型'] == '3') & (df['管宽'] >= 4) & (df['触顶']) & (df['升排']), '等3_扩管')
        mark((df['等型'] == '3') & (df['管宽'] >= 4) & ~(df['触顶'] & df['升排']), '等3_平管')
        mark((df['等型'] == '3') & (df['BSHA'] >= 5), '等3_BSHA5')
        # 等5 备选
        mark(df['等型'] == '5', '等5_首下破')
        mark((df['等型'] == '6') & (df['涨幅'] > 0) & (df['日ZA'].shift(-1) > 0), '等5_等6第二柱阳柱+次日再站DJA')

    # 输出
    print(f'\n{"备选介入点":<28} {"n":>8} {"次日P3":>7} {"次日均高":>7} {"5日P3":>6} {"5日收益":>7} {"10日P3":>7} {"20日P3":>7}')
    print('-' * 85)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        p3 = s[1] / n * 100
        avg = s[2] / n
        p5 = s[3] / n * 100
        r5 = s[4] / n
        p10 = s[5] / n * 100
        p20 = s[6] / n * 100
        results.append((name, n, p3, avg, p5, r5, p10, p20))
    results.sort(key=lambda x: -x[2])
    for name, n, p3, avg, p5, r5, p10, p20 in results:
        flag = ' ⚠样本不足' if n < MIN_SAMPLE else ''
        print(f'{name:<28} {n:>8} {p3:>6.2f}% {avg:>6.2f}% {p5:>5.1f}% {r5:>6.2f}% {p10:>6.1f}% {p20:>6.1f}%{flag}')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['备选', 'n', '次日P3%', '次日均高幅%', '5日P3%', '5日收益%', '10日P3%', '20日P3%'])
        for name, n, p3, avg, p5, r5, p10, p20 in results:
            w.writerow([name, n, f'{p3:.2f}', f'{avg:.2f}', f'{p5:.1f}', f'{r5:.2f}', f'{p10:.1f}', f'{p20:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
