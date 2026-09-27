# -*- coding: utf-8 -*-
"""
独立验证（2026-09-26）：用当前数据重算日类护型转移矩阵
=====================================================
目的：验证 MC3.3_C2 §2.3.1.1 的日类矩阵（2026-08-27 旧数据）是否仍可复现
关键：己→甲（分 DXZC）、甲→甲 稳定态
若当前日类数据与旧矩阵一致 → 护型规律稳定，周类与日类"高度一致"是真实规律
若不一致 → 旧矩阵已过时，"高度一致"可能是巧合

列映射（元数据_vba数据映射_日类.md）：
  [9]  DXAB 护型
  [13] 日ZA
  [14] 日ZC
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_日类转移矩阵_当前数据.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_dxab = 9
i_za = 13
i_zc = 14

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(dxab, za):
    if not dxab or len(dxab) < 1:
        return None
    c = dxab[0]
    if c == 'a':
        return '甲'
    if c == 'b':
        return '乙(ZA>0)' if za > 0 else '乙(ZA≤0)'
    if c == 'c':
        return '丙'
    if c == 'z':
        return '丁'
    if c == 'y':
        return '戊(ZA>0)' if za > 0 else '戊(ZA≤0)'
    if c == 'r':
        return '己'
    return None

ji_to_甲 = defaultdict(lambda: {'total': 0, 'to甲': 0})
甲_to_甲 = defaultdict(lambda: {'total': 0, 'to甲': 0})
hx_full_count = defaultdict(int)

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
            rows = []
            for row in r:
                if len(row) <= max(i_dxab, i_za, i_zc):
                    continue
                try:
                    dxab = row[i_dxab].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                except (ValueError, IndexError):
                    continue
                rows.append((dxab, za, zc))

            n = len(rows)
            for i in range(n):
                dxab, za, zc = rows[i]
                hx = parse_hx(dxab, za)
                if hx:
                    hx_full_count[hx] += 1
                key = 'DXZC>0' if zc > 0 else 'DXZC<=0'
                if i+1 < n:
                    next_hx = parse_hx(rows[i+1][0], rows[i+1][1])
                    if hx == '己' and next_hx == '甲':
                        ji_to_甲[key]['total'] += 1
                        ji_to_甲[key]['to甲'] += 1
                    elif hx == '己':
                        ji_to_甲[key]['total'] += 1
                    if hx == '甲' and next_hx == '甲':
                        甲_to_甲[key]['total'] += 1
                        甲_to_甲[key]['to甲'] += 1
                    elif hx == '甲':
                        甲_to_甲[key]['total'] += 1
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('日类护型转移（当前数据 2026-09-26 重算）')
out('=' * 100)
out('')
out('--- 己→甲（分 DXZC）---')
for key in ['DXZC>0', 'DXZC<=0']:
    s = ji_to_甲[key]
    if s['total'] > 0:
        out(f'{key}: 己总数 {s["total"]:,}，转甲 {s["to甲"]:,} = {s["to甲"]/s["total"]*100:.1f}%')

out('')
out('--- 甲→甲（分 DXZC）---')
for key in ['DXZC>0', 'DXZC<=0']:
    s = 甲_to_甲[key]
    if s['total'] > 0:
        out(f'{key}: 甲总数 {s["total"]:,}，维持甲 {s["to甲"]:,} = {s["to甲"]/s["total"]*100:.1f}%')

out('')
out('--- 各护型占比（完整拆分）---')
total_full = sum(hx_full_count.values())
for hx in ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']:
    out(f'{hx}: {hx_full_count.get(hx,0):,} = {hx_full_count.get(hx,0)/total_full*100:.1f}%')

out('')
out('=' * 100)
out('对比')
out('=' * 100)
out('')
out('日类旧矩阵（MC3.3_C2 §2.3.1.1，2026-08-27）：DXZC>0 己→甲 62.1%，DXZC≤0 己→甲 34.8%')
out('日类当前重算：DXZC>0 己→甲 ' + f'{ji_to_甲["DXZC>0"]["to甲"]/ji_to_甲["DXZC>0"]["total"]*100:.1f}%' + '，DXZC≤0 己→甲 ' + f'{ji_to_甲["DXZC<=0"]["to甲"]/ji_to_甲["DXZC<=0"]["total"]*100:.1f}%')
out('周类（2026-09-26）：WXZC>0 己→甲 60.4%，WXZC≤0 己→甲 33.2%')

OUTF.close()
print('Done')