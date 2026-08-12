# -*- coding: utf-8 -*-
"""全量赛马 v2：从 DTZA+中符串 重算 6等，不依赖 CSV 日等型列"""
import csv, os, io
from collections import defaultdict

CODE2BOARD = {}
with open('____temp/市板映射.csv', 'r', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if len(row) >= 2:
            CODE2BOARD[row[0].strip()] = row[1].strip()
CORE = {'Qic', 'Qim', 'Qit', 'Qin'}

stats = defaultdict(lambda: [0, 0, 0])

def add(key, nxt, h2, h3):
    stats[key][0] += 1
    stats[key][1] += h2
    stats[key][2] += h3

def get_cls(dtza, cx):
    """6等分类：从 DTZA(日ZA) + 中符串末位 推导"""
    if not cx: return None
    mf = cx[-1]  # 末符
    if dtza == 1:
        return '等1'
    elif dtza >= 2:
        return '等3' if mf in ('A', 'B') else '等2'
    elif dtza == -1:
        return '等5'
    elif dtza <= -2:
        return '等7' if mf in ('E', 'F') else '等6'
    return None

files_core = 0
total_rows = 0
cls_counts = defaultdict(int)

for fname in os.listdir('昭明算展/谕组日'):
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if CODE2BOARD.get(code, '') not in CORE:
        continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 35: continue
                # 逐个字段容错转换（BT鼎/BT连阳 仅 ZE>0+ZC>0 时有值，其他为空）
                def to_f(v):
                    try:
                        return float(v)
                    except:
                        return 0.0
                nxt_gf = to_f(row[26])
                dtza = to_f(row[13])
                zc = to_f(row[14])
                btding = to_f(row[40]) if len(row) > 40 else 0.0
                btly = to_f(row[42]) if len(row) > 42 else 0.0
                bsha = to_f(row[19]) if len(row) > 19 else 0.0
                cx = row[33].strip()  # 中符串
                cd = row[8].strip()
                cengjie = row[28].strip() if len(row) > 28 else ''
                bx = row[11].strip() if len(row) > 11 else ''

                cls = get_cls(dtza, cx)
                if cls is None:
                    continue
                cls_counts[cls] += 1
                total_rows += 1

                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                cond_bsha5 = bsha > 5
                cond_bsha3 = bsha > 3
                cond_ly = btly > 0
                cond_men = zc > 0 and cd == '上'
                cond_cz = cengjie.startswith('主')
                cond_btding = btding > 0
                cond_sp = bx.startswith('升')

                conds = {
                    '基准': True,
                    '偏5': cond_bsha5,
                    '偏3': cond_bsha3,
                    '连': cond_ly,
                    '门': cond_men,
                    '层主': cond_cz,
                    'BT鼎': cond_btding,
                    '升排': cond_sp,
                    '偏5连': cond_bsha5 and cond_ly,
                    '偏5门': cond_bsha5 and cond_men,
                    '偏5连门': cond_bsha5 and cond_ly and cond_men,
                    '偏3连': cond_bsha3 and cond_ly,
                    '偏3门': cond_bsha3 and cond_men,
                    '偏3连门': cond_bsha3 and cond_ly and cond_men,
                    '连门': cond_ly and cond_men,
                    '层主升': cond_cz and cond_sp,
                    '层主门': cond_cz and cond_men,
                    'BT鼎门': cond_btding and cond_men,
                }
                for cname, cval in conds.items():
                    if cval:
                        add(f'{cls}|{cname}', nxt_gf, hit2, hit3)
    except Exception:
        pass

# 输出
out = io.open('____temp/_full_race_v2.txt', 'w', encoding='utf-8')
out.write(f'核心池文件: {files_core}, 总行数: {total_rows}\n')
out.write(f'等类分布: {dict(cls_counts)}\n\n')

BENCH = 37.1
MIN_N = 1000

rows = []
for k, (n, h2, h3) in stats.items():
    p2 = h2 / n * 100 if n else 0
    p3 = h3 / n * 100 if n else 0
    if p2 > BENCH and n >= MIN_N:
        rows.append((p2, k, n, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))  # 按≥2%降序，同分按样本降序

out.write(f'=== 全量赛马排名（≥2% > {BENCH}%，n≥{MIN_N}，共{len(rows)}条）===\n')
out.write(f'{"排名":>4s} {"策略":<28s} {"样本":>10s} {"≥2%":>8s} {"≥3%":>8s}\n')
out.write('-' * 65 + '\n')

def grade(p):
    if p > 60: return 'A'
    if p > 50: return 'B'
    if p > 40: return 'C'
    return 'D'

for i, (p2, k, n, p3) in enumerate(rows, 1):
    cl, cond = k.split('|', 1)
    g = grade(p2)
    name = f'{g}{cl}.{cond}'
    out.write(f'{i:>4d} {name:<28s} {n:>10,} {p2:>7.1f}% {p3:>7.1f}%\n')

out.close()
print(f'Done: {len(rows)} strategies, {total_rows} rows, {files_core} files')