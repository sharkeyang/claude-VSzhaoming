# -*- coding: utf-8 -*-
"""
DJC丘生命周期（重跑版，2026-09-13）
====================================================
补 DXZB>0 和其他护型（不只甲）。
DXZB = 价格 vs EMA12（DJB），从收盘价[1] 计算 EMA12。
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def parse_dxab_val(dxab):
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    return int(m.group(1)) if m else None

def ema12(prices):
    """计算 EMA12 序列"""
    if not prices: return []
    k = 2/13
    ema = [prices[0]]
    for p in prices[1:]:
        ema.append(p*k + ema[-1]*(1-k))
    return ema

# 统计容器
# q4: 阶段 -> [n, DXAB>0, DXZA>0, DXZB>0, 甲,乙,己,戊,丙,丁]
q4 = defaultdict(lambda: [0]*10)

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    # 计算 EMA12
    prices = []
    for row in rows:
        p = to_f(row[1]) if len(row)>1 else None
        prices.append(p if p is not None else 0)
    emas = ema12(prices)

    # DJC丘生命周期：找DXZC>0连续区域，按位置分段
    i = 0
    while i < n:
        zc = to_f(rows[i][14]) if len(rows[i])>14 else None
        if zc is None or zc <= 0:
            i += 1; continue
        start = i
        while i < n:
            zc2 = to_f(rows[i][14]) if len(rows[i])>14 else None
            if zc2 is None or zc2 <= 0: break
            i += 1
        end = i
        length = end - start
        if length < 5: continue
        for j in range(start, end):
            pos = (j - start) / length
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            dxab = rows[j][9].strip() if len(rows[j])>9 else ''
            hx = parse_hx(dxab)
            btab = parse_dxab_val(dxab)
            # DXZB>0: 收盘价 > EMA12
            close = to_f(rows[j][1]) if len(rows[j])>1 else None
            dxzb_pos = (close is not None and emas[j] is not None and close > emas[j])
            if pos < 0.1: stage = '首(0-10%)'
            elif pos < 0.3: stage = '初(10-30%)'
            elif pos < 0.7: stage = '中(30-70%)'
            elif pos < 0.9: stage = '顶(70-90%)'
            else: stage = '尾(90-100%)'
            q4[stage][0]+=1
            if btab is not None and btab > 0: q4[stage][1]+=1
            if za is not None and za > 0: q4[stage][2]+=1
            if dxzb_pos: q4[stage][3]+=1
            hx_idx = {'甲':4,'乙':5,'己':6,'戊':7,'丙':8,'丁':9}.get(hx)
            if hx_idx is not None: q4[stage][hx_idx]+=1

print(f'高波池文件: {files_core}')
print()
print('='*80)
print('【4】DJC丘生命周期各阶段状态（重跑版，补DXZB>0+全护型）')
print('='*80)
print(f'{"阶段":<12} {"n":>10} {"DXAB>0":>8} {"DXZA>0":>8} {"DXZB>0":>8} {"甲":>7} {"乙":>7} {"己":>7} {"戊":>7} {"丙":>7} {"丁":>7}')
print('-'*90)
for stage in ['首(0-10%)','初(10-30%)','中(30-70%)','顶(70-90%)','尾(90-100%)']:
    if stage in q4:
        s = q4[stage]
        if s[0] >= 100:
            print(f'{stage:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]*100:>7.2f}% {s[3]/s[0]*100:>7.2f}% '
                  f'{s[4]/s[0]*100:>6.1f}% {s[5]/s[0]*100:>6.1f}% {s[6]/s[0]*100:>6.1f}% {s[7]/s[0]*100:>6.1f}% {s[8]/s[0]*100:>6.1f}% {s[9]/s[0]*100:>6.1f}%')
print()
