#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
跌破 DJA 止损规则实际效果验证

验证用户问题：当 DXCD=上 时，如果都变为 DXCD 变坏（中/下/忑），
说明早就发生了跌破 DJA——"跌破 DJA 且 DXCD 变坏才止损"是否太晚？

模拟：从 DXCD=上 且 日ZA>0（持有）开始，跟踪到 DXCD 变坏（中/下/忑），
看：1) 从跌破 DJA（日ZA<0）到 DXCD 变坏过了多少天
    2) 期间回撤多大（用收盘价近似）

数据来源：谕组日 CSV（高波池 Qic/Qim/Qit），GBK 编码，66 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [1] 收   [8] DXCD   [13] 日ZA   [14] 日ZC

用法：
    python _产出物/_工具/vba表止损规则验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/止损规则验证结果.csv'


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

    # 统计：从跌破DJA到DXCD变坏的天数分布
    days_to_bad = defaultdict(int)
    # 从跌破DJA到DXCD变坏期间的回撤
    drawdowns = []
    # 跌破DJA时DXCD还是上的比例
    n_break_dja_cd_up = 0
    n_break_dja_total = 0
    # DXCD变坏时，跌破DJA已发生天数
    n_bad_after_break = 0
    n_bad_total = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[1, 8, 13, 14])
            df.columns = ['收', 'DXCD', '日ZA', '日ZC']
        except Exception:
            continue
        for c in ['收', '日ZA', '日ZC']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['日ZA', '收'])
        if df.empty:
            continue

        cd = df['DXCD'].astype(str).values
        za = df['日ZA'].values
        close = df['收'].values
        n = len(df)

        # 遍历：从 DXCD=上 且 日ZA>0（持有）开始
        idx = 0
        while idx < n:
            # 找持有起点：DXCD=上 且 日ZA>0
            if cd[idx] == '上' and za[idx] > 0:
                # 记录买入价
                buy_price = close[idx]
                # 跟踪到 DXCD 变坏（中/下/忑）
                j = idx + 1
                max_close = buy_price
                while j < n:
                    max_close = max(max_close, close[j])
                    if cd[j] in ('中', '下', '忑'):
                        # DXCD 变坏，检查是否已跌破 DJA（日ZA<0）
                        n_bad_total += 1
                        # 从买入到变坏，是否跌破过 DJA
                        broke_dja = any(za[k] < 0 for k in range(idx, j + 1))
                        if broke_dja:
                            n_bad_after_break += 1
                            # 从跌破DJA到变坏的天数
                            first_break = next(k for k in range(idx, j + 1) if za[k] < 0)
                            days = j - first_break
                            days_to_bad[days] += 1
                            # 回撤（从最高点到变坏收盘）
                            dd = (max_close - close[j]) / max_close * 100
                            drawdowns.append(dd)
                        break
                    j += 1
                idx = j + 1
            else:
                idx += 1

        # 统计跌破DJA时DXCD还是上的比例
        for k in range(n):
            if za[k] < 0:
                n_break_dja_total += 1
                if cd[k] == '上':
                    n_break_dja_cd_up += 1

    # 输出
    print(f'\n=== 跌破 DJA 时 DXCD 状态 ===')
    print(f'跌破DJA总数: {n_break_dja_total}, 其中DXCD=上: {n_break_dja_cd_up} ({n_break_dja_cd_up/n_break_dja_total*100:.1f}%)')

    print(f'\n=== DXCD 变坏时，是否已跌破 DJA ===')
    print(f'DXCD变坏总数: {n_bad_total}, 其中已跌破DJA: {n_bad_after_break} ({n_bad_after_break/n_bad_total*100:.1f}%)')

    print(f'\n=== 从跌破 DJA 到 DXCD 变坏的天数分布 ===')
    for d in sorted(days_to_bad.keys()):
        print(f'  {d}天: {days_to_bad[d]}')

    print(f'\n=== 从跌破 DJA 到 DXCD 变坏期间的回撤 ===')
    if drawdowns:
        import statistics
        print(f'  平均回撤: {statistics.mean(drawdowns):.2f}%')
        print(f'  中位回撤: {statistics.median(drawdowns):.2f}%')
        print(f'  最大回撤: {max(drawdowns):.2f}%')
        print(f'  回撤≥5%: {sum(1 for d in drawdowns if d>=5)/len(drawdowns)*100:.1f}%')
        print(f'  回撤≥10%: {sum(1 for d in drawdowns if d>=10)/len(drawdowns)*100:.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['指标', '值'])
        w.writerow(['跌破DJA总数', n_break_dja_total])
        w.writerow(['跌破DJA且DXCD=上', f'{n_break_dja_cd_up} ({n_break_dja_cd_up/n_break_dja_total*100:.1f}%)'])
        w.writerow(['DXCD变坏总数', n_bad_total])
        w.writerow(['DXCD变坏且已跌破DJA', f'{n_bad_after_break} ({n_bad_after_break/n_bad_total*100:.1f}%)'])
        if drawdowns:
            import statistics
            w.writerow(['平均回撤', f'{statistics.mean(drawdowns):.2f}%'])
            w.writerow(['中位回撤', f'{statistics.median(drawdowns):.2f}%'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()