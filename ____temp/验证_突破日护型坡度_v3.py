# -*- coding: utf-8 -*-
"""
验证：DXZC>0 突破日护型（己/甲/乙）→ 升势坡度（用涨幅/累计涨幅）
====================================================
宽哼JC(列24)封顶100且@5天为负，无法区分坡度。
改用更直接的"涨幅速度"指标：
  ① 5日/10日/20日累计涨幅（收/突破日收-1）
  ② 前5日平均单日涨幅
  ③ 20日内最大单日高幅
  ④ 冲高后急跌（峰值后回撤）

用户假设：
- 突破日护型=己 → 坡度陡 → 冲高后急跌
- 突破日护型=甲 → 正常升势
- 突破日护型=乙 → 平缓/反复震荡

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

WINDOW = 20

stats = defaultdict(lambda: {'cum5': [], 'cum10': [], 'cum20': [], 'avg5': [], 'maxhf': [], 'dd': []})
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
                    closes = []
                    zfs = []
                    hfs = []
                    for j in range(i, min(i + WINDOW, n)):
                        rj = data[j]
                        if len(rj) <= 6: break
                        c = to_f(rj[1]); zf = to_f(rj[5]); hf = to_f(rj[6])
                        if c is None: break
                        closes.append(c)
                        if zf is not None: zfs.append(zf)
                        if hf is not None: hfs.append(hf)
                    if len(closes) < 5: continue
                    # 累计涨幅
                    cum5 = (closes[4] - base_close) / base_close * 100
                    cum10 = (closes[9] - base_close) / base_close * 100 if len(closes) > 9 else (closes[-1] - base_close) / base_close * 100
                    cum20 = (closes[-1] - base_close) / base_close * 100
                    # 前5日平均涨幅
                    avg5 = sum(zfs[:5]) / len(zfs[:5]) if zfs[:5] else 0
                    # 最大单日高幅
                    maxhf = max(hfs) if hfs else 0
                    # 峰值后回撤（用收盘峰值）
                    peak_close = max(closes)
                    peak_idx = closes.index(peak_close)
                    min_after = min(closes[peak_idx:])
                    dd = (peak_close - min_after) / peak_close * 100 if peak_close else 0
                    s = stats[key]
                    s['cum5'].append(cum5); s['cum10'].append(cum10); s['cum20'].append(cum20)
                    s['avg5'].append(avg5); s['maxhf'].append(maxhf); s['dd'].append(dd)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

targets = ['己(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)']

def avg(lst): return sum(lst)/len(lst) if lst else 0

print('=' * 92)
print('DXZC>0 突破日护型 → 升势坡度（涨幅速度）')
print('=' * 92)
print(f'{"突破日护型":<12} {"n":>8} {"5日累计":>8} {"10日累计":>8} {"20日累计":>8} {"前5日均涨":>8} {"最大高幅":>8} {"峰值回撤":>8}')
print('-' * 92)
for k in targets:
    s = stats[k]
    if not s['cum5']: continue
    print(f'{k:<12} {len(s["cum5"]):>8,} {avg(s["cum5"]):>7.2f}% {avg(s["cum10"]):>7.2f}% {avg(s["cum20"]):>7.2f}% {avg(s["avg5"]):>7.2f}% {avg(s["maxhf"]):>7.2f}% {avg(s["dd"]):>7.2f}%')

print()
print('=' * 92)
print('5日累计涨幅 分布（坡度陡→5日涨得多）')
print('=' * 92)
bins = [(-999, -5), (-5, 0), (0, 5), (5, 10), (10, 20), (20, 999)]
print(f'{"突破日护型":<12} {"n":>8}', end='')
for lo, hi in bins:
    print(f' {"<"+str(hi):>8}', end='')
print()
print('-' * 92)
for k in targets:
    s = stats[k]
    if not s['cum5']: continue
    c5 = s['cum5']
    print(f'{k:<12} {len(c5):>8,}', end='')
    for lo, hi in bins:
        cnt = sum(1 for v in c5 if lo <= v < hi)
        print(f' {cnt/len(c5)*100:>7.1f}%', end='')
    print()
