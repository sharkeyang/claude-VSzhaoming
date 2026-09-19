# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

def parse_ding(s):
    if not s: return None, None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 44: continue
            try:
                zf = float(row[5]); dtza = int(row[13])
                hx = row[9][1] if len(row[9])>1 else None
                dc = parse_ding(row[43])[1]
                zp = row[10]
                bf = row[34].strip(); last = bf[-1] if bf else ''
                frows.append((zf, dtza, hx, dc, zp, last))
            except: continue
    files.append(frows)

# 调试：统计各条件命中数
n_total=0; n_hx=0; n_dtza=0; n_zf=0; n_cb=0
for frows in files:
    N=len(frows)
    for i in range(1, N-1):
        zf, dtza, hx, dc, zp, last = frows[i]
        n_total+=1
        if hx=='甲': n_hx+=1
        if hx=='甲' and dtza>0: n_dtza+=1
        if hx=='甲' and dtza>0 and zf>0: n_zf+=1
        if hx=='甲' and dtza>0 and zf>0:
            cb=None
            for k in range(i-1, max(i-6,-1), -1):
                if frows[k][1]<0: cb='下破'; break
                if frows[k][0]<0: cb='阴柱'; break
            if cb: n_cb+=1
print(f'总样本: {n_total}')
print(f'甲护型: {n_hx}')
print(f'甲+升管: {n_dtza}')
print(f'甲+升管+阳柱: {n_zf}')
print(f'甲+升管+阳柱+回调: {n_cb}')
