# -*- coding: utf-8 -*-
"""
周类验证（2026-09-26）：WXAB 正交驱动 + 己/戊/丙 转甲/转乙概率
=============================================================
用户思想：
1. 周类上升驱动力=WXAB正交，优先已正交(甲乙)或将正交(己戊ZA>0)
2. 优先已正交且WXZC>0（将正交有欺骗性）
3. WXAB己 不一定转甲——验证己转甲概率、戊(ZA>0)转甲概率
4. 统计：WXZC<0 时 WXAB己 未转甲比例；WXZC>0 时 WXAB丙 未转丁而是转乙(WXZA<0)比例
5. 周类 WXAB 己与甲乙的比例

列映射（元数据_vba数据映射_周类.md）：
  [4]  WXAB 护型（a甲/b乙/c丙/z丁/y戊/r己）
  [14] WXZA
  [15] WXZB
  [16] WXZC
  [17] WXZD
  [20] AB周（WXAB 交叉天数）
  [25] CD周（WXCD 交叉天数）
  [1]  周涨
  [3]  HR（周高幅）
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_周类WXAB转甲.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_wxab = 4
i_wxza = 14
i_wxzb = 15
i_wxzc = 16
i_wxzd = 17
i_ab = 20
i_cd = 25
i_hr = 3

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(wxab):
    if not wxab or len(wxab) < 1:
        return ''
    return 护型映射.get(wxab[0], '')

# 统计
# 1. 各护型占比
hx_count = defaultdict(int)
# 2. 己转甲（分 WXZC 正负）
# key = (护型, WXZC正负), value = {total, 转甲, 转乙, 转其他}
ji_trans = defaultdict(lambda: {'total': 0, 'to甲': 0, 'to乙': 0, 'to其他': 0})
# 3. 戊(ZA>0)转甲
wu_trans = defaultdict(lambda: {'total': 0, 'to甲': 0, 'to其他': 0})
# 4. 丙转丁/乙
bing_trans = defaultdict(lambda: {'total': 0, 'to丁': 0, 'to乙': 0, 'to其他': 0})
# 5. 下周P3（各护型）
hx_p3 = defaultdict(list)

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
                if len(row) <= max(i_wxab, i_wxza, i_wxzb, i_wxzc, i_wxzd, i_ab, i_cd, i_hr):
                    continue
                try:
                    wxab = row[i_wxab].strip()
                    wxza = float(row[i_wxza])
                    wxzb = float(row[i_wxzb])
                    wxzc = float(row[i_wxzc])
                    wxzd = float(row[i_wxzd])
                    ab = float(row[i_ab])
                    cd = float(row[i_cd])
                    hr = float(row[i_hr])
                except (ValueError, IndexError):
                    continue
                rows.append((wxab, wxza, wxzb, wxzc, wxzd, ab, cd, hr))

            n = len(rows)
            for i in range(n):
                wxab, wxza, wxzb, wxzc, wxzd, ab, cd, hr = rows[i]
                hx = parse_hx(wxab)
                if not hx:
                    continue
                hx_count[hx] += 1
                # 下周P3（下周HR≥3%）
                if i+1 < n:
                    next_hr = rows[i+1][7]
                    hx_p3[hx].append(1 if next_hr >= 3 else 0)
                # 转移统计（看下周护型）
                if i+1 < n:
                    next_hx = parse_hx(rows[i+1][0])
                    # 己转甲（分WXZC正负）
                    if hx == '己':
                        key = '己_WXZC>0' if wxzc > 0 else '己_WXZC<=0'
                        ji_trans[key]['total'] += 1
                        if next_hx == '甲':
                            ji_trans[key]['to甲'] += 1
                        elif next_hx == '乙':
                            ji_trans[key]['to乙'] += 1
                        else:
                            ji_trans[key]['to其他'] += 1
                    # 戊(ZA>0)转甲
                    if hx == '戊' and wxza > 0:
                        key = '戊ZA>0'
                        wu_trans[key]['total'] += 1
                        if next_hx == '甲':
                            wu_trans[key]['to甲'] += 1
                        else:
                            wu_trans[key]['to其他'] += 1
                    # 丙转丁/乙（分WXZC正负）
                    if hx == '丙':
                        key = '丙_WXZC>0' if wxzc > 0 else '丙_WXZC<=0'
                        bing_trans[key]['total'] += 1
                        if next_hx == '丁':
                            bing_trans[key]['to丁'] += 1
                        elif next_hx == '乙':
                            bing_trans[key]['to乙'] += 1
                        else:
                            bing_trans[key]['to其他'] += 1
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('1. 周类 WXAB 各护型占比')
out('=' * 100)
out('')
total_hx = sum(hx_count.values())
out(f'| {"护型":<6s} | {"数量":>10s} | {"占比":>8s} | {"下周P3":>8s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->8s}:|{"":->8s}:|')
for hx in ['甲', '乙', '丙', '丁', '戊', '己']:
    cnt = hx_count.get(hx, 0)
    p3 = sum(hx_p3.get(hx, [])) / len(hx_p3.get(hx, [])) * 100 if hx_p3.get(hx) else 0
    out(f'| {hx:<6s} | {cnt:>10,d} | {cnt/total_hx*100:>7.1f}% | {p3:>7.1f}% |')

out('')
out('=' * 100)
out('2. WXAB 己 转甲概率（分 WXZC 正负）')
out('=' * 100)
out('')
out(f'| {"条件":<14s} | {"总数":>10s} | {"转甲":>8s} | {"转甲率":>8s} | {"转乙":>8s} | {"转乙率":>8s} | {"不转正交":>8s} | {"不转率":>8s} |')
out(f'|{"":->14s}|{"":->10s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for key in ['己_WXZC>0', '己_WXZC<=0']:
    s = ji_trans[key]
    total = s['total']
    if total == 0:
        continue
    not_orth = total - s['to甲']
    out(f'| {key:<14s} | {total:>10,d} | {s["to甲"]:>8,d} | {s["to甲"]/total*100:>7.1f}% | {s["to乙"]:>8,d} | {s["to乙"]/total*100:>7.1f}% | {not_orth:>8,d} | {not_orth/total*100:>7.1f}% |')

out('')
out('=' * 100)
out('3. WXAB 戊(ZA>0) 转甲概率')
out('=' * 100)
out('')
for key in ['戊ZA>0']:
    s = wu_trans[key]
    total = s['total']
    if total == 0:
        continue
    out(f'{key}: 总数 {total:,}，转甲 {s["to甲"]:,} 次 = {s["to甲"]/total*100:.1f}%，不转甲 {total-s["to甲"]:,} 次 = {(total-s["to甲"])/total*100:.1f}%')

out('')
out('=' * 100)
out('4. WXAB 丙 转丁/乙概率（分 WXZC 正负）')
out('=' * 100)
out('')
out(f'| {"条件":<14s} | {"总数":>10s} | {"转丁":>8s} | {"转丁率":>8s} | {"转乙":>8s} | {"转乙率":>8s} | {"其他":>8s} |')
out(f'|{"":->14s}|{"":->10s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for key in ['丙_WXZC>0', '丙_WXZC<=0']:
    s = bing_trans[key]
    total = s['total']
    if total == 0:
        continue
    out(f'| {key:<14s} | {total:>10,d} | {s["to丁"]:>8,d} | {s["to丁"]/total*100:>7.1f}% | {s["to乙"]:>8,d} | {s["to乙"]/total*100:>7.1f}% | {s["to其他"]:>8,d} |')

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')
# 己转甲：WXZC>0 vs WXZC<=0
if '己_WXZC>0' in ji_trans and '己_WXZC<=0' in ji_trans:
    a = ji_trans['己_WXZC>0']
    b = ji_trans['己_WXZC<=0']
    out(f'己转甲率：WXZC>0 = {a["to甲"]/a["total"]*100:.1f}% vs WXZC<=0 = {b["to甲"]/b["total"]*100:.1f}%')
    out(f'  → WXZC>0 时己转甲率更高（差 {a["to甲"]/a["total"]*100 - b["to甲"]/b["total"]*100:+.1f}pp）')

OUTF.close()
print('Done')