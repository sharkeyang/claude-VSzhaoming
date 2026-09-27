# -*- coding: utf-8 -*-
"""
验证用户思想（2026-09-26）：
1. DXCD=上/忐 即主升？主战场（DXZE>0 + DXCD上/忐）是否必赢？
2. 主战场内存在大量"劫"（DXZA/DXZB/DXZC/DXZD 震荡）？占比多少？
3. 不能因震荡放弃主升——劫过去后是否值得再次介入？
4. 主升与震荡无清晰分界（DXCD 上/忐 与 中/下 之间是否连续过渡）？
5. 主战场内高抛低吸，依赖 DXZC、DXZB 两类入口操作是否可行？

列映射（元数据_vba数据映射_日类.md，勿信表头）：
  [8]  DXCD（上/中/下/忐/忠/忑）
  [13] 日ZA = DTZA
  [14] 日ZC = DTZC
  [15] 日ZE = DTZE
  [26] 次日高幅
  [62] DTZB（JZ vs JB 交叉天数）
  [63] DTZD（JZ vs JD 交叉天数）
  [64] DTAB（JA vs JB 交叉天数）
  [65] DTCD（JC vs JD 交叉天数）
"""
import csv, os, io
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_主战场震荡与必赢.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
import json
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

# 列索引
i_cd = 8
i_za = 13
i_zc = 14
i_ze = 15
i_nhr = 26
i_zb = 62
i_zd = 63
i_ab = 64
i_cd2 = 65

# 统计容器
# 主战场 = DXZE>0 + DXCD in (上,忐)
# 各条件组合的次日高幅
results = defaultdict(list)

files_done = 0
total_rows = 0

for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            for row in r:
                if len(row) <= max(i_cd, i_za, i_zc, i_ze, i_nhr, i_zb, i_zd, i_ab, i_cd2):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                    ab = float(row[i_ab])
                    cd2 = float(row[i_cd2])
                except (ValueError, IndexError):
                    continue
                total_rows += 1

                # 主战场判定
                in_main = (ze > 0) and (cd in ('上', '忐'))

                # 1. DXCD 各值次日高幅（验证 DXCD=上/忐 是否即主升）
                results['CD_' + cd].append(nhr)

                # 2. 主战场整体
                if in_main:
                    results['主战场(ZE>0+CD上忐)'].append(nhr)

                # 3. 主战场内各"劫"（震荡）的占比与次日高幅
                if in_main:
                    # 各交叉天数为负 = 跌破对应均线 = 劫
                    if za <= 0:
                        results['主战场_劫ZA<=0'].append(nhr)
                    if zb <= 0:
                        results['主战场_劫ZB<=0'].append(nhr)
                    if zc <= 0:
                        results['主战场_劫ZC<=0'].append(nhr)
                    if zd <= 0:
                        results['主战场_劫ZD<=0'].append(nhr)
                    if ab <= 0:
                        results['主战场_劫AB<=0'].append(nhr)
                    if cd2 <= 0:
                        results['主战场_劫CD<=0'].append(nhr)
                    # 无劫（所有交叉天数为正）
                    if za > 0 and zb > 0 and zc > 0 and zd > 0:
                        results['主战场_无劫(全正)'].append(nhr)

                # 4. 主战场内 DXZC 入口（ZC>0 站上DJC）vs ZC<=0
                if in_main:
                    if zc > 0:
                        results['主战场_ZC>0入口'].append(nhr)
                    else:
                        results['主战场_ZC<=0'].append(nhr)

                # 5. 主战场内 DXZB 入口（ZB>0 站上DJB）vs ZB<=0
                if in_main:
                    if zb > 0:
                        results['主战场_ZB>0入口'].append(nhr)
                    else:
                        results['主战场_ZB<=0'].append(nhr)

                # 6. 主战场内 DXZA 入口（ZA>0 站上DJA）
                if in_main:
                    if za > 0:
                        results['主战场_ZA>0入口'].append(nhr)

                # 7. 主战场内 DXZD 入口（ZD>0 站上DJD）
                if in_main:
                    if zd > 0:
                        results['主战场_ZD>0入口'].append(nhr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}, 总行数: {total_rows:,}')
out('')

def print_stats(label, vals):
    arr = np.array(vals)
    n = len(arr)
    if n < 100:
        out(f'| {label:<28s} | {n:>8,d} | (样本过少) |')
        return
    mean_hr = np.mean(arr)
    gt3 = (arr >= 3).sum() / n * 100
    gt5 = (arr >= 5).sum() / n * 100
    p25 = np.percentile(arr, 25)
    p75 = np.percentile(arr, 75)
    out(f'| {label:<28s} | {n:>8,d} | {mean_hr:>6.2f}% | {gt3:>5.1f}% | {gt5:>5.1f}% | {p25:>5.2f}% | {p75:>5.2f}% |')

out('=' * 100)
out('验证1：DXCD 各值次日高幅（DXCD=上/忐 是否即主升？）')
out('=' * 100)
out('')
out(f'| {"DXCD":<28s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} | {"P25":>5s} | {"P75":>5s} |')
out(f'|{"":->28s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|{"":->5s}:|{"":->5s}:|')
for cd in ['上', '忐', '中', '下', '忠', '忑']:
    if 'CD_' + cd in results:
        print_stats('DXCD=' + cd, results['CD_' + cd])

out('')
out('=' * 100)
out('验证2：主战场（ZE>0 + CD上/忐）是否必赢？')
out('=' * 100)
out('')
out(f'| {"条件":<28s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} | {"P25":>5s} | {"P75":>5s} |')
out(f'|{"":->28s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|{"":->5s}:|{"":->5s}:|')
for label in ['主战场(ZE>0+CD上忐)', '主战场_无劫(全正)', '主战场_劫ZA<=0', '主战场_劫ZB<=0',
              '主战场_劫ZC<=0', '主战场_劫ZD<=0', '主战场_劫AB<=0', '主战场_劫CD<=0']:
    if label in results:
        print_stats(label, results[label])

out('')
out('=' * 100)
out('验证3：主战场内各"劫"占比（震荡比例）')
out('=' * 100)
out('')
main_n = len(results.get('主战场(ZE>0+CD上忐)', []))
if main_n > 0:
    for label in ['主战场_劫ZA<=0', '主战场_劫ZB<=0', '主战场_劫ZC<=0', '主战场_劫ZD<=0',
                  '主战场_劫AB<=0', '主战场_劫CD<=0', '主战场_无劫(全正)']:
        if label in results:
            n = len(results[label])
            out(f'{label}: {n:,} 行, 占主战场 {n/main_n*100:.1f}%')

out('')
out('=' * 100)
out('验证4：主战场内 DXZC / DXZB 两类入口（高抛低吸可行性）')
out('=' * 100)
out('')
out(f'| {"条件":<28s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} |')
out(f'|{"":->28s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|')
for label in ['主战场_ZC>0入口', '主战场_ZC<=0', '主战场_ZB>0入口', '主战场_ZB<=0',
              '主战场_ZA>0入口', '主战场_ZD>0入口']:
    if label in results:
        print_stats(label, results[label])

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')

# 主战场 vs 基线（全样本）
if '主战场(ZE>0+CD上忐)' in results:
    a = np.array(results['主战场(ZE>0+CD上忐)'])
    out(f'主战场样本: {len(a):,} 行, 占全样本 {len(a)/total_rows*100:.1f}%')
    out(f'  均次日高: {np.mean(a):.2f}%, 高≥3%: {(a>=3).sum()/len(a)*100:.1f}%')

# 主战场内 无劫 vs 有劫
if '主战场_无劫(全正)' in results and '主战场_劫ZA<=0' in results:
    a = np.array(results['主战场_无劫(全正)'])
    b = np.array(results['主战场_劫ZA<=0'])
    out(f'')
    out(f'主战场内 无劫(全正) vs 劫ZA<=0：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

# 主战场内 ZC>0 vs ZC<=0
if '主战场_ZC>0入口' in results and '主战场_ZC<=0' in results:
    a = np.array(results['主战场_ZC>0入口'])
    b = np.array(results['主战场_ZC<=0'])
    out(f'')
    out(f'主战场内 ZC>0入口 vs ZC<=0：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

# 主战场内 ZB>0 vs ZB<=0
if '主战场_ZB>0入口' in results and '主战场_ZB<=0' in results:
    a = np.array(results['主战场_ZB>0入口'])
    b = np.array(results['主战场_ZB<=0'])
    out(f'')
    out(f'主战场内 ZB>0入口 vs ZB<=0：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

OUTF.close()
print('Done')
