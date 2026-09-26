# -*- coding: utf-8 -*-
"""
验证 DXZC>0 且 DTZD>0 是否为必赢策略
=====================================
- DXZC>0 = 日ZC>0（站上DJC，EMA26）
- DTZD>0 = 收盘价在EMA60之上（站上DJD）
- 必赢判定：次日高幅≥3% 且 均次日高幅
- 对比：DXZC>0 单独 vs DXZC>0+DTZD>0 vs DXZE>0+DXZC>0（原V1必赢）
- 高波池 Qic+Qim+Qit
"""
import csv, os, json, io
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_DXZC_DTZD_必赢验证.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

# 统计：各条件组合的次日高幅分布
# key = 条件标签, value = list of 次日高幅
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
            # 固定列索引（对照 _产出物\_工具\元数据_vba数据映射_日类.md，勿信表头名）
            idx_close = 1       # 收
            idx_zc = 14         # 日ZC
            idx_ze = 15         # 日ZE
            idx_next_hr = 26    # 次日高幅
            idx_dtzd = 63       # DTZD（JZ vs JD交叉天数，2026-09-24新增导出）

            prices = []
            rows_data = []
            for row in r:
                if len(row) <= max(idx_close, idx_zc, idx_ze, idx_next_hr, idx_dtzd):
                    continue
                try:
                    close = float(row[idx_close])
                    zc = float(row[idx_zc])
                    ze = float(row[idx_ze])
                    next_hr = float(row[idx_next_hr])
                    dtzd = float(row[idx_dtzd])
                except (ValueError, IndexError):
                    continue
                prices.append(close)
                rows_data.append((zc, ze, next_hr, dtzd))

            if len(prices) < 1:
                continue

            for i in range(len(prices)):
                zc, ze, next_hr, dtzd = rows_data[i]

                # 记录各条件组合
                cond_zc = zc > 0
                cond_ze = ze > 0
                cond_dtzd = dtzd > 0

                # DXZC>0 单独
                if cond_zc:
                    results['ZC>0'].append(next_hr)

                # DXZC>0 + DTZD>0
                if cond_zc and cond_dtzd:
                    results['ZC>0+DTZD>0'].append(next_hr)

                # DXZE>0 + DXZC>0（原V1必赢）
                if cond_ze and cond_zc:
                    results['ZE>0+ZC>0(V1必赢)'].append(next_hr)

                # DXZC>0 + DTZD<=0（对照）
                if cond_zc and not cond_dtzd:
                    results['ZC>0+DTZD<=0'].append(next_hr)

                # DTZD>0 单独
                if cond_dtzd:
                    results['DTZD>0'].append(next_hr)

                # 全不满足（对照）
                if not cond_zc and not cond_ze and not cond_dtzd:
                    results['全不满足'].append(next_hr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')

def print_stats(label, vals):
    arr = np.array(vals)
    n = len(arr)
    if n < 100:
        return
    mean_hr = np.mean(arr)
    gt3 = (arr >= 3).sum() / n * 100
    gt5 = (arr >= 5).sum() / n * 100
    gt7 = (arr >= 7).sum() / n * 100
    p25 = np.percentile(arr, 25)
    p75 = np.percentile(arr, 75)
    out(f'| {label:<30s} | {n:>8,d} | {mean_hr:>6.2f}% | {gt3:>5.1f}% | {gt5:>5.1f}% | {gt7:>5.1f}% | {p25:>5.2f}% | {p75:>5.2f}% |')

out('=' * 100)
out('DXZC>0 + DTZD>0 必赢策略验证（高波池）')
out('=' * 100)
out('')
out(f'| {"条件":<30s} | {"样本":>8s} | {"均次日高":>7s} | {"高≥3%":>6s} | {"高≥5%":>6s} | {"高≥7%":>6s} | {"P25":>5s} | {"P75":>5s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->7s}:|{"":->6s}:|{"":->6s}:|{"":->6s}:|{"":->5s}:|{"":->5s}:|')

for label in ['ZC>0', 'DTZD>0', 'ZC>0+DTZD>0', 'ZC>0+DTZD<=0', 'ZE>0+ZC>0(V1必赢)', '全不满足']:
    if label in results:
        print_stats(label, results[label])

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')

# 对比：ZC>0+DTZD>0 vs ZC>0 单独
if 'ZC>0+DTZD>0' in results and 'ZC>0' in results:
    a = np.array(results['ZC>0+DTZD>0'])
    b = np.array(results['ZC>0'])
    out(f'ZC>0+DTZD>0  vs  ZC>0 单独：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')
    out(f'  样本比: {len(a)} vs {len(b)} ({len(a)/len(b)*100:.1f}%)')

# 对比：ZC>0+DTZD>0 vs ZE>0+ZC>0（V1必赢）
if 'ZC>0+DTZD>0' in results and 'ZE>0+ZC>0(V1必赢)' in results:
    a = np.array(results['ZC>0+DTZD>0'])
    c = np.array(results['ZE>0+ZC>0(V1必赢)'])
    out(f'')
    out(f'ZC>0+DTZD>0  vs  ZE>0+ZC>0(V1必赢)：')
    out(f'  均次日高差: {np.mean(a)-np.mean(c):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (c>=3).sum()/len(c)*100:+.1f}pp')
    out(f'  样本比: {len(a)} vs {len(c)} ({len(a)/len(c)*100:.1f}%)')

# 对比：ZC>0+DTZD>0 vs ZC>0+DTZD<=0
if 'ZC>0+DTZD>0' in results and 'ZC>0+DTZD<=0' in results:
    a = np.array(results['ZC>0+DTZD>0'])
    d = np.array(results['ZC>0+DTZD<=0'])
    out(f'')
    out(f'ZC>0+DTZD>0  vs  ZC>0+DTZD<=0（DTZD的增量贡献）：')
    out(f'  均次日高差: {np.mean(a)-np.mean(d):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (d>=3).sum()/len(d)*100:+.1f}pp')

OUTF.close()
print('Done')