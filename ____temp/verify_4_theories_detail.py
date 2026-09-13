# -*- coding: utf-8 -*-
"""
补充分析（单次遍历）：验证1(DTAB分档) + 验证2(基顶型细分) + 验证3(帐篷细分)
"""
import csv, glob, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_dxab(s):
    if not s or len(s) < 2:
        return None, None
    hx = s[1]
    m = re.search(r'(\d+)', s[3:])
    dt = int(m.group(1)) if m else None
    return hx, dt

def parse_ding(s):
    if not s:
        return None, None
    if s[0] in ('K', 'L'):
        return s[0], s[1:]
    if s[0] == '_':
        return 'G', s[1:]
    return 'G', s

# 单次遍历加载
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
                frows.append((float(row[5]), int(row[13]),
                              row[9][1] if len(row[9])>1 else None,
                              parse_dxab(row[9])[1],
                              parse_ding(row[43])[0], parse_ding(row[43])[1]))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total_rows = sum(len(f) for f in files)
print(f'总行数: {total_rows}')

def rest(frows, i, la=5):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][1] > 0:
            return True
    return False

def cont_up(frows, i, la=3):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][1] <= 0:
            return False
    return True

# 验证1: DTAB分档
bins = [(0,5),(5,10),(10,15),(15,20),(20,30),(30,999)]
v1b = {f'{a}-{b}': [0,0] for a,b in bins}
# 验证2: 基顶型细分
v2d = collections.defaultdict(lambda: [0,0])
# 验证3: 帐篷细分
v3d = collections.defaultdict(lambda: [0,0])
v3 = {'tent':[0,0], 'notent':[0,0]}

for frows in files:
    N = len(frows)
    for i in range(N-1):
        zf, dtza, hx, dtab, dstate, dcore = frows[i]
        # 验证1
        if dtza in (-1,-2) and dtab is not None:
            for a,b in bins:
                if a <= dtab < b:
                    key = f'{a}-{b}'
                    v1b[key][1] += 1
                    if rest(frows, i): v1b[key][0] += 1
                    break
        # 验证2
        if dtza in (-1,-2) and dstate=='G':
            v2d[dcore][1] += 1
            if rest(frows, i): v2d[dcore][0] += 1
        # 验证3
        if i >= 1:
            pzf, pdtza, phx, pdtab, pdstate, pdcore = frows[i-1]
            if hx=='甲' and dtza>0 and zf>0 and pzf<0:
                is_tent = (dstate=='G')
                key = 'tent' if is_tent else 'notent'
                v3[key][1] += 1
                if cont_up(frows, i): v3[key][0] += 1
                if is_tent:
                    v3d[dcore][1] += 1
                    if cont_up(frows, i): v3d[dcore][0] += 1

print('\n=== 验证1: DTAB分档（下破DTZA=-1/-2）===')
for k,(restn,tot) in v1b.items():
    if tot:
        print(f'DTAB {k}: n={tot}, 5日重新站上DJA={restn/tot*100:.1f}%')

print('\n=== 验证2: 顶态G各核心顶型（下破DTZA=-1/-2）===')
for k,(restn,tot) in sorted(v2d.items(), key=lambda x:-x[1][1]):
    if tot > 1000:
        print(f'顶态G {k}: n={tot}, 5日重新站上DJA={restn/tot*100:.1f}%')

print('\n=== 验证3: 帐篷=升管 ===')
if v3['tent'][1]:
    print(f'帐篷(触顶): n={v3["tent"][1]}, 未来3日继续升管={v3["tent"][0]/v3["tent"][1]*100:.1f}%')
if v3['notent'][1]:
    print(f'非帐篷(未触顶): n={v3["notent"][1]}, 未来3日继续升管={v3["notent"][0]/v3["notent"][1]*100:.1f}%')
print('帐篷细分(触顶核心顶型):')
for k,(cont,tot) in sorted(v3d.items(), key=lambda x:-x[1][1]):
    if tot > 1000:
        print(f'  {k}: n={tot}, 未来3日继续升管={cont/tot*100:.1f}%')
