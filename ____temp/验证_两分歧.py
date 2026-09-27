# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：两个分歧的数据确认
=====================================
分歧1：首下破 DJB（甲乙己→丙丁戊）应不应退出？
  - §6.1.1.1/§6.12.1：下破DJB退出
  - §6.8.7：首次下跌DJB 64.9%反弹，不当退出
  需要：首下破DJB后的短期（次日/3日/5日累计）vs 长期（10/20日恢复）走势

分歧2：DJA 之上连阴/阴阳阴 是否应退出？
  - §6.8.7：一般不退出
  需要：DJA 之上（甲乙己+ZA>0）连阴/阴阳阴后的次日/3日/5日走势

列映射：
  [8]  DXCD
  [9]  DXAB 护型
  [10] 柱排
  [13] 日ZA
  [14] 日ZC
  [26] 次日高幅
  [30] 上符串
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_两分歧.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_dxab = 9
i_zp = 10
i_za = 13
i_zc = 14
i_nhr = 26
i_sfs = 30

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

def is_甲乙己(hx):
    return hx in ('甲', '乙(ZA>0)', '己')

def is_丙丁戊(hx):
    return hx in ('丙', '丁', '戊(ZA≤0)')

def is_连阴(zp):
    return zp and zp.startswith('跌')

def is_阴阳阴(zp):
    return zp and '人' in zp

def is_离顶(sfs):
    return sfs and not sfs.rstrip().endswith('A')

# 统计：每个条件 → 后续走势
stats = defaultdict(lambda: {'nhr': [], 'cum3': [], 'cum5': [], 'rec10': [], 'rec20': []})

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
                if len(row) <= max(i_cd, i_dxab, i_zp, i_za, i_zc, i_nhr, i_sfs):
                    continue
                try:
                    cd = row[i_cd].strip()
                    dxab = row[i_dxab].strip()
                    zp = row[i_zp].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    nhr = float(row[i_nhr])
                    sfs = row[i_sfs].strip()
                except (ValueError, IndexError):
                    continue
                rows.append((cd, dxab, zp, za, zc, nhr, sfs))

            n = len(rows)
            for i in range(1, n):
                cd, dxab, zp, za, zc, nhr, sfs = rows[i]
                hx = parse_hx(dxab, za)
                prev = rows[i-1]
                prev_hx = parse_hx(prev[1], prev[3])
                prev_za = prev[3]
                prev_zp = prev[2]
                prev_sfs = prev[6]

                # 分歧1：首下破 DJB（前一日甲乙己+ZA>0，今日丙丁戊+ZA<0）
                if is_甲乙己(prev_hx) and is_丙丁戊(hx):
                    key = '首下破DJB(甲乙己→丙丁戊)'
                    stats[key]['nhr'].append(nhr)
                    # 3日/5日累计高幅（未来N日最大高幅，近似累计）
                    cum3 = max((rows[j][5] for j in range(i+1, min(i+4, n))), default=0)
                    cum5 = max((rows[j][5] for j in range(i+1, min(i+6, n))), default=0)
                    stats[key]['cum3'].append(cum3)
                    stats[key]['cum5'].append(cum5)
                    # 10/20日恢复（重新站上DJB=重新甲乙己）
                    for horizon, hkey in [(10, 'rec10'), (20, 'rec20')]:
                        rec = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if is_甲乙己(parse_hx(rows[j][1], rows[j][3])):
                                rec = True
                                break
                        stats[key][hkey].append(1 if rec else 0)

                # 分歧2：DJA 之上（甲乙己+ZA>0）连阴/阴阳阴
                if is_甲乙己(hx) and za > 0:
                    if is_连阴(zp):
                        key = 'DJA之上连阴'
                        stats[key]['nhr'].append(nhr)
                        cum3 = max((rows[j][5] for j in range(i+1, min(i+4, n))), default=0)
                        cum5 = max((rows[j][5] for j in range(i+1, min(i+6, n))), default=0)
                        stats[key]['cum3'].append(cum3)
                        stats[key]['cum5'].append(cum5)
                    if is_阴阳阴(zp):
                        key = 'DJA之上阴阳阴'
                        stats[key]['nhr'].append(nhr)
                        cum3 = max((rows[j][5] for j in range(i+1, min(i+4, n))), default=0)
                        cum5 = max((rows[j][5] for j in range(i+1, min(i+6, n))), default=0)
                        stats[key]['cum3'].append(cum3)
                        stats[key]['cum5'].append(cum5)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('分歧1：首下破 DJB 应不应退出？')
out('=' * 100)
out('')
for key in ['首下破DJB(甲乙己→丙丁戊)']:
    s = stats[key]
    if not s['nhr']:
        continue
    nhr = np.array(s['nhr'])
    cum3 = np.array(s['cum3'])
    cum5 = np.array(s['cum5'])
    rec10 = np.mean(s['rec10'])*100
    rec20 = np.mean(s['rec20'])*100
    out(f'{key}: 样本 {len(nhr):,}')
    out(f'  次日高≥3%: {(nhr>=3).sum()/len(nhr)*100:.1f}%')
    out(f'  3日内最大高≥3%: {(cum3>=3).sum()/len(cum3)*100:.1f}%')
    out(f'  5日内最大高≥3%: {(cum5>=3).sum()/len(cum5)*100:.1f}%')
    out(f'  10日恢复(重新甲乙己): {rec10:.1f}%')
    out(f'  20日恢复(重新甲乙己): {rec20:.1f}%')

out('')
out('=' * 100)
out('分歧2：DJA 之上连阴/阴阳阴 是否应退出？')
out('=' * 100)
out('')
for key in ['DJA之上连阴', 'DJA之上阴阳阴']:
    s = stats[key]
    if not s['nhr']:
        continue
    nhr = np.array(s['nhr'])
    cum3 = np.array(s['cum3'])
    cum5 = np.array(s['cum5'])
    out(f'{key}: 样本 {len(nhr):,}')
    out(f'  次日高≥3%: {(nhr>=3).sum()/len(nhr)*100:.1f}%')
    out(f'  3日内最大高≥3%: {(cum3>=3).sum()/len(cum3)*100:.1f}%')
    out(f'  5日内最大高≥3%: {(cum5>=3).sum()/len(cum5)*100:.1f}%')

out('')
out('=' * 100)
out('对比基线（全样本 23.6%）')
out('=' * 100)
out('')

OUTF.close()
print('Done')