"""WXAB双向带动 + 市板细分（全量7463只）"""
import csv, glob, os
from collections import defaultdict, Counter

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = sorted(glob.glob(os.path.join(DIR, "谕组_*.csv")))
print(f"全量: {len(files)} 只")

def first_wxab(s):
    if not s: return '?'
    for c in '甲乙己丙戊':
        if c in s:
            return c
    if '丁' in s: return '丁'
    return '?'

def wxab_score(c):
    return {'甲':4,'乙':3,'己':2,'丙':1,'丁':0,'戊':0}.get(c, -1)

def wxcd_label(s):
    for c in '金银铜':
        if c in s: return c
    if '铁' in s: return '铁'
    for c in '屎尿唏嘘':
        if c in s: return c
    return '?'

def wxcd_score(s):
    for c in '金银铜':
        if c in s: return {'金':3,'银':2,'铜':1}[c]
    return 0

def board(code):
    name = code.replace('谕组_','').replace('.csv','')
    # name = exchange + code, e.g. 'sh600000' or 'sz300750'
    if name.startswith('bj'): return 'Qin'
    # 去掉交易所前缀(sh/sz)
    c = name[2:] if len(name) > 2 else name
    if c.startswith(('600','601','603','605')): return 'Qd'
    if c.startswith(('000','001','002')): return 'Qe'
    if c.startswith('300'): return 'Qic'
    if c.startswith('688'): return 'Qim'
    return 'Qin'

# 正向带动: WXAB(丙戊→甲乙己) → 后续WXCD(屎尿→金银)
# 反向带动: WXAB(甲乙己→丙戊) → 后续WXCD(金银→屎尿)
pos_follow = 0  # 正向带动成功
pos_fail = 0    # 正向带动失败
neg_follow = 0  # 反向带动成功
neg_fail = 0    # 反向带动失败

pos_by_board = defaultdict(lambda: {'f':0,'t':0})
neg_by_board = defaultdict(lambda: {'f':0,'t':0})

for f in files:
    b = board(os.path.basename(f))
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        rows = list(csv.DictReader(fh))
    for i in range(len(rows)-4):
        wab_cur = first_wxab(rows[i].get('WXAB',''))
        wab_prev = first_wxab(rows[i-1].get('WXAB','')) if i > 0 else wab_cur
        wcd_cur = rows[i].get('WXCD','')
        if wab_cur == '?' or not wcd_cur: continue
        sc_cur = wxab_score(wab_cur)
        sc_prev = wxab_score(wab_prev)
        sc_wcd = wxcd_score(wcd_cur)

        # 正向: WXAB从低级升到甲乙己
        if sc_cur >= 2 and sc_prev < 2 and sc_prev >= 0:
            # 看后续4周WXCD是否提升
            followed = False
            for lag in range(1,5):
                if i+lag >= len(rows): break
                wcd_f = rows[i+lag].get('WXCD','')
                if not wcd_f: continue
                if wxcd_score(wcd_f) >= 2:  # 金或银
                    followed = True
                    break
            if followed:
                pos_follow += 1
                pos_by_board[b]['t'] += 1
            else:
                pos_fail += 1
                pos_by_board[b]['f'] += 1

        # 反向: WXAB从甲乙己降到丙戊
        if sc_cur < 2 and sc_prev >= 2:
            followed = False
            for lag in range(1,5):
                if i+lag >= len(rows): break
                wcd_f = rows[i+lag].get('WXCD','')
                if not wcd_f: continue
                if wxcd_score(wcd_f) < 1:  # 屎尿唏
                    followed = True
                    break
            if followed:
                neg_follow += 1
                neg_by_board[b]['t'] += 1
            else:
                neg_fail += 1
                neg_by_board[b]['f'] += 1

print(f"\n=== WXAB正向带动（低级→甲乙己，后续WXCD转金银）===")
total_pos = pos_follow + pos_fail
print(f"总事件: {total_pos}")
print(f"WXCD跟随转好: {pos_follow} ({pos_follow/total_pos*100:.1f}%)")
print(f"WXCD未跟随: {pos_fail} ({pos_fail/total_pos*100:.1f}%)")

print(f"\n=== WXAB反向带动（甲乙己→丙戊，后续WXCD转屎尿）===")
total_neg = neg_follow + neg_fail
print(f"总事件: {total_neg}")
print(f"WXCD跟随转差: {neg_follow} ({neg_follow/total_neg*100:.1f}%)")
print(f"WXCD未跟随: {neg_fail} ({neg_fail/total_neg*100:.1f}%)")

print(f"\n=== 市板细分：正向带动 ===")
for b in ['Qd','Qe','Qic','Qim','Qin']:
    d = pos_by_board[b]
    t = d['t']+d['f']
    if t < 100: continue
    print(f"  [{b}] 跟随={d['t']/t*100:.1f}% (n={t})")

print(f"\n=== 市板细分：反向带动 ===")
for b in ['Qd','Qe','Qic','Qim','Qin']:
    d = neg_by_board[b]
    t = d['t']+d['f']
    if t < 100: continue
    print(f"  [{b}] 跟随={d['t']/t*100:.1f}% (n={t})")

# 各等级WXAB → WXCD交叉表
print(f"\n=== WXAB各等级 → WXCD分布（全量）===")
ab_cd = defaultdict(lambda: defaultdict(int))
for f in files:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            wab = first_wxab(row.get('WXAB',''))
            wcd = wxcd_label(row.get('WXCD',''))
            if wab != '?' and wcd:
                ab_cd[wab][wcd] += 1

for ab in ['乙','甲','丙','己','戊']:
    d = ab_cd[ab]
    t = sum(d.values())
    if t < 100: continue
    g = d.get('金',0)+d.get('银',0)
    b = d.get('屎',0)+d.get('尿',0)+d.get('唏',0)+d.get('嘘',0)
    print(f"  WXAB={ab}: 金银={g/t*100:.1f}%  屎尿={b/t*100:.1f}%  (n={t})")