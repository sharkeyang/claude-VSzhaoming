# -*- coding: utf-8 -*-
"""
验证4项理论（用 昭明算展/谕组日0911 数据）
1. DTAB持续时长 < 平均持续时长（不要正交存续较长）
2. 基顶型（a龙/b龙/d虎天劫/d虎AZ劫，下破DTZA=-1/-2时可考虑再次站上DJA）
3. 帐篷=升管（甲机会段内阴柱后阳柱反包触顶）
4. 乙(DXZA>0)防M头诱多（配合周类柱排）

权威列映射（0-indexed）：
  col5=涨幅  col9=DXAB护型(含DTAB)  col10=柱排  col13=日ZA(DTZA)
  col26=次日高幅  col43=顶型  col44=日等型
"""
import csv, glob, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_dxab(s):
    """解析DXAB护型字符串，返回(护型, DTAB)
    格式: a甲↗上3.A4  -> 护型='甲', DTAB=3
    """
    if not s or len(s) < 2:
        return None, None
    hx = s[1]
    m = re.search(r'(\d+)', s[3:])
    dt = int(m.group(1)) if m else None
    return hx, dt

def parse_ding(s):
    """解析顶型字符串，返回(顶态, 核心顶型)"""
    if not s:
        return None, None
    if s[0] in ('K', 'L'):
        return s[0], s[1:]
    if s[0] == '_':
        return 'G', s[1:]
    return 'G', s

BASE_DING = {'a龙', 'b龙', 'd虎天劫', 'd虎AZ劫'}

# ---------- 单次遍历加载所有文件（保留完整行用于未来数据） ----------
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62:
                continue
            try:
                frows.append({
                    'zf': float(row[5]),
                    'dtza': int(row[13]),
                    'hx': row[9][1] if len(row[9]) > 1 else None,
                    'dtab': parse_dxab(row[9])[1],
                    'ding_state': parse_ding(row[43])[0],
                    'ding_core': parse_ding(row[43])[1],
                })
            except (ValueError, IndexError):
                continue
    files.append(frows)

total_rows = sum(len(f) for f in files)
print(f'总行数: {total_rows}')

# ---------- 平均DTAB ----------
dtabs = [r['dtab'] for f in files for r in f if r['dtab'] is not None]
avg_dtab = sum(dtabs) / len(dtabs) if dtabs else 0
print(f'平均DTAB持续时长: {avg_dtab:.2f} 天')

def check_restation(frows, i, lookahead=5):
    """未来lookahead天内是否重新站上DJA(日ZA>0)"""
    for j in range(i+1, min(i+1+lookahead, len(frows))):
        if frows[j]['dtza'] > 0:
            return True
    return False

def check_break(frows, i, lookahead=3):
    """未来lookahead天内是否跌破DJA(日ZA<0)"""
    for j in range(i+1, min(i+1+lookahead, len(frows))):
        if frows[j]['dtza'] < 0:
            return True
    return False

def check_continue_up(frows, i, lookahead=3):
    """未来lookahead天是否全部继续升管(日ZA>0)"""
    for j in range(i+1, min(i+1+lookahead, len(frows))):
        if frows[j]['dtza'] <= 0:
            return False
    return True

# ---------- 验证1: DTAB < 平均 ----------
v1 = {'short': [0,0], 'long': [0,0]}
# ---------- 验证2: 基顶型 ----------
v2 = {'base': [0,0], 'other': [0,0]}
base_detail = collections.Counter()
# ---------- 验证3: 帐篷 ----------
v3 = {'tent': [0,0], 'notent': [0,0]}
# ---------- 验证4: M头 ----------
v4 = {'mhead': [0,0], 'notmhead': [0,0]}

for frows in files:
    N = len(frows)
    for i in range(N-1):
        r = frows[i]
        # 验证1+2: 下破DTZA=-1/-2
        if r['dtza'] in (-1, -2):
            # 验证1
            if r['dtab'] is not None:
                if r['dtab'] < avg_dtab:
                    v1['short'][1] += 1
                    if check_restation(frows, i): v1['short'][0] += 1
                else:
                    v1['long'][1] += 1
                    if check_restation(frows, i): v1['long'][0] += 1
            # 验证2
            is_base = (r['ding_state'] == 'G' and r['ding_core'] in BASE_DING)
            if is_base:
                v2['base'][1] += 1
                base_detail[r['ding_core']] += 1
                if check_restation(frows, i): v2['base'][0] += 1
            else:
                v2['other'][1] += 1
                if check_restation(frows, i): v2['other'][0] += 1
        # 验证3: 甲升管 阴后阳反包
        if i >= 1:
            prev = frows[i-1]
            if r['hx'] == '甲' and r['dtza'] > 0 and r['zf'] > 0 and prev['zf'] < 0:
                is_tent = (r['ding_state'] == 'G')
                key = 'tent' if is_tent else 'notent'
                v3[key][1] += 1
                if check_continue_up(frows, i): v3[key][0] += 1
            # 验证4: 乙升管 阳后阴冲高回落
            if r['hx'] == '乙' and r['dtza'] > 0:
                is_mhead = (prev['zf'] > 0 and r['zf'] < 0)
                key = 'mhead' if is_mhead else 'notmhead'
                v4[key][1] += 1
                if check_break(frows, i): v4[key][0] += 1

# ---------- 输出 ----------
print('\n' + '='*60)
print('验证1: DTAB持续时长 < 平均持续时长')
print('='*60)
if v1['short'][1]:
    print(f'DTAB<平均({avg_dtab:.1f}): n={v1["short"][1]}, 5日重新站上DJA={v1["short"][0]/v1["short"][1]*100:.1f}%')
if v1['long'][1]:
    print(f'DTAB>=平均: n={v1["long"][1]}, 5日重新站上DJA={v1["long"][0]/v1["long"][1]*100:.1f}%')

print('\n' + '='*60)
print('验证2: 基顶型（a龙/b龙/d虎天劫/d虎AZ劫）')
print('='*60)
if v2['base'][1]:
    print(f'基顶型(G态): n={v2["base"][1]}, 5日重新站上DJA={v2["base"][0]/v2["base"][1]*100:.1f}%')
if v2['other'][1]:
    print(f'其他顶型: n={v2["other"][1]}, 5日重新站上DJA={v2["other"][0]/v2["other"][1]*100:.1f}%')
print('基顶型细分:')
for k,v in base_detail.most_common():
    print(f'  {k}: {v}')

print('\n' + '='*60)
print('验证3: 帐篷=升管（甲升管阴后阳反包触顶）')
print('='*60)
if v3['tent'][1]:
    print(f'帐篷(触顶): n={v3["tent"][1]}, 未来3日继续升管={v3["tent"][0]/v3["tent"][1]*100:.1f}%')
if v3['notent'][1]:
    print(f'非帐篷(未触顶): n={v3["notent"][1]}, 未来3日继续升管={v3["notent"][0]/v3["notent"][1]*100:.1f}%')

print('\n' + '='*60)
print('验证4: 乙(DXZA>0)防M头诱多')
print('='*60)
if v4['mhead'][1]:
    print(f'M头(阳后阴冲高回落): n={v4["mhead"][1]}, 未来3日跌破DJA={v4["mhead"][0]/v4["mhead"][1]*100:.1f}%')
if v4['notmhead'][1]:
    print(f'非M头(乙升管其他): n={v4["notmhead"][1]}, 未来3日跌破DJA={v4["notmhead"][0]/v4["notmhead"][1]*100:.1f}%')
