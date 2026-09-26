# -*- coding: utf-8 -*-
"""升管(DXZA>0) 管宽分类 分布统计（用户纠正口径 2026-09-20）
统计：窄管/扩管/平管 分布比例 + 管宽哼JA 值分布 + 等型分布
列映射(实际数据验证,勿信表头)：
col10=护型DXAB, col11=柱排, col14=日ZA, col22=管宽哼JA,
col27=次日高幅, col31=上符串(触顶A), col43=等型(BT连阳)
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
import random
LIMIT = int(os.environ.get('FILE_LIMIT', '0'))
if LIMIT:
    random.seed(1)
    files = random.sample(files, LIMIT)
print(f'共 {len(files)} 个文件', flush=True)

# 分布统计
dist = defaultdict(int)          # 管宽分类分布
gk_hist = defaultdict(int)       # 管宽哼JA 值分布
deng_dist = defaultdict(int)     # 等型分布
hx_dist = defaultdict(int)       # 护型分布
cross = defaultdict(int)         # 管宽分类 × 等型
cross_hx = defaultdict(int)      # 管宽分类 × 护型

def classify(gkv, touch, shengpai):
    if 0 < gkv < 5:
        return '窄管'
    elif gkv >= 5:
        return '扩管' if (touch and shengpai) else '平管'
    else:
        return '管宽<=0'

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 44: continue
            try:
                za = float(row[13])
                gk = row[21].strip()
                nh = float(row[26])
                sf = row[30]
                zp = row[10]
                deng = row[42].strip()
                hx = row[9].strip()
            except:
                continue
            if za <= 0: continue  # 只统计升管 DXZA>0
            h = hx[0] if hx else ''
            if h not in ('a','b','r'): continue  # 升管 = 甲乙己（用户确认：只有甲乙己才能定义升管）
            touch = 'A' in sf
            shengpai = zp.startswith('升.')
            # 等型
            try: dv = int(deng)
            except: dv = None
            if dv is None: d = '等其他'
            elif dv == 1: d = '等1'
            elif dv == 2: d = '等2'
            elif dv >= 3: d = '等3'
            elif dv == -1: d = '等5'
            elif dv == -2: d = '等6'
            elif dv <= -3: d = '等7'
            else: d = '等其他'
            # 护型首字符
            h = hx[0] if hx else ''
            if gk == '':
                cls = '管宽空'
            else:
                gkv = float(gk)
                cls = classify(gkv, touch, shengpai)
                # 管宽哼JA 值分布
                if gkv < 5: gk_hist['0-5'] += 1
                elif gkv < 10: gk_hist['5-10'] += 1
                elif gkv < 20: gk_hist['10-20'] += 1
                elif gkv < 30: gk_hist['20-30'] += 1
                elif gkv < 60: gk_hist['30-60'] += 1
                else: gk_hist['60+'] += 1
            dist[cls] += 1
            deng_dist[d] += 1
            if h: hx_dist[h] += 1
            cross[(cls, d)] += 1
            cross_hx[(cls, h)] += 1

total = sum(dist.values())
print(f'\n=== 升管(DXZA>0) 管宽分类 分布 ===')
print(f'总样本: {total}')
for k in ['窄管','扩管','平管','管宽<=0','管宽空']:
    if dist[k]:
        print(f'  {k}: n={dist[k]}, 占比={dist[k]/total*100:.2f}%')

print(f'\n=== 管宽哼JA 值分布 ===')
for k in ['0-5','5-10','10-20','20-30','30-60','60+']:
    if gk_hist[k]:
        print(f'  {k}: n={gk_hist[k]}, 占比={gk_hist[k]/total*100:.2f}%')

print(f'\n=== 升管 等型分布 ===')
for k in ['等1','等2','等3','等5','等6','等7','等其他']:
    if deng_dist[k]:
        print(f'  {k}: n={deng_dist[k]}, 占比={deng_dist[k]/total*100:.2f}%')

print(f'\n=== 升管 护型分布 ===')
for k in sorted(hx_dist):
    print(f'  {k}: n={hx_dist[k]}, 占比={hx_dist[k]/total*100:.2f}%')

print(f'\n=== 管宽分类 × 等型 分布 ===')
for cls in ['窄管','扩管','平管','管宽<=0','管宽空']:
    row = []
    for d in ['等1','等2','等3','等5','等6','等7','等其他']:
        if cross[(cls,d)]:
            row.append(f'{d}:{cross[(cls,d)]/total*100:.2f}%')
    if row:
        print(f'  {cls}: ' + ', '.join(row))

print(f'\n=== 管宽分类 × 护型 分布 ===')
for cls in ['窄管','扩管','平管','管宽<=0','管宽空']:
    row = []
    for h in sorted(hx_dist):
        if cross_hx[(cls,h)]:
            row.append(f'{h}:{cross_hx[(cls,h)]/total*100:.2f}%')
    if row:
        print(f'  {cls}: ' + ', '.join(row))