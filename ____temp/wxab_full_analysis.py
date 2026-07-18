"""全量分析：WXAB引领WXCD + 市板分布 + 条件有效性"""
import csv, glob, os
from collections import defaultdict, Counter

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = sorted(glob.glob(os.path.join(DIR, "谕组_*.csv")))
print(f"全量: {len(files)} 只股票")

# ====== 工具函数 ======
WXAB_POS = {'甲':4,'乙':3,'己':2}
WXAB_NEG = {'丙':1,'戊':0}
WXCD_GOOD = {'金':3,'银':2,'铜':1}
WXCD_BAD = {'铁':0,'屎':0,'尿':0,'唏':0,'嘘':0}

def wxab_max(s):
    if not s: return -1
    for c in '甲乙己丙戊':
        if c in s: return {'甲':4,'乙':3,'己':2,'丙':1,'戊':0}[c]
    return -1

def wxab_label(s):
    for c in '甲乙己丙戊':
        if c in s: return c
    return '?'

def wxcd_best(s):
    if not s: return -1
    for c in '金银铜铁屎尿唏嘘':
        if c in s:
            return {'金':3,'银':2,'铜':1,'铁':0,'屎':0,'尿':0,'唏':0,'嘘':0}[c]
    return -1

def wxcd_label(s):
    for c in '金银铜':
        if c in s: return c
    if '铁' in s: return '铁'
    for c in '屎尿唏嘘':
        if c in s: return c
    return '?'

def board(code):
    c = code.replace('谕组_','').replace('.csv','')
    if c.startswith(('600','601','603','605')): return 'Qd'
    if c.startswith(('000','001','002')): return 'Qe'
    if c.startswith('300'): return 'Qic'
    if c.startswith('688'): return 'Qim'
    if c.startswith('bj'): return 'Qin'
    return 'Qin'

# ====== 1. 全量: WXAB > 0 vs ≤ 0 的 WXCD 分布 ======
print("\n====== 1. WXAB>0 vs ≤0 → WXCD分布（全量） ======")
stats = {'pos':Counter(), 'neg':Counter(), 'total': {'pos':0,'neg':0}}
board_stats = defaultdict(lambda: {'pos':Counter(), 'neg':Counter(), 'pos_n':0, 'neg_n':0})

count_files = 0
for f in files:
    code = os.path.basename(f)
    b = board(code)
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        r = csv.DictReader(fh)
        for row in r:
            wxab = row.get('WXAB','')
            wxcd = row.get('WXCD','')
            if not wxab or not wxcd: continue
            ab_s = wxab_max(wxab)
            cd_l = wxcd_label(wxcd)
            key = 'pos' if ab_s >= 2 else 'neg'
            stats[key]['总'] += 1
            stats[key][cd_l] += 1
            stats['total'][key] += 1
            board_stats[b][key][cd_l] += 1
            board_stats[b][f'{key}_n'] += 1
    count_files += 1
    if count_files % 1000 == 0:
        print(f"  已处理: {count_files}/{len(files)}")

print(f"\n  WXAB>0: {stats['total']['pos']:,} 行")
print(f"  WXAB≤0: {stats['total']['neg']:,} 行")
print()
for k in ['pos','neg']:
    t = stats[k]['总']
    label = 'WXAB>0 (甲乙己)' if k == 'pos' else 'WXAB≤0 (丙戊)'
    print(f"  {label}:")
    for v in ['金','银','铜','铁','屎','尿','唏','嘘','?']:
        if v in stats[k]:
            pct = stats[k][v]/t*100
            bar = '█'*int(pct/2)
            print(f"    {v}: {stats[k][v]:>8,} ({pct:5.1f}%) {bar}")
    g = sum(stats[k].get(x,0) for x in ['金','银','铜'])
    b = sum(stats[k].get(x,0) for x in ['铁','屎','尿','唏','嘘'])
    print(f"    ───────────────────")
    print(f"    金银铜合计: {g:>8,} ({g/t*100:.1f}%)")
    print(f"    屎尿嘘合计: {b:>8,} ({b/t*100:.1f}%)")

# ====== 2. 按市板细分 ======
print("\n\n====== 2. 按市板细分 ======")
for b in ['Qd','Qe','Qic','Qim','Qin']:
    bs = board_stats[b]
    if bs['pos_n'] == 0: continue
    print(f"\n  [{b}]")
    for k in ['pos','neg']:
        n = bs[f'{k}_n']
        if n == 0: continue
        g = sum(bs[k].get(x,0) for x in ['金','银','铜'])
        bd = sum(bs[k].get(x,0) for x in ['铁','屎','尿','唏','嘘'])
        label = 'WXAB>0' if k == 'pos' else 'WXAB≤0'
        print(f"    {label}: 金银铜={g/n*100:.1f}%  屎尿嘘={bd/n*100:.1f}%  (n={n:,})")

# ====== 3. WXAB领先WXCD（全量） ======
print("\n\n====== 3. WXAB引领WXCD（全量） ======")
all_trans = []
lag_dist = Counter()
ab_trig = Counter()
cd_target = Counter()
stock_trans = defaultdict(list)

for f in files:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))
    for i in range(len(rows)-4):
        wab_now = rows[i].get('WXAB','')
        wcd_now = rows[i].get('WXCD','')
        if not wab_now or not wcd_now: continue
        sab_now = wxab_max(wab_now)
        sab_prev = wxab_max(rows[i-1].get('WXAB','')) if i > 0 else sab_now
        if sab_now > sab_prev and sab_now >= 2:
            wab_l = wxab_label(wab_now)
            wcd_l = wxcd_label(wcd_now)
            # 寻找后续1-4周WXCD提升
            for lag in range(1,5):
                if i+lag >= len(rows): break
                wcd_f = rows[i+lag].get('WXCD','')
                if not wcd_f: continue
                scd_f = wxcd_best(wcd_f)
                if scd_f > wxcd_best(wcd_now) and scd_f >= 1:
                    all_trans.append((wab_l, wcd_l, wxcd_label(wcd_f), lag))
                    lag_dist[lag] += 1
                    ab_trig[wab_l] += 1
                    cd_target[wxcd_label(wcd_f)] += 1
                    break

n = len(all_trans)
print(f"  WXAB提升后WXCD在1-4周内跟随: {n:,} 次")
print(f"\n  领先周数:")
for lag in [1,2,3,4]:
    print(f"    {lag}周: {lag_dist[lag]:>6,} ({lag_dist[lag]/n*100:.1f}%)")
print(f"\n  WXAB触发:")
for ab in ['己','甲','乙','丙','戊']:
    if ab in ab_trig:
        print(f"    WXAB={ab}: {ab_trig[ab]:>6,} ({ab_trig[ab]/n*100:.1f}%)")
print(f"\n  WXCD到达:")
for cd in ['金','银','铜']:
    if cd in cd_target:
        print(f"    →{cd}: {cd_target[cd]:>6,} ({cd_target[cd]/n*100:.1f}%)")

# ====== 4. 深化：WXAB提升的持续性 ======
print("\n\n====== 4. 深化分析：WXAB提升后的持续性 ======")
# WXAB提升后，检查后续4周的WXCD稳定性
stable_gold = 0  # 提升后WXCD维持金银
unstable = 0     # 提升后又掉回屎尿

for f in files[:2000]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))
    for i in range(len(rows)-8):
        wab_now = rows[i].get('WXAB','')
        wcd_now = rows[i].get('WXCD','')
        if not wab_now or not wcd_now: continue
        sab_now = wxab_max(wab_now)
        sab_prev = wxab_max(rows[i-1].get('WXAB','')) if i > 0 else sab_now
        if sab_now > sab_prev and sab_now >= 2:
            # 看后续8周WXCD表现
            goods = sum(1 for j in range(1,9) if i+j < len(rows) and wxcd_best(rows[i+j].get('WXCD','')) >= 1)
            if goods >= 6: stable_gold += 1
            elif goods <= 2: unstable += 1

print(f"  WXAB提升后8周内: 保持金银≥6周: {stable_gold}  掉回屎尿≥6周: {unstable}")

# ====== 5. 什么条件下WXAB提升后WXCD不跟随 ======
print("\n\n====== 5. WXAB提升但WXCD不跟随的典型场景 ======")
false_positives = 0
total_ab_up = 0
for f in files[:2000]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))
    for i in range(len(rows)-4):
        wab_now = rows[i].get('WXAB','')
        if not wab_now: continue
        sab_now = wxab_max(wab_now)
        sab_prev = wxab_max(rows[i-1].get('WXAB','')) if i > 0 else sab_now
        if sab_now > sab_prev and sab_now >= 2:
            total_ab_up += 1
            # 检查1-4周内WXCD是否跟随
            followed = False
            for lag in range(1,5):
                if i+lag >= len(rows): break
                wcd_f = rows[i+lag].get('WXCD','')
                if not wcd_f: continue
                if wxcd_best(wcd_f) > wxcd_best(rows[i].get('WXCD','')) and wxcd_best(wcd_f) >= 1:
                    followed = True
                    break
            if not followed:
                false_positives += 1

print(f"  WXAB提升总次数: {total_ab_up}")
print(f"  WXCD跟随: {total_ab_up - false_positives} ({(total_ab_up-false_positives)/total_ab_up*100:.1f}%)")
print(f"  WXCD不跟随(假信号): {false_positives} ({false_positives/total_ab_up*100:.1f}%)")

# ====== 6. WXAB各等级的冲高策分 ======
print("\n\n====== 6. WXAB各等级的周冲策分表现 ======")
# 简化: 用WXAB等级分组, 看金银占比
wxab_grades = {'甲':Counter(), '乙':Counter(), '己':Counter(), '丙':Counter(), '戊':Counter()}
for f in files[:2000]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            wxab = row.get('WXAB','')
            wxcd = row.get('WXCD','')
            if not wxab or not wxcd: continue
            for c in '甲乙己丙戊':
                if c in wxab:
                    wxab_grades[c][wxcd_label(wxcd)] += 1
                    break

for c in '甲乙己丙戊':
    d = wxab_grades[c]
    t = sum(d.values())
    if t == 0: continue
    g = d.get('金',0) + d.get('银',0)
    print(f"  WXAB={c}: 金银={g/t*100:.1f}%  屎尿={(t-g)/t*100:.1f}%  (n={t:,})")

print("\n\n====== 分析完成 ======")