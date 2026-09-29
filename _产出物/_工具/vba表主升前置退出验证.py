#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：§8.1.4.4/8.1.4.5 各情况与主升条件（WXAB>0 且 WXZB>0）的关系

用户假设（2026-09-29）：
§8.1.4.4（由负转正，主升条件前置）：
1. 情况1（前周WTAB=1+升排）实际已经是 WXAB 正交
2. 情况2（己+前WTZB>0+升排）与情况3（戊+前WTZA>0+升排+连阳）可以作为主升条件前置
3. 情况4（前WTZA<0今WTZA>0）不作为主升条件前置
4. 单纯 WXZA>0 也不作为主升条件前置

§8.1.4.5（由正转负，主升条件退出）：
1. 情况1（前周WTAB=-1+跌排）、情况2（丙+前WTZB<0+跌排）实际都不满足主升条件
2. 情况3（乙+前WTZA<0+跌排+连阴）可以作为主升条件提前退出
3. 其他情况按 DXZC 进行操作，但都不认为是主升退出

主升条件 = WXAB>0 且 WXZB>0（当前周）
"进入主升" = 当前周满足主升条件
"离开主升" = 当前周满足主升，但下周不满足

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4] WXAB护型  [6] 柱排周  [14] WXZA  [15] WXZB  [16] WXZC  [20] AB周

用法：
    python _产出物/_工具/vba表主升前置退出验证.py
"""
import csv, os, io
import pandas as pd
from collections import defaultdict

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升前置退出验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


def load_board_map():
    import json
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 统计：场景 -> [n, 当前主升数, 下周主升数, 当前主升且下周离开数]
    stat = defaultdict(lambda: [0, 0, 0, 0])

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0], usecols=[4, 6, 14, 15, 16, 20])
            df.columns = ['WXAB护型', '柱排周', 'WXZA', 'WXZB', 'WXZC', 'AB周']
        except Exception:
            continue
        for c in ['WXZA', 'WXZB', 'WXZC', 'AB周']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['WXZA', 'WXZB', 'WXZC', 'AB周'])
        if df.empty:
            continue

        df['hx'] = df['WXAB护型'].astype(str).str[0].map(HX_MAP)
        df['next_AB'] = df['AB周'].shift(-1)
        df['next_WXZB'] = df['WXZB'].shift(-1)
        df['prev_AB'] = df['AB周'].shift(1)
        df['prev_WXZA'] = df['WXZA'].shift(1)
        df['prev_WXZB'] = df['WXZB'].shift(1)
        df['柱排str'] = df['柱排周'].astype(str)
        df['升排'] = df['柱排str'].str.startswith('升')
        df['连阳'] = df['柱排str'].str.startswith('升') & df['柱排str'].str.contains('连')
        df['跌排'] = df['柱排str'].str.startswith('跌')
        df['连阴'] = df['柱排str'].str.startswith('跌') & df['柱排str'].str.contains('连')

        # 主升条件 = WXAB>0 且 WXZB>0
        df['主升'] = (df['AB周'] > 0) & (df['WXZB'] > 0)
        # 下周主升
        df['next_主升'] = (df['next_AB'] > 0) & (df['next_WXZB'] > 0)

        def mark(cond, name):
            sub = df[cond]
            if sub.empty:
                return
            s = stat[name]
            s[0] += len(sub)
            s[1] += int(sub['主升'].sum())
            s[2] += int(sub['next_主升'].sum())
            # 当前主升且下周离开
            s[3] += int(((sub['主升']) & (~sub['next_主升'])).sum())

        # ===== §8.1.4.4 由负转正（主升条件前置）=====
        # 情况1：前周WTAB=1+升排（是否已经是主升）
        mark((df['prev_AB'] == 1) & (df['升排']), '情况1_前周WTAB=1+升排')
        # 情况2：己+前WTZB>0+升排
        mark((df['hx'] == '己') & (df['prev_WXZB'] > 0) & (df['WXZA'] > 0) & (df['升排']), '情况2_己+前WTZB>0+升排')
        # 情况3：戊+前WTZA>0+升排+连阳
        mark((df['hx'] == '戊') & (df['prev_WXZA'] > 0) & (df['WXZA'] > 0) & (df['升排']) & (df['连阳']), '情况3_戊+前WTZA>0+升排+连阳')
        # 情况4：前WTZA<0今WTZA>0
        mark((df['prev_WXZA'] < 0) & (df['WXZA'] > 0), '情况4_前WTZA<0今WTZA>0')
        # 单纯 WXZA>0
        mark(df['WXZA'] > 0, '单纯WXZA>0')

        # ===== §8.1.4.5 由正转负（主升条件退出）=====
        # 情况1：前周WTAB=-1+跌排（是否已经不满足主升）
        mark((df['prev_AB'] == -1) & (df['跌排']), '退_情况1_前周WTAB=-1+跌排')
        # 情况2：丙+前WTZB<0+跌排
        mark((df['hx'] == '丙') & (df['prev_WXZB'] < 0) & (df['WXZA'] < 0) & (df['跌排']), '退_情况2_丙+前WTZB<0+跌排')
        # 情况3：乙+前WTZA<0+跌排+连阴（当前主升但下周离开）
        mark((df['hx'] == '乙') & (df['prev_WXZA'] < 0) & (df['WXZA'] < 0) & (df['跌排']) & (df['连阴']), '退_情况3_乙+前WTZA<0+跌排+连阴')

    # 输出
    print(f'\n=== 主升条件（WXAB>0 且 WXZB>0）前置/退出验证 ===')
    print(f'{"场景":<30} {"n":>8} {"当前主升%":>9} {"下周主升%":>9} {"主升后离开%":>10}')
    print('-' * 75)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        cur = s[1] / n * 100
        nxt = s[2] / n * 100
        leave = s[3] / s[1] * 100 if s[1] else 0
        results.append((name, n, cur, nxt, leave))
    for name, n, cur, nxt, leave in results:
        print(f'{name:<30} {n:>8} {cur:>8.1f}% {nxt:>8.1f}% {leave:>9.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '当前主升%', '下周主升%', '主升后离开%'])
        for name, n, cur, nxt, leave in results:
            w.writerow([name, n, f'{cur:.1f}', f'{nxt:.1f}', f'{leave:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()