# -*- coding: utf-8 -*-
"""
日级别 DXAB护型 转移概率矩阵，按 DXZC 符号分条件，乙/戊按 DXZA 拆分子行+子列
===========================================================================
- 全量 谕组日 数据（7461只股票，2000万行）
- 护型：甲/乙/丙/丁/戊/己（DXAB 首字符 a/b/c/z/y/r）
- 乙拆为 乙(ZA>0) 和 乙(ZA≤0)；戊拆为 戊(ZA>0) 和 戊(ZA≤0)
- 条件：当前日 DXZC>0 vs DXZC≤0
- 转移：当前日护型 → 次日护型（横向也按 ZA 拆分子列）
- 限定：高波池 Qic+Qim+Qit
"""
import csv, os, io, json, glob
from collections import defaultdict

OUTF = io.open('____temp/_护型转移矩阵_DXZC_result.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

# 护型首字符映射
HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
# 输出行顺序
ROW_ORDER = ['甲','乙_pos','乙_neg','丙','丁','戊_pos','戊_neg','己']
# 输出列顺序（横向拆分后的目标护型）
COL_ORDER = ['甲','乙_pos','乙_neg','丙','丁','戊_pos','戊_neg','己']

# 花册映射
BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

# 转移计数: (cur_key, zc_sign, next_key) -> count
trans = defaultdict(int)
row_total = defaultdict(int)

total_rows = 0
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
            next(r)
            prev_hx = None
            prev_za = None
            prev_zc = None
            prev_key = None
            for row in r:
                if len(row) < 16:
                    continue
                dxab_raw = row[9]
                za_raw = row[13]   # 日ZA
                zc_raw = row[14]   # 日ZC
                if len(dxab_raw) < 1:
                    continue
                cur_hx = HX_MAP.get(dxab_raw[0])
                if cur_hx is None:
                    continue
                try:
                    za = float(za_raw)
                    zc = float(zc_raw)
                except:
                    continue
                total_rows += 1

                # 当前行 key（乙/戊按 ZA 拆分子行）
                if cur_hx == '乙':
                    cur_key = '乙_pos' if za > 0 else '乙_neg'
                elif cur_hx == '戊':
                    cur_key = '戊_pos' if za > 0 else '戊_neg'
                else:
                    cur_key = cur_hx

                # 次日 key（横向也按 ZA 拆分子列）
                if prev_hx is not None and prev_zc is not None:
                    zc_sign = 'pos' if prev_zc > 0 else 'neg'
                    trans[(prev_key, zc_sign, cur_key)] += 1
                    row_total[(prev_key, zc_sign)] += 1

                prev_hx = cur_hx
                prev_key = cur_key
                prev_za = za
                prev_zc = zc
    except Exception:
        pass
    files_done += 1

out(f'## 数据规模')
out(f'文件数: {files_done}, 总行数: {total_rows:,}')
out(f'限定: 高波池 Qic+Qim+Qit')
out('')

def print_matrix(title, zc_sign):
    out('=' * 90)
    out(title)
    out('=' * 90)
    # 表头
    header = f'| {"当前":>10s} | {"样本":>8s} |'
    for col in COL_ORDER:
        header += f' {col:>8s} |'
    header += f' {"维持":>6s} |'
    out(header)
    sep = f'|{"":->10s}|{"":->8s}:|'
    for col in COL_ORDER:
        sep += f'{"":->8s}:|'
    sep += f'{"":->6s}:|'
    out(sep)

    for cur in ROW_ORDER:
        total = row_total[(cur, zc_sign)]
        if total < 100:
            continue
        cells = []
        for nxt in COL_ORDER:
            cnt = trans[(cur, zc_sign, nxt)]
            cells.append(f'{cnt/total*100:>7.1f}%')
        # 维持率：乙_pos/乙_neg 的维持 = →乙_pos 或 →乙_neg
        if cur in ('乙_pos', '乙_neg'):
            mr = (trans[(cur, zc_sign, '乙_pos')] + trans[(cur, zc_sign, '乙_neg')]) / total * 100
        elif cur in ('戊_pos', '戊_neg'):
            mr = (trans[(cur, zc_sign, '戊_pos')] + trans[(cur, zc_sign, '戊_neg')]) / total * 100
        else:
            mr = trans[(cur, zc_sign, cur)] / total * 100
        row_str = f'| {cur:>10s} | {total:>8,d} |' + ' '.join(cells) + f' | {mr:>5.1f}% |'
        out(row_str)
    out('')

print_matrix('一、DXZC>0 条件下的护型转移矩阵（高波池）', 'pos')
print_matrix('二、DXZC≤0 条件下的护型转移矩阵（高波池）', 'neg')

# 无条件矩阵
out('=' * 90)
out('三、无条件护型转移矩阵（高波池，全样本）')
out('=' * 90)
header = f'| {"当前":>10s} | {"样本":>8s} |'
for col in COL_ORDER:
    header += f' {col:>8s} |'
header += f' {"维持":>6s} |'
out(header)
sep = f'|{"":->10s}|{"":->8s}:|'
for col in COL_ORDER:
    sep += f'{"":->8s}:|'
sep += f'{"":->6s}:|'
out(sep)
for cur in ROW_ORDER:
    total = row_total[(cur, 'pos')] + row_total[(cur, 'neg')]
    if total < 100:
        continue
    cells = []
    for nxt in COL_ORDER:
        cnt = trans[(cur, 'pos', nxt)] + trans[(cur, 'neg', nxt)]
        cells.append(f'{cnt/total*100:>7.1f}%')
    if cur in ('乙_pos', '乙_neg'):
        mr = (trans[(cur, 'pos', '乙_pos')] + trans[(cur, 'pos', '乙_neg')] +
              trans[(cur, 'neg', '乙_pos')] + trans[(cur, 'neg', '乙_neg')]) / total * 100
    elif cur in ('戊_pos', '戊_neg'):
        mr = (trans[(cur, 'pos', '戊_pos')] + trans[(cur, 'pos', '戊_neg')] +
              trans[(cur, 'neg', '戊_pos')] + trans[(cur, 'neg', '戊_neg')]) / total * 100
    else:
        mr = (trans[(cur, 'pos', cur)] + trans[(cur, 'neg', cur)]) / total * 100
    row_str = f'| {cur:>10s} | {total:>8,d} |' + ' '.join(cells) + f' | {mr:>5.1f}% |'
    out(row_str)
out('')

# 关键差异：ZC>0 vs ZC≤0 的转移差异
out('=' * 90)
out('四、DXZC 对转移的影响（ZC>0 减 ZC≤0，单位 pp，高波池）')
out('=' * 90)
header = f'| {"当前":>10s} |'
for col in COL_ORDER:
    header += f' {col:>8s} |'
out(header)
sep = f'|{"":->10s}|'
for col in COL_ORDER:
    sep += f'{"":->8s}:|'
out(sep)
for cur in ROW_ORDER:
    tp = row_total[(cur, 'pos')]
    tn = row_total[(cur, 'neg')]
    if tp < 100 or tn < 100:
        continue
    cells = []
    for nxt in COL_ORDER:
        pp = trans[(cur, 'pos', nxt)] / tp * 100
        pn = trans[(cur, 'neg', nxt)] / tn * 100
        cells.append(f'{pp-pn:>+7.1f}')
    row_str = f'| {cur:>10s} |' + ' '.join(cells) + ' |'
    out(row_str)
out('')

OUTF.close()
print('Done')