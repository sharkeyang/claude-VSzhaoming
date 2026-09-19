# -*- coding: utf-8 -*-
"""验证DXAB由负转正后的特权（健壮版）"""
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

files = []
skip = 0
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
                hx, dtab = parse_dxab(row[9])
                # 日ZE可能为空，用try
                try:
                    dze = int(row[15])
                except:
                    dze = 0
                def_ = row[17] if len(row) > 17 else ''
                frows.append((zf, dtza, hx, dtab, dze, def_))
            except (ValueError, IndexError):
                skip += 1
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}, 跳过: {skip}')

def is_orth(dtab):
    return dtab is not None and dtab > 0

def again_up(frows, i, la=3):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][1] > 0:
            return True
    return False

def not_neg(frows, i, la=3):
    for j in range(i+1, min(i+1+la, len(frows))):
        if not is_orth(frows[j][3]):
            return False
    return True

stats = {'全局': [0,0,0], 'DXZE>0': [0,0,0], 'DXZE>0且DXEF>0': [0,0,0]}

for frows in files:
    N = len(frows)
    for i in range(1, N-1):
        zf, dtza, hx, dtab, dze, def_ = frows[i]
        if not is_orth(dtab) or dtza <= 0 or zf >= 0:
            continue
        stats['全局'][0] += 1
        if again_up(frows, i): stats['全局'][1] += 1
        if not_neg(frows, i): stats['全局'][2] += 1
        if dze > 0:
            stats['DXZE>0'][0] += 1
            if again_up(frows, i): stats['DXZE>0'][1] += 1
            if not_neg(frows, i): stats['DXZE>0'][2] += 1
            if def_ and ('开' in def_ or '金' in def_ or '升' in def_):
                stats['DXZE>0且DXEF>0'][0] += 1
                if again_up(frows, i): stats['DXZE>0且DXEF>0'][1] += 1
                if not_neg(frows, i): stats['DXZE>0且DXEF>0'][2] += 1

print(f'\n=== DXAB正交后阴柱回调特权 ===')
for key in ['全局', 'DXZE>0', 'DXZE>0且DXEF>0']:
    tot, up, nn = stats[key]
    if tot:
        print(f'{key}: n={tot}, 未来3日再次上升={up/tot*100:.1f}%, 不马上负交={nn/tot*100:.1f}%')
