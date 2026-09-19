# -*- coding: utf-8 -*-
"""
验证帐篷（回调后阳柱继续上升）
用户定义：升管中暂时出现阴柱或下破DJA，但再次出现阳柱后会继续上升的概率
指标：回调后阳柱，未来3日继续升管（日ZA>0）概率
"""
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_ding(s):
    if not s: return None,None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

# 加载数据
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
                zf = float(row[5])
                dtza = int(row[13])
                hx = row[9][1] if len(row[9]) > 1 else None
                ds, dc = parse_ding(row[43])
                frows.append((zf, dtza, hx, ds, dc))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}')

def cont_up(frows, i, la=3):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][1] <= 0:
            return False
    return True

# 场景：甲护型 + 升管（日ZA>0）
# 回调后阳柱：当前柱阳柱(zf>0)，之前出现过阴柱(zf<0)或下破DJA(dtza<0)
# 指标：阳柱后未来3日继续升管

# 形态A：升管中阴柱后阳柱（回调反弹）
#   当前阳柱，前一柱阴柱，且日ZA>0
# 形态B：下破DJA后重新站上（下破反弹）
#   当前阳柱且日ZA>0（重新站上），之前下破过DJA（日ZA<0）
# 形态C：暂停后阳柱（暂停反弹）
#   当前阳柱，前一柱小阴/十字星(|zf|<0.5%)，日ZA>0

stats = {
    'A': collections.defaultdict(lambda: [0,0]),  # 阴后阳
    'B': collections.defaultdict(lambda: [0,0]),  # 下破后站上
    'C': collections.defaultdict(lambda: [0,0]),  # 暂停后阳
}
# 基线：升管中所有阳柱
base = [0,0]

for frows in files:
    N = len(frows)
    for i in range(1, N-1):
        zf, dtza, hx, ds, dc = frows[i]
        pzf, pdtza, phx, pds, pdc = frows[i-1]
        if hx != '甲' or dtza <= 0:
            continue
        # 基线：升管中阳柱
        if zf > 0:
            base[1] += 1
            if cont_up(frows, i): base[0] += 1
        # 形态A：阴后阳（前一柱阴柱）
        if zf > 0 and pzf < 0:
            stats['A'][dc][1] += 1
            if cont_up(frows, i): stats['A'][dc][0] += 1
        # 形态B：下破后站上（当前阳柱且日ZA>0，之前下破过DJA）
        if zf > 0 and dtza > 0:
            # 往前找最近的下破DJA（日ZA<0）
            k = i-1
            while k >= 0 and frows[k][1] > 0:
                k -= 1
            if k >= 0 and i - k <= 5:  # 5日内下破过
                stats['B'][dc][1] += 1
                if cont_up(frows, i): stats['B'][dc][0] += 1
        # 形态C：暂停后阳（前一柱小阴/十字星）
        if zf > 0 and abs(pzf) < 0.5:
            stats['C'][dc][1] += 1
            if cont_up(frows, i): stats['C'][dc][0] += 1

print(f'\n基线(甲升管阳柱): n={base[1]}, 未来3日继续升管={base[0]/base[1]*100:.1f}%')

for name, label in [('A','形态A: 阴后阳(回调反弹)'), ('B','形态B: 下破后站上(下破反弹)'), ('C','形态C: 暂停后阳(暂停反弹)')]:
    print(f'\n=== {label} ===')
    for dc, (cont, tot) in sorted(stats[name].items(), key=lambda x:-x[1][1]):
        if tot > 1000:
            print(f'  {dc}: n={tot}, 未来3日继续升管={cont/tot*100:.1f}%')
