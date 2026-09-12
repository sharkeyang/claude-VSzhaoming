# -*- coding: utf-8 -*-
"""
验证：DXZC>0 突破日护型（己/甲/乙）→ 升势坡度（修正版）
====================================================
宽哼JC(列24)封顶100，20日内最大宽哼JC会饱和，无法区分坡度。
改用"坡度速度"指标：
  ① 宽哼JC@第5天 / 第10天（早期偏离，坡度越陡越高）
  ② 达到宽哼JC=50%所需天数（坡度越陡越快）
  ③ 20日内最大宽哼JC（参考，会饱和）
  ④ 冲高后急跌（达到峰值后的回撤）

用户假设：
- 突破日护型=己 → 坡度陡 → 冲高后急跌
- 突破日护型=甲 → 正常升势
- 突破日护型=乙 → 平缓/反复震荡

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
THRESH = 50  # 达到50%宽哼JC的天数

# 突破日护型 -> 各指标列表
stats = defaultdict(lambda: {'jc5': [], 'jc10': [], 'days50': [], 'maxjc': [], 'dd': []})
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
                if len(row) <= 24: continue
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
                    # 窗口内各日宽哼JC
                    jc_vals = []
                    for j in range(i, min(i + WINDOW, n)):
                        rj = data[j]
                        if len(rj) <= 24: break
                        jc = to_f(rj[22])
                        if jc is None: break
                        jc_vals.append(jc)
                    if len(jc_vals) < 5: continue
                    # 第5天/第10天宽哼JC（索引4/9）
                    jc5 = jc_vals[4]
                    jc10 = jc_vals[9] if len(jc_vals) > 9 else jc_vals[-1]
                    # 达到50%的天数
                    days50 = None
                    for idx, v in enumerate(jc_vals):
                        if v >= THRESH:
                            days50 = idx + 1
                            break
                    # 最大宽哼JC
                    maxjc = max(jc_vals)
                    # 峰值后回撤
                    peak_idx = jc_vals.index(maxjc)
                    peak_close = to_f(data[i + peak_idx][1])
                    min_close = peak_close
                    for j in range(i + peak_idx + 1, min(i + WINDOW, n)):
                        c = to_f(data[j][1])
                        if c is not None and c < min_close:
                            min_close = c
                    dd = (peak_close - min_close) / peak_close * 100 if peak_close else 0
                    # 记录
                    s = stats[key]
                    s['jc5'].append(jc5)
                    s['jc10'].append(jc10)
                    if days50 is not None: s['days50'].append(days50)
                    s['maxjc'].append(maxjc)
                    s['dd'].append(dd)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

targets = ['己(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)']

def avg(lst): return sum(lst)/len(lst) if lst else 0
def med(lst):
    if not lst: return 0
    s = sorted(lst); return s[len(s)//2]

print('=' * 90)
print('DXZC>0 突破日护型 → 升势坡度（宽哼JC速度）')
print('=' * 90)
print(f'{"突破日护型":<12} {"n":>8} {"宽哼JC@5天":>10} {"@10天":>8} {"达50%天数":>8} {"最大宽哼JC":>10} {"峰值后回撤":>10}')
print('-' * 90)
for k in targets:
    s = stats[k]
    if not s['jc5']: continue
    print(f'{k:<12} {len(s["jc5"]):>8,} {avg(s["jc5"]):>9.1f}% {avg(s["jc10"]):>7.1f}% {avg(s["days50"]):>7.1f}天 {avg(s["maxjc"]):>9.1f}% {avg(s["dd"]):>9.2f}%')

print()
print('=' * 90)
print('宽哼JC@第5天 分布（坡度陡→第5天就高）')
print('=' * 90)
bins = [(0, 10), (10, 30), (30, 50), (50, 70), (70, 90), (90, 101)]
print(f'{"突破日护型":<12} {"n":>8}', end='')
for lo, hi in bins:
    print(f' {"<"+str(hi):>8}', end='')
print()
print('-' * 90)
for k in targets:
    s = stats[k]
    if not s['jc5']: continue
    jc5 = s['jc5']
    print(f'{k:<12} {len(jc5):>8,}', end='')
    for lo, hi in bins:
        cnt = sum(1 for v in jc5 if lo <= v < hi)
        print(f' {cnt/len(jc5)*100:>7.1f}%', end='')
    print()
