# -*- coding: utf-8 -*-
"""
持续周期比较（2026-09-26）：日类 vs 周类 各护型持续时长
=====================================================
用各自周期计数（日类=天，周类=周），不把周转日。
统计各护型的平均/中位/最大持续时长。

列映射：
  日类：DXAB[9]、日ZA[13]、日ZC[14]
  周类：WXAB[4]、WXZA[14]、WXZC[16]
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_日周持续周期.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(ab, za):
    if not ab or len(ab) < 1:
        return None
    c = ab[0]
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

def compute_durations(dirname, prefix, i_ab, i_za, i_zc):
    """统计各护型持续时长（连续相同护型的行数）"""
    durations = defaultdict(list)
    files_done = 0
    for fname in os.listdir(dirname):
        p = os.path.join(dirname, fname)
        try:
            cidl = fname.replace(prefix, '').replace('.csv', '')
            board = board_map.get(cidl, '')
            if board not in 高波池板块:
                continue
            with open(p, 'r', encoding='gbk', errors='replace') as f:
                r = csv.reader(f)
                header = next(r)
                rows = []
                for row in r:
                    if len(row) <= max(i_ab, i_za, i_zc):
                        continue
                    try:
                        ab = row[i_ab].strip()
                        za = float(row[i_za])
                        zc = float(row[i_zc])
                    except (ValueError, IndexError):
                        continue
                    rows.append((ab, za, zc))
                # 识别连续相同护型的段
                n = len(rows)
                i = 0
                while i < n:
                    hx = parse_hx(rows[i][0], rows[i][1])
                    if hx is None:
                        i += 1
                        continue
                    j = i
                    while j < n:
                        jhx = parse_hx(rows[j][0], rows[j][1])
                        if jhx != hx:
                            break
                        j += 1
                    durations[hx].append(j - i)
                    i = j
        except Exception:
            pass
        files_done += 1
    return durations, files_done

# 日类
日dur, 日files = compute_durations('昭明算展/谕组日', '谕组日_', 9, 13, 14)
# 周类
周dur, 周files = compute_durations('昭明算展/谕组周', '谕组周_', 4, 14, 16)

out(f'日类文件数: {日files}, 周类文件数: {周files}')
out('')
out('=' * 100)
out('各护型持续时长：日类（天） vs 周类（周）')
out('=' * 100)
out('')
out('说明：日类持续时长单位=天，周类持续时长单位=周。用各自周期计数，不把周转日。')
out('')
out(f'| {"护型":<12s} | {"日类段数":>10s} | {"日均(天)":>8s} | {"日中位":>7s} | {"周类段数":>10s} | {"周均(周)":>8s} | {"周中位":>7s} | {"周/日均值比":>10s} |')
out(f'|{"":->12s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|{"":->10s}:|{"":->8s}:|{"":->7s}:|{"":->10s}:|')
for hx in ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']:
    d = np.array(日dur.get(hx, []))
    w = np.array(周dur.get(hx, []))
    if len(d) == 0 or len(w) == 0:
        continue
    d_mean = np.mean(d)
    w_mean = np.mean(w)
    ratio = w_mean / d_mean if d_mean > 0 else 0
    out(f'| {hx:<12s} | {len(d):>10,d} | {d_mean:>7.1f} | {np.median(d):>6.0f} | {len(w):>10,d} | {w_mean:>7.2f} | {np.median(w):>6.0f} | {ratio:>9.2f} |')

out('')
out('=' * 100)
out('解读')
out('=' * 100)
out('')
out('周/日均值比 ≈ 5 说明周线护型持续 ≈ 日线护型持续 × 5（1周=5日，等倍数重复）')
out('周/日均值比 < 5 说明周线护型持续相对日线更短（周线更易切换）')
out('周/日均值比 > 5 说明周线护型持续相对日线更长（周线更稳定）')
out('')

OUTF.close()
print('Done')