# -*- coding: utf-8 -*-
"""
补充验证（2026-09-26）：
A. 主战场内 ZC / ZD 是否恒为正？（若恒正则 DXZC/DXZD 不是有效入口）
B. DXCD=上 vs 忐 差异是否显著？（"DXCD=上/忐即主升"是否成立）
C. 劫过去后再次介入：震荡后恢复上涨（ZA由负转正当天）的次日高幅
D. 主战场内"高抛低吸"：DXZA/DXZB 由正转负（劫开始）vs 由负转正（劫结束）的次日高幅
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_主战场震荡与必赢_补充.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_za = 13
i_zc = 14
i_ze = 15
i_nhr = 26
i_zb = 62
i_zd = 63

results = defaultdict(list)
files_done = 0

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
            prev = None  # (za, zb, zc, zd, ze, cd, nhr)
            for row in r:
                if len(row) <= max(i_cd, i_za, i_zc, i_ze, i_nhr, i_zb, i_zd):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                except (ValueError, IndexError):
                    continue
                cur = (za, zb, zc, zd, ze, cd, nhr)
                in_main = (ze > 0) and (cd in ('上', '忐'))

                # A. 主战场内 ZC/ZD 分布
                if in_main:
                    results['主战场_ZC>0'].append(1 if zc > 0 else 0)
                    results['主战场_ZD>0'].append(1 if zd > 0 else 0)
                    results['主战场_ZC值'].append(zc)
                    results['主战场_ZD值'].append(zd)

                # B. DXCD=上 vs 忐
                if ze > 0 and cd == '上':
                    results['CD上_ZE>0'].append(nhr)
                if ze > 0 and cd == '忐':
                    results['CD忐_ZE>0'].append(nhr)

                # C. 劫过去后再次介入：ZA 由负转正当天（前一日 ZA<=0，今日 ZA>0）
                if prev is not None:
                    pza, pzb, pzc, pzd, pze, pcd, pnhr = prev
                    # 主战场内，ZA 由负转正（劫结束）
                    if in_main and pza <= 0 and za > 0:
                        results['劫结束_ZA转正当天'].append(nhr)
                    # 主战场内，ZB 由负转正
                    if in_main and pzb <= 0 and zb > 0:
                        results['劫结束_ZB转正当天'].append(nhr)
                    # 主战场内，ZA 由正转负（劫开始）
                    if in_main and pza > 0 and za <= 0:
                        results['劫开始_ZA转负当天'].append(nhr)
                    # 主战场内，ZB 由正转负
                    if in_main and pzb > 0 and zb <= 0:
                        results['劫开始_ZB转负当天'].append(nhr)

                prev = cur
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')

def print_stats(label, vals):
    arr = np.array(vals)
    n = len(arr)
    if n < 100:
        out(f'| {label:<30s} | {n:>8,d} | (样本过少) |')
        return
    mean_hr = np.mean(arr)
    gt3 = (arr >= 3).sum() / n * 100
    gt5 = (arr >= 5).sum() / n * 100
    out(f'| {label:<30s} | {n:>8,d} | {mean_hr:>6.2f}% | {gt3:>5.1f}% | {gt5:>5.1f}% |')

out('=' * 100)
out('A. 主战场内 ZC / ZD 是否恒为正？')
out('=' * 100)
out('')
zc_pos = np.array(results['主战场_ZC>0'])
zd_pos = np.array(results['主战场_ZD>0'])
out(f'主战场内 ZC>0 比例: {zc_pos.mean()*100:.1f}%')
out(f'主战场内 ZD>0 比例: {zd_pos.mean()*100:.1f}%')
zc_vals = np.array(results['主战场_ZC值'])
zd_vals = np.array(results['主战场_ZD值'])
out(f'主战场内 ZC 值分布: min={zc_vals.min():.0f}, P25={np.percentile(zc_vals,25):.0f}, 中位={np.median(zc_vals):.0f}, P75={np.percentile(zc_vals,75):.0f}, max={zc_vals.max():.0f}')
out(f'主战场内 ZD 值分布: min={zd_vals.min():.0f}, P25={np.percentile(zd_vals,25):.0f}, 中位={np.median(zd_vals):.0f}, P75={np.percentile(zd_vals,75):.0f}, max={zd_vals.max():.0f}')

out('')
out('=' * 100)
out('B. DXCD=上 vs 忐（ZE>0 口径）')
out('=' * 100)
out('')
out(f'| {"条件":<30s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|')
print_stats('CD上_ZE>0', results['CD上_ZE>0'])
print_stats('CD忐_ZE>0', results['CD忐_ZE>0'])

out('')
out('=' * 100)
out('C. 劫过去后再次介入（主战场内，转正当天次日高幅）')
out('=' * 100)
out('')
out(f'| {"条件":<30s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|')
for label in ['劫结束_ZA转正当天', '劫结束_ZB转正当天', '劫开始_ZA转负当天', '劫开始_ZB转负当天']:
    if label in results:
        print_stats(label, results[label])

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')
if '劫结束_ZA转正当天' in results and '劫开始_ZA转负当天' in results:
    a = np.array(results['劫结束_ZA转正当天'])
    b = np.array(results['劫开始_ZA转负当天'])
    out(f'劫结束(ZA转正) vs 劫开始(ZA转负)：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

if '劫结束_ZB转正当天' in results and '劫开始_ZB转负当天' in results:
    a = np.array(results['劫结束_ZB转正当天'])
    b = np.array(results['劫开始_ZB转负当天'])
    out(f'')
    out(f'劫结束(ZB转正) vs 劫开始(ZB转负)：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

OUTF.close()
print('Done')
