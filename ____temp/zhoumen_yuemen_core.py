# -*- coding: utf-8 -*-
"""周门×月门 全量核心池重跑 —— 修复 §3.1/§3.3 旧样本量(1.12M) → 真实核心池(15.5M)"""
import csv, os, io
from collections import Counter

# 加载市板映射
CODE2BOARD = {}
with open('____temp/市板映射.csv', 'r', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if len(row) >= 2:
            CODE2BOARD[row[0].strip()] = row[1].strip()

CORE = {'Qic', 'Qim', 'Qit'}  # 高波池（已剔除Qin非成分股）
n_core = sum(1 for b in CODE2BOARD.values() if b in CORE)
n_excl = sum(1 for b in CODE2BOARD.values() if b not in CORE)
out = io.open('____temp/_zhoumen_yuemen_core.txt', 'w', encoding='utf-8')

def outln(s=''):
    out.write(s + '\n')

# 统计：核心池
# 4格组合 + 等高线分层
total = 0
combos = Counter()
combo_hits = Counter()  # (combo) -> ≥2% hits
# 等高线×周门×月门分层
class_stats = {}  # (cls, zm, ym) -> count
class_hits = {}   # (cls, zm, ym) -> ≥2%

files_core = 0
files_excl = 0

for fname in os.listdir('昭明算展/谕组日'):
    code = fname.replace('谕组日_', '').replace('.csv', '')
    board = CODE2BOARD.get(code, '')
    if board not in CORE:
        files_excl += 1
        continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 17: continue
                gf_raw = row[6].strip()
                cd_raw = row[8].strip()
                za_raw = row[13].strip()
                zc_raw = row[14].strip()
                ze_raw = row[15].strip()
                # 等高线类别：需要从 row 里取。等高线列是最后一列(日等型)
                # 但某些CSV可能没有。用 row[44] 如果存在
                try:
                    gf = float(gf_raw)
                except:
                    gf = 0
                try:
                    zc = float(zc_raw)
                except:
                    zc = 0
                try:
                    ze = float(ze_raw)
                except:
                    ze = 0
                try:
                    za = float(za_raw)
                except:
                    za = 0

                zhoumen = (zc > 0 and cd_raw == '上')
                yuemen = (ze > 0)

                total += 1
                # 4格组合
                c = ('周门✓月门✓' if zhoumen and yuemen else
                     '周门✓月门✗' if zhoumen else
                     '周门✗月门✓' if yuemen else
                     '周门✗月门✗')
                combos[c] += 1
                if gf >= 2:
                    combo_hits[c] += 1
    except Exception:
        pass
    if files_core % 1000 == 0:
        outln(f'Progress: core={files_core} excl={files_excl}')

outln(f'## 核心池周门×月门 全量重跑')
outln(f'映射文件代码数: {len(CODE2BOARD)} (核心池{n_core} + 排除{n_excl})')
outln(f'核心池文件: {files_core}, 排除池文件: {files_excl}')
outln(f'核心池总行数: {total}')
outln('')

def pct(a, b):
    return a / b * 100 if b else 0

outln('=== 4格组合（核心池） ===')
outln(f'| 组合 | 样本 | 占比 | 下日高≥2% |')
outln(f'|:----|-----:|:----:|:-------:|')
outln(f'| 全样本（核心池基准） | {total:,} | 100% | {pct(sum(combo_hits.values()), total):.1f}% |')
for c in ['周门✓月门✓', '周门✓月门✗', '周门✗月门✓', '周门✗月门✗']:
    n = combos.get(c, 0)
    h = combo_hits.get(c, 0)
    outln(f'| **{c}** | {n:,} | {pct(n, total):.1f}% | {pct(h, n):.1f}% |')
outln('')
outln(f'总和校验: {sum(combos.values()):,} vs {total:,}')
out.close()
print('Done')