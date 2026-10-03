#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：主升条件与主升前置重构（2026-10-01）— 修正版

用户新口径：
1. 主升条件 = WXAB>0 且 WXZB>0
2. 主升初始 = 主升条件 且 WTAB≤3（AB周[20]交叉天数≤3）
3. 主升前置 = 降转（WXAB<0 且 WXZB>0）= 本周己护型
   - 不需附加 WJA柱排（降转时 WXZA>0 恒成立，冗余）
4. 原主升前置（WXAB<0 且 WXZA>0 且在WJA柱排多柱）→ 降级为"降主中的空头提前退出"
5. 前周丁/戊(WXZA<0) 不作为主升前置（本身转甲率极低）

关键修正（2026-10-01）：
- 前周丁/戊(WXZA<0) 本身转甲率仅 4.7%/3.8%（与"戊转甲3.44%"吻合）
- 本周己（降转）转甲率 43.0%（与"己转甲43%"吻合）
- 前周丁/戊(WXZA<0)+本周己 显示的 46.1%/42.4% 是"丁/戊→己→甲"三段转移，
  其中"己→甲"贡献43%转甲率，前周丁/戊条件未提升任何转甲概率

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引： [1]周涨 [3]HR [4]WXAB护型 [6]柱排周 [14]WXZA [15]WXZB [20]AB周
"""
import csv, os, io, json, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/主升前置重构验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}


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

    # 场景 -> [n, 下周主升, 下周WXZB>0, 下周周涨和, 下周正涨, 下周HR和, 下周HR>3]
    stat = defaultdict(lambda: [0, 0, 0, 0.0, 0, 0.0, 0])

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
            zhang = to_f(row[1]); hr = to_f(row[3])
            wxab = to_f(row[20]); wxzb = to_f(row[15]); wxza = to_f(row[14])
            if zhang is None or hr is None or wxab is None or wxzb is None or wxza is None:
                continue
            hx_cn = HX_MAP.get(str(row[4])[:1], '')
            zhupai = str(row[6])
            shengpai = zhupai.startswith('升')

            # 下周数据
            if idx + 1 >= n:
                continue
            nxt = rows[idx + 1]
            if len(nxt) <= 20:
                continue
            nxt_ab = to_f(nxt[20]); nxt_zb = to_f(nxt[15])
            nxt_zhang = to_f(nxt[1]); nxt_hr = to_f(nxt[3])
            if nxt_ab is None or nxt_zb is None or nxt_zhang is None or nxt_hr is None:
                continue

            nxt_zhsheng = (nxt_ab > 0) and (nxt_zb > 0)
            nxt_zb_pos = nxt_zb > 0

            def mark(cond, name):
                if not cond:
                    return
                s = stat[name]
                s[0] += 1
                if nxt_zhsheng: s[1] += 1
                if nxt_zb_pos: s[2] += 1
                s[3] += nxt_zhang
                if nxt_zhang > 0: s[4] += 1
                s[5] += nxt_hr
                if nxt_hr > 3: s[6] += 1

            zhsheng = (wxab > 0) and (wxzb > 0)
            jiangzhuan = (wxab < 0) and (wxzb > 0)   # 降转 = 本周己护型
            jiangzhu = (wxab < 0) and (wxzb < 0)     # 降主

            # 前一周护型
            p_hx_cn = ''
            p_wxza = None
            if idx - 1 >= 0:
                prow = rows[idx - 1]
                if len(prow) > 20:
                    p_hx_cn = HX_MAP.get(str(prow[4])[:1], '')
                    p_wxza = to_f(prow[14])

            # ===== Part 1: 主升前置（降转=本周己护型）=====
            mark(jiangzhuan, '主升前置_降转(本周己)整体')
            # 前周护型对"本周己→下周主升"的影响
            if p_hx_cn == '己':
                mark(jiangzhuan, '主升前置_前周己+本周己')
            elif p_hx_cn == '丁' and p_wxza is not None and p_wxza < 0:
                mark(jiangzhuan, '主升前置_前周丁(WXZA<0)+本周己')
            elif p_hx_cn == '戊' and p_wxza is not None and p_wxza < 0:
                mark(jiangzhuan, '主升前置_前周戊(WXZA<0)+本周己')
            elif p_hx_cn == '戊' and p_wxza is not None and p_wxza > 0:
                mark(jiangzhuan, '主升前置_前周戊(WXZA>0)+本周己')

            # ===== Part 2: 前周丁/戊(WXZA<0)本身转甲率（不作为主升前置的依据）=====
            if p_hx_cn == '丁' and p_wxza is not None and p_wxza < 0:
                mark(True, '前周丁(WXZA<0)本身')
            if p_hx_cn == '戊' and p_wxza is not None and p_wxza < 0:
                mark(True, '前周戊(WXZA<0)本身')
            if p_hx_cn == '戊' and p_wxza is not None and p_wxza > 0:
                mark(True, '前周戊(WXZA>0)本身')

            # ===== Part 3: 原前置降级为空头提前退出 =====
            yuan_qianzhi = (wxab < 0) and (wxza > 0) and shengpai
            mark(yuan_qianzhi and wxzb < 0, '原前置+WXZB<0(降主子集)')
            mark(yuan_qianzhi and wxzb > 0, '原前置+WXZB>0(降转子集)')
            mark(jiangzhu, '降主整体')

            # ===== Part 4: 主升初始 vs 持续 =====
            mark(zhsheng, '主升整体')
            mark(zhsheng and 0 < wxab <= 3, '主升初始(0<WTAB≤3)')
            mark(zhsheng and wxab > 3, '主升持续(WTAB>3)')

    # 输出
    print(f'\n=== 主升条件与主升前置重构验证（修正版） ===')
    print(f'{"场景":<34} {"n":>8} {"下周主升%":>9} {"下周WXZB>0%":>11} {"下周均涨%":>9} {"下周正涨%":>9} {"下周均HR%":>9} {"P(HR>3%)":>9}')
    print('-' * 100)
    results = []
    for name, s in stat.items():
        if s[0] == 0:
            continue
        n = s[0]
        results.append((name, n,
                        s[1] / n * 100, s[2] / n * 100,
                        s[3] / n, s[4] / n * 100, s[5] / n, s[6] / n * 100))
    results.sort(key=lambda x: -x[2])
    for name, n, nz, nzb, az, pz, ahr, phr3 in results:
        print(f'{name:<34} {n:>8} {nz:>8.1f}% {nzb:>10.1f}% {az:>8.3f}% {pz:>8.1f}% {ahr:>8.2f}% {phr3:>8.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['场景', 'n', '下周主升%', '下周WXZB>0%', '下周均涨%', '下周正涨%', '下周均HR%', 'P(HR>3%)'])
        for name, n, nz, nzb, az, pz, ahr, phr3 in results:
            w.writerow([name, n, f'{nz:.1f}', f'{nzb:.1f}', f'{az:.3f}', f'{pz:.1f}', f'{ahr:.2f}', f'{phr3:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()