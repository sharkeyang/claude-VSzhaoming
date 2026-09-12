# -*- coding: utf-8 -*-
"""
验证：DXZC>0 突破日护型（己/甲/乙）→ 升势坡度（20日内最大宽哼JC）
====================================================
用户假设：
- 突破日护型=己 → 坡度陡 → 冲高后急跌
- 突破日护型=甲 → DXZC<0时已完成DXAB正交 → 正常升势
- 突破日护型=乙 → DXZC<0时已完成正交但经历DXZA劫 → 平缓/反复震荡

衡量：突破DXZC>0后20日内（含突破日）较日ZC的最大偏离 = 20日内最大宽哼JC(列24, 向上)
另测：冲高后急跌（达到最大宽哼JC后的回撤）

磁盘CSV列序：1=收, 9=DXAB, 13=日ZA, 14=日ZC, 22=宽哼JC
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

# 突破日护型 -> [n, max宽哼JC列表, 急跌列表, 峰值后回撤列表]
# 急跌 = 达到最大宽哼JC后，剩余窗口内最大回撤(峰值收->最低收)/峰值收
stats = defaultdict(lambda: {'n': 0, 'maxjc': [], 'drawdown': []})
# 各护型突破次数
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
            header = rows[0]
            data = rows[1:]
            n = len(data)
            for i in range(n):
                row = data[i]
                if len(row) <= 24: continue
                zc = to_f(row[14])
                if zc is None: continue
                # 突破日：前一日ZC<=0 且 当日ZC>0
                prev_zc = to_f(data[i-1][14]) if i > 0 else None
                if zc > 0 and (prev_zc is None or prev_zc <= 0):
                    # 突破日护型
                    dxab = row[9].strip()
                    hx = 护型映射.get(dxab[0], '') if dxab else ''
                    if not hx: continue
                    za = to_f(row[13])
                    za_key = 'ZA>0' if (za or 0) > 0 else ('ZA=0' if (za or 0) == 0 else 'ZA<0')
                    key = f'{hx}({za_key})'
                    breakout_cnt[key] += 1
                    # 20日窗口（含突破日）
                    maxjc = 0.0
                    peak_close = None
                    peak_idx = i
                    for j in range(i, min(i + WINDOW, n)):
                        rj = data[j]
                        if len(rj) <= 24: break
                        jc = to_f(rj[22])
                        if jc is not None and jc > maxjc:
                            maxjc = jc
                            peak_close = to_f(rj[1])
                            peak_idx = j
                    if maxjc > 0 and peak_close:
                        # 峰值后回撤（急跌）
                        min_close = peak_close
                        for j in range(peak_idx + 1, min(i + WINDOW, n)):
                            rj = data[j]
                            if len(rj) <= 1: break
                            c = to_f(rj[1])
                            if c is not None and c < min_close:
                                min_close = c
                        drawdown = (peak_close - min_close) / peak_close * 100
                        stats[key]['n'] += 1
                        stats[key]['maxjc'].append(maxjc)
                        stats[key]['drawdown'].append(drawdown)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# 目标护型
targets = ['己(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)']

print('=' * 78)
print('DXZC>0 突破日护型 → 20日内最大宽哼JC（坡度）')
print('=' * 78)
print(f'{"突破日护型":<12} {"突破次数":>8} {"有效样本":>8} {"平均最大宽哼JC":>12} {"中位":>6} {"平均峰值后回撤":>12}')
print('-' * 78)
for k in targets:
    s = stats[k]
    if s['n'] == 0: continue
    mj = s['maxjc']
    dd = s['drawdown']
    avg = sum(mj)/len(mj)
    med = sorted(mj)[len(mj)//2]
    avg_dd = sum(dd)/len(dd)
    print(f'{k:<12} {breakout_cnt[k]:>8,} {s["n"]:>8,} {avg:>11.2f}% {med:>5.1f}% {avg_dd:>11.2f}%')

print()
print('=' * 78)
print('按坡度分组：最大宽哼JC 分布（突破日护型）')
print('=' * 78)
bins = [(0, 5), (5, 10), (10, 20), (20, 40), (40, 100), (100, 999)]
print(f'{"突破日护型":<12} {"n":>8}', end='')
for lo, hi in bins:
    print(f' {"<"+str(hi):>8}', end='')
print()
print('-' * 78)
for k in targets:
    s = stats[k]
    if s['n'] == 0: continue
    mj = s['maxjc']
    print(f'{k:<12} {s["n"]:>8,}', end='')
    for lo, hi in bins:
        cnt = sum(1 for v in mj if lo <= v < hi)
        print(f' {cnt/s["n"]*100:>7.1f}%', end='')
    print()
