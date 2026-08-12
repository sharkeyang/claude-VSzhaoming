# -*- coding: utf-8 -*-
"""全量赛马：6等类 × 多条件组合，核心池口径，≥2%>37.1% 且 n≥1000"""
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

stats = defaultdict(lambda: [0, 0, 0])  # key -> [n, hit2, hit3]

def add(key, nxt, hit2, hit3):
    stats[key][0] += 1
    stats[key][1] += hit2
    stats[key][2] += hit3

files_core = 0
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
                if len(row) < 45: continue
                try:
                    nxt_gf = float(row[26])
                    dtza = float(row[13])
                    zc = float(row[14])
                    btding = float(row[40])
                    btly = float(row[42])
                    bsha = float(row[19])
                except:
                    continue
                cls = row[44].strip()
                cd = row[8].strip()
                cx = row[33].strip()
                cengjie = row[28].strip()
                bx = row[11].strip()  # 波型

                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                # 确定等类
                if cls not in ('等1', '等2', '等3', '等5', '等6', '等7'):
                    continue

                # ====== 条件定义 ======
                cond_bsha5 = bsha > 5
                cond_bsha3 = bsha > 3
                cond_ly = btly > 0
                cond_men = zc > 0 and cd == '上'
                cond_cz = cengjie.startswith('主')
                cond_btding = btding > 0
                cond_sp = bx.startswith('升')  # 升排

                # 单条件
                conds = {
                    '基准': True,
                    '偏5': cond_bsha5,
                    '偏3': cond_bsha3,
                    '连': cond_ly,
                    '门': cond_men,
                    '层主': cond_cz,
                    'BT鼎': cond_btding,
                    '升排': cond_sp,
                }
                # 双条件
                conds['偏5连'] = cond_bsha5 and cond_ly
                conds['偏5门'] = cond_bsha5 and cond_men
                conds['偏5连门'] = cond_bsha5 and cond_ly and cond_men
                conds['偏3连'] = cond_bsha3 and cond_ly
                conds['偏3门'] = cond_bsha3 and cond_men
                conds['偏3连门'] = cond_bsha3 and cond_ly and cond_men
                conds['连门'] = cond_ly and cond_men
                conds['层主升'] = cond_cz and cond_sp
                conds['层主门'] = cond_cz and cond_men
                conds['BT鼎门'] = cond_btding and cond_men

                for cname, cval in conds.items():
                    if cval:
                        add(f'{cls}|{cname}', nxt_gf, hit2, hit3)

    except Exception:
        pass
    if files_core % 1000 == 0:
        pass

# 输出
out = io.open('____temp/_full_race.txt', 'w', encoding='utf-8')
out.write(f'核心池文件: {files_core}\n')
out.write(f'策略总数: {len(stats)}\n\n')

# 过滤：≥2% > 37.1% 且 n≥1000
BENCH = 37.1
MIN_N = 1000

rows = []
for k, (n, h2, h3) in stats.items():
    p2 = h2 / n * 100 if n else 0
    p3 = h3 / n * 100 if n else 0
    if p2 > BENCH and n >= MIN_N:
        rows.append((p2, k, n, p3))

rows.sort(key=lambda x: -x[0])

out.write(f'=== 全量赛马排名（≥2% > {BENCH}%，n≥{MIN_N}，共{len(rows)}条）===\n')
out.write(f'{"排名":>4s} {"策略":<28s} {"样本":>10s} {"≥2%":>8s} {"≥3%":>8s}\n')
out.write('-' * 65 + '\n')

# 等级
def grade(p):
    if p > 60: return 'A'
    if p > 50: return 'B'
    if p > 40: return 'C'
    return 'D'

for i, (p2, k, n, p3) in enumerate(rows, 1):
    cl, cond = k.split('|', 1)
    g = grade(p2)
    # 策略名: 等级+等类+条件缩写
    # 条件缩写映射
    abbr = {
        '基准': '基准',
        '偏5': '偏5', '偏3': '偏3',
        '连': '连', '门': '门',
        '层主': '层主', 'BT鼎': 'BT鼎', '升排': '升排',
        '偏5连': '偏5连', '偏5门': '偏5门', '偏5连门': '偏5连门',
        '偏3连': '偏3连', '偏3门': '偏3门', '偏3连门': '偏3连门',
        '连门': '连门',
        '层主升': '层主升', '层主门': '层主门', 'BT鼎门': 'BT鼎门',
    }
    name = f'{g}{cl}.{abbr[cond]}'
    out.write(f'{i:>4d} {name:<28s} {n:>10,} {p2:>7.1f}% {p3:>7.1f}%\n')

out.close()
print('Done')