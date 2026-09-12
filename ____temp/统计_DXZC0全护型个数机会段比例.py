# -*- coding: utf-8 -*-
"""
DXZC>0 时各 DXAB 护型（全护型，含丁/戊ZA<0，乙拆分）的 个数/机会段/比例
====================================================
机会段（run）定义：连续 N 天 DXZC>0 且 DXAB 护型相同 = 一次机会段。
  - 护型变化（如甲→乙）或 DXZC<=0 都会中断当前机会段。
  - 一个机会段内包含多个"样本"（行），即该护型持续期间每天 DXZC>0 都算一个样本。
  - 平均持续 = 个数(行) / 机会段数 = 每个机会段平均横跨多少天（持续性指标）。

输出：
  ① 全护型总表（个数/机会段/平均持续/占比）
  ② 按持续性排名
  ③ 按 DXCD 拆分（个数/机会段/平均持续）

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池板块映射
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

# 行计数: key -> n
row_cnt = defaultdict(int)
# 机会段计数: key -> n
run_cnt = defaultdict(int)
# 平均持续: key -> 累计天数
run_days = defaultdict(int)
# 按DXCD: (key, dxcd) -> [rows, runs, days]
dxcd_stats = defaultdict(lambda: [0, 0, 0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    cur_key = None
    cur_len = 0
    cur_dxcd = None
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                dxcd = row[8].strip()
                if zc is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx:
                    if cur_key is not None:
                        run_cnt[cur_key] += 1
                        run_days[cur_key] += cur_len
                        dxcd_stats[(cur_key, cur_dxcd)][1] += 1
                        dxcd_stats[(cur_key, cur_dxcd)][2] += cur_len
                        cur_key = None; cur_len = 0; cur_dxcd = None
                    continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                if zc > 0:
                    row_cnt[key] += 1
                    if key == cur_key:
                        cur_len += 1
                    else:
                        if cur_key is not None:
                            run_cnt[cur_key] += 1
                            run_days[cur_key] += cur_len
                            dxcd_stats[(cur_key, cur_dxcd)][1] += 1
                            dxcd_stats[(cur_key, cur_dxcd)][2] += cur_len
                        cur_key = key
                        cur_len = 1
                        cur_dxcd = dxcd
                    dxcd_stats[(key, dxcd)][0] += 1
                else:
                    if cur_key is not None:
                        run_cnt[cur_key] += 1
                        run_days[cur_key] += cur_len
                        dxcd_stats[(cur_key, cur_dxcd)][1] += 1
                        dxcd_stats[(cur_key, cur_dxcd)][2] += cur_len
                        cur_key = None; cur_len = 0; cur_dxcd = None
            if cur_key is not None:
                run_cnt[cur_key] += 1
                run_days[cur_key] += cur_len
                dxcd_stats[(cur_key, cur_dxcd)][1] += 1
                dxcd_stats[(cur_key, cur_dxcd)][2] += cur_len
                cur_key = None; cur_len = 0; cur_dxcd = None
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# 全护型（含丁/戊ZA<0，乙拆分）
all_types = ['甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)', '己(ZA>0)']

tot_rows = sum(row_cnt[k] for k in all_types)
tot_runs = sum(run_cnt[k] for k in all_types)

print('=' * 78)
print('① DXZC>0 全护型总表（个数/机会段/平均持续/占比）')
print('=' * 78)
print(f'{"护型":<12} {"个数(行)":>12} {"机会段":>10} {"平均持续":>8} {"行占比":>8} {"段占比":>8}')
print('-' * 78)
for k in all_types:
    rows = row_cnt[k]
    runs = run_cnt[k]
    avg = rows / runs if runs else 0
    print(f'{k:<12} {rows:>12,} {runs:>10,} {avg:>7.1f}天 {rows/tot_rows*100:>7.2f}% {runs/tot_runs*100:>7.2f}%')
print('-' * 78)
print(f'{"合计":<12} {tot_rows:>12,} {tot_runs:>10,} {"":>8} {100:>7.2f}% {100:>7.2f}%')

print()
print('=' * 78)
print('② 按持续性排名（平均持续 = 个数/机会段，越大越持久）')
print('=' * 78)
ranked = sorted(all_types, key=lambda k: (row_cnt[k]/run_cnt[k] if run_cnt[k] else 0), reverse=True)
print(f'{"排名":<4} {"护型":<12} {"平均持续":>8} {"个数":>10} {"机会段":>10} {"行占比":>8} {"段占比":>8}')
print('-' * 66)
for i, k in enumerate(ranked, 1):
    rows = row_cnt[k]; runs = run_cnt[k]
    avg = rows / runs if runs else 0
    print(f'{i:<4} {k:<12} {avg:>7.1f}天 {rows:>10,} {runs:>10,} {rows/tot_rows*100:>7.2f}% {runs/tot_runs*100:>7.2f}%')

print()
print('=' * 78)
print('③ 按 DXCD 拆分（DXZC>0，各护型 个数/机会段/平均持续）')
print('=' * 78)
for dxcd in ['上', '忐', '忠', '中', '忑', '下']:
    print(f'\n--- DXCD={dxcd} ---')
    print(f'{"护型":<12} {"个数(行)":>10} {"机会段":>9} {"平均持续":>8}')
    print('-' * 45)
    for k in all_types:
        rows, runs, days = dxcd_stats[(k, dxcd)]
        if rows == 0: continue
        avg = days / runs if runs else 0
        print(f'{k:<12} {rows:>10,} {runs:>9,} {avg:>7.1f}天')
