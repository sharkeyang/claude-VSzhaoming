# -*- coding: utf-8 -*-
"""
验证：己 的"坡度陡"是否发生在极早期（1-3天）
====================================================
用户假设：突破日护型=己 → 角度坡度较陡 → 冲高后急跌。
首验发现己 5日累计最低(0.53%)，坡度陡不成立。
本脚本测更短时间窗：1/2/3日累计涨幅 + 最大单日高幅，看己是否在极早期冲高。

磁盘CSV列序：1=收, 5=涨幅, 6=高幅, 9=DXAB, 13=日ZA, 14=日ZC
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

stats = defaultdict(lambda: {'cum1': [], 'cum2': [], 'cum3': [], 'maxhf1': [], 'maxhf3': [], 'zf1': [], 'zf2': [], 'zf3': []})
breakout_cnt = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            rows = list(csv.reader(f))
            data = rows[1:]
            n = len(data)
            for i in range(n):
                row = data[i]
                if len(row) <= 14: continue
                zc = to_f(row[14])
                if zc is None: continue
                prev_zc = to_f(data[i-1][14]) if i > 0 else None
                if zc > 0 and (prev_zc is None or prev_zc <= 0):
                    dxab = row[9].strip()
                    hx = 护型映射.get(dxab[0], '') if dxab else ''
                    if not hx: continue
                    za = to_f(row[13])
                    za_key = 'ZA>0' if (za or 0) > 0 else ('ZA=0' if (za or 0) == 0 else 'ZA<0')
                    key = f'{hx}({za_key})'
                    breakout_cnt[key] += 1
                    base_close = to_f(row[1])
                    if not base_close: continue
                    # 收集窗口内收盘、涨幅、高幅
                    closes = [base_close]
                    zfs = []
                    hfs = []
                    for j in range(i + 1, min(i + 4, n)):
                        rj = data[j]
                        if len(rj) <= 6: break
                        c = to_f(rj[1]); zf = to_f(rj[5]); hf = to_f(rj[6])
                        if c is None: break
                        closes.append(c)
                        if zf is not None: zfs.append(zf)
                        if hf is not None: hfs.append(hf)
                    if len(closes) < 2: continue
                    # 1/2/3日累计涨幅
                    cum1 = (closes[1] - base_close) / base_close * 100
                    cum2 = (closes[2] - base_close) / base_close * 100 if len(closes) > 2 else cum1
                    cum3 = (closes[3] - base_close) / base_close * 100 if len(closes) > 3 else cum2
                    # 突破日当天涨幅（zf1是突破日后一天）
                    zf1 = zfs[0] if zfs else 0
                    zf2 = zfs[1] if len(zfs) > 1 else 0
                    zf3 = zfs[2] if len(zfs) > 2 else 0
                    # 最大单日高幅（突破日+后2天）
                    maxhf3 = max(hfs) if hfs else 0
                    s = stats[key]
                    s['cum1'].append(cum1); s['cum2'].append(cum2); s['cum3'].append(cum3)
                    s['zf1'].append(zf1); s['zf2'].append(zf2); s['zf3'].append(zf3)
                    s['maxhf3'].append(maxhf3)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

targets = ['己(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)']

def avg(lst): return sum(lst)/len(lst) if lst else 0

print('=' * 92)
print('DXZC>0 突破日护型 → 极早期冲高（1-3天）')
print('=' * 92)
print(f'{"突破日护型":<12} {"n":>8} {"1日累计":>8} {"2日累计":>8} {"3日累计":>8} {"次日涨":>7} {"第2日涨":>7} {"第3日涨":>7} {"3日最大高幅":>10}')
print('-' * 92)
for k in targets:
    s = stats[k]
    if not s['cum1']: continue
    print(f'{k:<12} {len(s["cum1"]):>8,} {avg(s["cum1"]):>7.2f}% {avg(s["cum2"]):>7.2f}% {avg(s["cum3"]):>7.2f}% {avg(s["zf1"]):>6.2f}% {avg(s["zf2"]):>6.2f}% {avg(s["zf3"]):>6.2f}% {avg(s["maxhf3"]):>9.2f}%')

print()
print('=' * 92)
print('次日涨幅 分布（坡度陡→次日涨得多）')
print('=' * 92)
bins = [(-999, -3), (-3, 0), (0, 3), (3, 6), (6, 10), (10, 999)]
print(f'{"突破日护型":<12} {"n":>8}', end='')
for lo, hi in bins:
    print(f' {"<"+str(hi):>8}', end='')
print()
print('-' * 92)
for k in targets:
    s = stats[k]
    if not s['zf1']: continue
    z1 = s['zf1']
    print(f'{k:<12} {len(z1):>8,}', end='')
    for lo, hi in bins:
        cnt = sum(1 for v in z1 if lo <= v < hi)
        print(f' {cnt/len(z1)*100:>7.1f}%', end='')
    print()
