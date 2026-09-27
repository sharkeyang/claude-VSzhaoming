# -*- coding: utf-8 -*-
"""
独立验证（2026-09-26）：周类护型转移矩阵正确性
=============================================
用不同的实现方式重新计算，交叉核对关键数字：
1. 己→甲 概率（分 WXZC）
2. 甲→甲 稳定态
3. 各护型占比
4. 与日类矩阵对比

关键：检查护型解析、转移方向、WXZC分档是否正确
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_周类转移矩阵_独立核对.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_wxab = 4
i_wxza = 14
i_wxzc = 16

# 护型映射（第1字符）
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(wxab, wxza):
    """解析护型，乙/戊按 WXZA 符号拆分"""
    if not wxab or len(wxab) < 1:
        return None
    c = wxab[0]
    if c == 'a':
        return '甲'
    if c == 'b':
        return '乙(ZA>0)' if wxza > 0 else '乙(ZA≤0)'
    if c == 'c':
        return '丙'
    if c == 'z':
        return '丁'
    if c == 'y':
        return '戊(ZA>0)' if wxza > 0 else '戊(ZA≤0)'
    if c == 'r':
        return '己'
    return None

# 统计
# 1. 己→甲（分WXZC），用两种方式：只看第1字符（不拆乙戊）vs 完整拆分
ji_to_甲 = defaultdict(lambda: {'total': 0, 'to甲': 0})
# 2. 甲→甲
甲_to_甲 = defaultdict(lambda: {'total': 0, 'to甲': 0})
# 3. 各护型占比（第1字符）
hx1_count = defaultdict(int)
# 4. 完整护型占比
hx_full_count = defaultdict(int)

files_done = 0
for fname in os.listdir('昭明算展/谕组周'):
    p = os.path.join('昭明算展/谕组周', fname)
    try:
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            rows = []
            for row in r:
                if len(row) <= max(i_wxab, i_wxza, i_wxzc):
                    continue
                try:
                    wxab = row[i_wxab].strip()
                    wxza = float(row[i_wxza])
                    wxzc = float(row[i_wxzc])
                except (ValueError, IndexError):
                    continue
                rows.append((wxab, wxza, wxzc))

            n = len(rows)
            for i in range(n):
                wxab, wxza, wxzc = rows[i]
                hx = parse_hx(wxab, wxza)
                hx1 = HX_MAP.get(wxab[0] if wxab else '', None)
                if hx1:
                    hx1_count[hx1] += 1
                if hx:
                    hx_full_count[hx] += 1
                key = 'WXZC>0' if wxzc > 0 else 'WXZC<=0'
                # 转移
                if i+1 < n:
                    next_hx = parse_hx(rows[i+1][0], rows[i+1][1])
                    next_hx1 = HX_MAP.get(rows[i+1][0][0] if rows[i+1][0] else '', None)
                    # 己→甲（完整拆分）
                    if hx == '己' and next_hx == '甲':
                        ji_to_甲[key]['total'] += 1
                        ji_to_甲[key]['to甲'] += 1
                    elif hx == '己':
                        ji_to_甲[key]['total'] += 1
                    # 甲→甲
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
out('独立核对：周类护型转移关键数字')
out('=' * 100)
out('')
out('--- 己→甲（分 WXZC）---')
for key in ['WXZC>0', 'WXZC<=0']:
    s = ji_to_甲[key]
    if s['total'] > 0:
        out(f'{key}: 己总数 {s["total"]:,}，转甲 {s["to甲"]:,} = {s["to甲"]/s["total"]*100:.1f}%')

out('')
out('--- 甲→甲（分 WXZC）---')
for key in ['WXZC>0', 'WXZC<=0']:
    s = 甲_to_甲[key]
    if s['total'] > 0:
        out(f'{key}: 甲总数 {s["total"]:,}，维持甲 {s["to甲"]:,} = {s["to甲"]/s["total"]*100:.1f}%')

out('')
out('--- 各护型占比（第1字符，不拆乙戊）---')
total1 = sum(hx1_count.values())
for hx in ['甲', '乙', '丙', '丁', '戊', '己']:
    out(f'{hx}: {hx1_count.get(hx,0):,} = {hx1_count.get(hx,0)/total1*100:.1f}%')

out('')
out('--- 各护型占比（完整拆分）---')
total_full = sum(hx_full_count.values())
for hx in ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']:
    out(f'{hx}: {hx_full_count.get(hx,0):,} = {hx_full_count.get(hx,0)/total_full*100:.1f}%')

out('')
out('=' * 100)
out('与日类矩阵对比（己→甲）')
out('=' * 100)
out('')
out('日类（MC3.3_C2 §2.3.1.1）：DXZC>0 己→甲 62.1%，DXZC≤0 己→甲 34.8%')
out('周类（本次独立核对）：WXZC>0 己→甲 ' + f'{ji_to_甲["WXZC>0"]["to甲"]/ji_to_甲["WXZC>0"]["total"]*100:.1f}%' + '，WXZC<=0 己→甲 ' + f'{ji_to_甲["WXZC<=0"]["to甲"]/ji_to_甲["WXZC<=0"]["total"]*100:.1f}%')

OUTF.close()
print('Done')