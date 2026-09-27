# -*- coding: utf-8 -*-
"""
周类护型转移矩阵（2026-09-26）：仿照日类 §2.3.1.1 格式
=====================================================
按 WXZC 正负拆分，8 护型（甲/乙ZA>0/乙ZA≤0/丙/丁/戊ZA>0/戊ZA≤0/己）全矩阵
护型解析：WXAB[4] 第1字符 = a甲/b乙/c丙/z丁/y戊/r己；乙/戊按 WXZA 符号拆分

列映射（元数据_vba数据映射_周类.md）：
  [4]  WXAB 护型
  [14] WXZA
  [16] WXZC
  [3]  HR（周高幅）
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_周类转移矩阵.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_wxab = 4
i_wxza = 14
i_wxzc = 16
i_hr = 3

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(wxab, wxza):
    """解析护型，乙/戊按 WXZA 符号拆分"""
    if not wxab or len(wxab) < 1:
        return ''
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
    return ''

# 转移矩阵：trans[WXZC正负][今日护型][明日护型] = 次数
trans = {
    'WXZC>0': defaultdict(lambda: defaultdict(int)),
    'WXZC<=0': defaultdict(lambda: defaultdict(int)),
}
# 各护型下周P3
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
                if len(row) <= max(i_wxab, i_wxza, i_wxzc, i_hr):
                    continue
                try:
                    wxab = row[i_wxab].strip()
                    wxza = float(row[i_wxza])
                    wxzc = float(row[i_wxzc])
                    hr = float(row[i_hr])
                except (ValueError, IndexError):
                    continue
                rows.append((wxab, wxza, wxzc, hr))

            n = len(rows)
            for i in range(n):
                wxab, wxza, wxzc, hr = rows[i]
                hx = parse_hx(wxab, wxza)
                if not hx:
                    continue
                key = 'WXZC>0' if wxzc > 0 else 'WXZC<=0'
                # 下周P3
                if i+1 < n:
                    next_hr = rows[i+1][3]
                    hx_p3[hx].append(1 if next_hr >= 3 else 0)
                # 转移
                if i+1 < n:
                    next_hx = parse_hx(rows[i+1][0], rows[i+1][1])
                    if next_hx:
                        trans[key][hx][next_hx] += 1
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('周类护型转移矩阵（按 WXZC 正负拆分）')
out('=' * 100)
out('')
out('护型顺序：甲 / 乙(ZA>0) / 乙(ZA≤0) / 丙 / 丁 / 戊(ZA>0) / 戊(ZA≤0) / 己')
out('')
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']

for key in ['WXZC>0', 'WXZC<=0']:
    out(f'--- {key} ---')
    out('')
    # 表头
    header = '| 今日\\明日 | ' + ' | '.join(HX_ORDER) + ' |'
    out(header)
    out('|' + '---|' * (len(HX_ORDER) + 1))
    for hx in HX_ORDER:
        row = trans[key][hx]
        total = sum(row.values())
        if total == 0:
            continue
        cells = []
        for tgt in HX_ORDER:
            cnt = row.get(tgt, 0)
            cells.append(f'{cnt/total*100:>5.1f}%' if cnt > 0 else '  —  ')
        out(f'| **{hx}** | ' + ' | '.join(cells) + ' |')
    out('')

out('')
out('=' * 100)
out('各护型下周P3（周高幅≥3%）')
out('=' * 100)
out('')
out(f'| {"护型":<12s} | {"样本":>10s} | {"下周P3":>8s} |')
out(f'|{"":->12s}|{"":->10s}:|{"":->8s}:|')
for hx in HX_ORDER:
    vals = hx_p3.get(hx, [])
    if not vals:
        continue
    out(f'| {hx:<12s} | {len(vals):>10,d} | {sum(vals)/len(vals)*100:>7.1f}% |')

out('')
out('=' * 100)
out('关键转移（用户要验证的结论）')
out('=' * 100)
out('')
# 己转甲（分WXZC）
for key in ['WXZC>0', 'WXZC<=0']:
    ji = trans[key]['己']
    total = sum(ji.values())
    if total == 0:
        continue
    to甲 = ji.get('甲', 0)
    out(f'{key} 己→甲: {to甲/total*100:.1f}%（不转正交 {total-to甲} = {(total-to甲)/total*100:.1f}%）')
# 戊(ZA>0)转甲
for key in ['WXZC>0', 'WXZC<=0']:
    wu = trans[key]['戊(ZA>0)']
    total = sum(wu.values())
    if total == 0:
        continue
    to甲 = wu.get('甲', 0)
    out(f'{key} 戊(ZA>0)→甲: {to甲/total*100:.1f}%')
# 丙转丁/乙
for key in ['WXZC>0', 'WXZC<=0']:
    bing = trans[key]['丙']
    total = sum(bing.values())
    if total == 0:
        continue
    to丁 = bing.get('丁', 0)
    to乙 = bing.get('乙(ZA>0)', 0) + bing.get('乙(ZA≤0)', 0)
    out(f'{key} 丙→丁: {to丁/total*100:.1f}%，丙→乙: {to乙/total*100:.1f}%')

OUTF.close()
print('Done')