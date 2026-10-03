#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证：舍弃区域合理性 + 主升条件/主升前置能否固化为周日联动周类判定条件
================================================================
用户猜想（2026-10-01）：
随着分析推进，被舍弃区域越来越多：
    ① DXZC<0 且丙丁戊 → 舍弃
    ② DXZC<0 全部 → 舍弃
    ③ 忠属鸡肋 → 舍弃
    ④ 现在只需操作主升（WXAB>0且WXZB>0）+ 少数主升前置
验证：这种舍弃是否正确？数据是否支持？能否固化为周日联动中周类判定条件？
即：周必须满足主升条件或主升前置，再在此范围内观察日类是否DXZC>0。

主升条件 = WXAB>0 且 WXZB>0
主升前置 = 己 + 前WTZB>0 + 升排（下周进入主升 55.7%）

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，53 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [1] 周涨  [3] HR  [4] WXAB护型  [6] 柱排周  [14] WXZA  [15] WXZB  [16] WXZC  [20] AB周

用法：
    python _产出物/_工具/vba表舍弃区域与主升条件固化验证.py
"""
import csv, os, io, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/舍弃区域与主升条件固化验证结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)


def to_f(v):
    try:
        return float(v)
    except Exception:
        return None


def main():
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # 区域 -> [n, 周涨和, 正周涨数, HR和, HR>3数, 下周主升数, 下周主升或前置数]
    stat = defaultdict(lambda: [0, 0.0, 0, 0.0, 0, 0, 0])

    n_files = 0
    for i, fname in enumerate(files):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        n_files += 1
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
            hx = row[4]
            zp = row[6]
            zhang = to_f(row[1])
            hr = to_f(row[3])
            wxza = to_f(row[14])
            wxzb = to_f(row[15])
            wxzc = to_f(row[16])
            ab = to_f(row[20])
            if hx is None or not hx or zhang is None or hr is None or wxza is None or wxzb is None or wxzc is None or ab is None:
                continue

            # 主升条件
            main_cond = (ab > 0) and (wxzb > 0)
            # 主升前置：己 + 前WTZB>0 + 升排
            prev_wxzb = None
            if idx > 0 and len(rows[idx - 1]) > 15:
                prev_wxzb = to_f(rows[idx - 1][15])
            is_qianzhi = (hx[0] == 'r') and (prev_wxzb is not None and prev_wxzb > 0) and zp.startswith('升')

            # 区域分类（忠 = 戊护型+忠方向 y戊↘忠，即鸡肋；非丁护型）
            if main_cond:
                region = '主升(WXAB>0且WXZB>0)'
            elif is_qianzhi:
                region = '主升前置(己+前WTZB>0+升排)'
            elif '忠' in hx:
                region = '舍弃_忠(戊↘忠,鸡肋)'
            elif wxzc < 0:
                region = '舍弃_DXZC<0'
            else:
                region = '舍弃_其他(非主升/前置/忠/DXZC<0)'

            s = stat[region]
            s[0] += 1
            s[1] += zhang
            if zhang > 0:
                s[2] += 1
            s[3] += hr
            if hr > 3:
                s[4] += 1

            # 下周是否进入主升或前置
            if idx + 1 < n and len(rows[idx + 1]) > 20:
                nxt = rows[idx + 1]
                nxt_ab = to_f(nxt[20])
                nxt_wxzb = to_f(nxt[15])
                nxt_hx = nxt[4]
                nxt_zp = nxt[6]
                nxt_wxza = to_f(nxt[14])
                nxt_prev_wxzb = wxzb  # 下周的前周WTZB = 本周WXZB
                if nxt_ab is not None and nxt_wxzb is not None:
                    nxt_main = (nxt_ab > 0) and (nxt_wxzb > 0)
                    nxt_qianzhi = (nxt_hx and nxt_hx[0] == 'r') and (nxt_prev_wxzb is not None and nxt_prev_wxzb > 0) and nxt_zp.startswith('升')
                    if nxt_main or nxt_qianzhi:
                        s[5] += 1
                        s[6] += 1
                    elif nxt_main:
                        s[5] += 1

    # 输出
    print(f'高波池文件: {n_files}')
    print()
    print('=== 舍弃区域合理性 + 主升条件固化验证 ===')
    print(f'{"区域":<28}{"n":>10}{"占比":>7}{"平均周涨":>9}{"正周涨%":>8}{"P(HR>3%)":>9}{"下周主升/前置%":>13}')
    print('-' * 90)
    order = ['主升(WXAB>0且WXZB>0)', '主升前置(己+前WTZB>0+升排)',
             '舍弃_忠(戊↘忠,鸡肋)', '舍弃_DXZC<0', '舍弃_其他(非主升/前置/忠/DXZC<0)']
    total = sum(stat[r][0] for r in stat)
    for r in order:
        s = stat[r]
        if s[0] == 0:
            continue
        n = s[0]
        print(f'{r:<28}{n:>10,}{n/total*100:>6.1f}%{s[1]/n:>8.3f}%{s[2]/n*100:>7.1f}%{s[4]/n*100:>8.1f}%{s[5]/n*100:>12.1f}%')

    # 汇总：主升+前置 vs 全部舍弃
    print()
    keep = stat['主升(WXAB>0且WXZB>0)'][0] + stat['主升前置(己+前WTZB>0+升排)'][0]
    discard = total - keep
    print(f'保留（主升+前置）: {keep:,} 周 = {keep/total*100:.1f}%')
    print(f'舍弃（其余）: {discard:,} 周 = {discard/total*100:.1f}%')

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['区域', 'n', '占比%', '平均周涨', '正周涨%', 'P(HR>3%)', '下周主升/前置%'])
        for r in order:
            s = stat[r]
            if s[0] == 0:
                continue
            n = s[0]
            w.writerow([r, n, f'{n/total*100:.1f}', f'{s[1]/n:.3f}', f'{s[2]/n*100:.1f}', f'{s[4]/n*100:.1f}', f'{s[5]/n*100:.1f}'])
        w.writerow([])
        w.writerow(['保留(主升+前置)', keep, f'{keep/total*100:.1f}'])
        w.writerow(['舍弃(其余)', discard, f'{discard/total*100:.1f}'])
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()
