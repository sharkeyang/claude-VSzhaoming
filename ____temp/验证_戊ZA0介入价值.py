# -*- coding: utf-8 -*-
"""
DXZC>0 时 戊(ZA>0) 是否值得介入
====================================================
输出：
  ① 各护型 P(≥3%)（DXZC>0）——对比戊(ZA>0) vs 基线/甲/乙
  ② 戊(ZA>0) 次日转移方向（DXZC>0）
  ③ 戊(ZA>0) 持续性（机会段/平均持续）

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅
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

# 当前行统计(DXZC>0): key -> [n, hr3, sum_hr]
cur = defaultdict(lambda: [0, 0, 0.0])
# 次日转移(DXZC>0): (cur_key, nxt_key) -> count
trans = defaultdict(int)
# 机会段
run_cnt = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_key = None
    cur_key = None
    cur_len = 0
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                hr = to_f(row[26])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                if zc > 0:
                    cur[key][0] += 1
                    cur[key][1] += (1 if hr >= 3 else 0)
                    cur[key][2] += hr
                    # 机会段
                    if key == cur_key:
                        cur_len += 1
                    else:
                        if cur_key is not None:
                            run_cnt[cur_key] += 1
                        cur_key = key
                        cur_len = 1
                    # 次日转移
                    if prev_key is not None:
                        trans[(prev_key, key)] += 1
                else:
                    if cur_key is not None:
                        run_cnt[cur_key] += 1
                        cur_key = None; cur_len = 0
                prev_key = key
            if cur_key is not None:
                run_cnt[cur_key] += 1
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

targets = ['戊(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '己(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA<0)']

print('=' * 70)
print('① 各护型 P(≥3%)（DXZC>0）')
print('=' * 70)
print(f'{"护型":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"机会段":>9} {"平均持续":>8}')
print('-' * 65)
for k in targets:
    s = cur[k]
    if s[0] == 0: continue
    runs = run_cnt[k]
    avg = s[0]/runs if runs else 0
    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {runs:>9,} {avg:>7.1f}天')

print()
print('=' * 70)
print('② 戊(ZA>0) 次日转移方向（DXZC>0）')
print('=' * 70)
k = '戊(ZA>0)'
all_t = {nk: c for (ck, nk), c in trans.items() if ck == k}
tot = sum(all_t.values())
for nk, c in sorted(all_t.items(), key=lambda x: -x[1]):
    print(f'  {nk:<12} {c:>10,}  {c/tot*100:>6.2f}%')
