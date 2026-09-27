# -*- coding: utf-8 -*-
"""
修正验证（2026-09-26）：用 DTCD（列65）判断"DXCD 由正转负"，不模拟
===================================================================
用户"修复"原则（正确表述）：
- DXCD 由正转负的本质 = DTCD（JC vs JD，EMA26 vs EMA60）由正转负
  - DTCD>0 = JC>JD = 多头排列 = DXCD 上/中/下
  - DTCD≤0 = JC≤JD = 空头排列 = DXCD 忐/忠/忑
- 劫 = 某指标（DXZA/DXZB/DXZC/DXZD/DXAB）由正转负（在 DTCD>0 区域内）
- 修复 = 在 DTCD 由正转负（列65）之前，该指标重新转正
- 转负 = 未修复，DTCD 直接由正转负（列65）

关键：直接用 DTCD 列65 判断"DXCD 由正转负"，不用 DXCD 字符，不用 ZC/ZD 模拟。
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_DXZC_DXZD震荡_DTCD.txt', 'w', encoding='utf-8')
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
i_zb = 62
i_zd = 63
i_ab = 64
i_dtcd = 65   # DTCD（JC vs JD 交叉天数）

# stats[指标] = {total, cd_neg, repaired, end}
stats = defaultdict(lambda: {'total': 0, 'cd_neg': 0, 'repaired': 0, 'end': 0})

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
                if len(row) <= max(i_cd, i_za, i_zc, i_ze, i_zb, i_zd, i_ab, i_dtcd):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                    ab = float(row[i_ab])
                    dtcd = float(row[i_dtcd])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, za, zc, ze, zb, zd, ab, dtcd))

            n = len(rows)
            for i in range(n):
                cd, za, zc, ze, zb, zd, ab, dtcd = rows[i]
                # 只在 DTCD>0（多头排列，DXCD 上/中/下）区域内检测劫
                if dtcd <= 0:
                    continue
                for kname, kcol in [('ZC', 2), ('ZD', 5), ('ZA', 1), ('ZB', 4), ('AB', 6)]:
                    val = rows[i][kcol]
                    if i > 0:
                        prev_val = rows[i-1][kcol]
                        if prev_val > 0 and val <= 0:
                            # 劫出现，扫描后续
                            stats[kname]['total'] += 1
                            outcome = 'end'
                            for j in range(i+1, n):
                                jcd, jza, jzc, jze, jzb, jzd, jab, jdtcd = rows[j]
                                jval = rows[j][kcol]
                                # 先检查修复（该指标重新转正）
                                if jval > 0:
                                    outcome = 'repaired'
                                    break
                                # 再检查 DTCD 由正转负（列65 直接判断）
                                if jdtcd <= 0:
                                    outcome = 'cd_neg'
                                    break
                            stats[kname][outcome] += 1
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('DTCD>0（多头排列）区域内，各指标由正转负后，DTCD 由正转负（列65 直接判断）的概率')
out('=' * 100)
out('')
out('DXCD 由正转负 = DTCD（列65）由正转负（JC>JD → JC≤JD）')
out('')
out(f'| {"指标":<6s} | {"出现次数":>10s} | {"DTCD转负":>10s} | {"转负率":>8s} | {"修复":>8s} | {"修复率":>8s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->10s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for key in ['ZC', 'ZD', 'ZA', 'ZB', 'AB']:
    s = stats[key]
    total = s['total']
    if total == 0:
        continue
    out(f'| {key:<6s} | {total:>10,d} | {s["cd_neg"]:>10,d} | {s["cd_neg"]/total*100:>7.1f}% | {s["repaired"]:>8,d} | {s["repaired"]/total*100:>7.1f}% |')

out('')
out('=' * 100)
out('解读')
out('=' * 100)
out('')
for key in ['ZC', 'ZD', 'ZA', 'ZB', 'AB']:
    s = stats[key]
    total = s['total']
    if total == 0:
        continue
    out(f'{key}劫：出现 {total:,} 次')
    out(f'  → DTCD由正转负（列65直接判断）: {s["cd_neg"]:,} 次 = {s["cd_neg"]/total*100:.1f}%')
    out(f'  → 修复成功（转正，DTCD保住）: {s["repaired"]:,} 次 = {s["repaired"]/total*100:.1f}%')
    out(f'  → 文件结束未定: {s["end"]:,} 次 = {s["end"]/total*100:.1f}%')
    out('')

OUTF.close()
print('Done')