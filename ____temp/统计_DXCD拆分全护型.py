# -*- coding: utf-8 -*-
"""
按 DXCD 拆分：各 DXAB 护型的 个数/机会段/平均持续/行占比/段占比（全行，含DXZC<0）
====================================================
目的：展示 DXCD=上/忐/忠（DXZC>0）vs 中/下/忑（DXZC<0）的对比，
让用户看到限定 DXZC>0（上/忐/忠）区域是有意义的。

机会段（run）定义：连续 N 天 DXAB 护型相同 且 DXCD 相同 = 一次机会段。
  - 护型变化 或 DXCD 变化 都会中断当前机会段。
  - 每个机会段属于唯一 (护型, DXCD) 组合。
  - 平均持续 = 个数(行) / 机会段数。

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

# (key, dxcd) -> [rows, runs, days]
stats = defaultdict(lambda: [0, 0, 0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    cur_key = None
    cur_dxcd = None
    cur_len = 0
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                dxcd = row[8].strip()
                if za is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx:
                    if cur_key is not None:
                        stats[(cur_key, cur_dxcd)][1] += 1
                        stats[(cur_key, cur_dxcd)][2] += cur_len
                        cur_key = None; cur_dxcd = None; cur_len = 0
                    continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                stats[(key, dxcd)][0] += 1
                if key == cur_key and dxcd == cur_dxcd:
                    cur_len += 1
                else:
                    if cur_key is not None:
                        stats[(cur_key, cur_dxcd)][1] += 1
                        stats[(cur_key, cur_dxcd)][2] += cur_len
                    cur_key = key
                    cur_dxcd = dxcd
                    cur_len = 1
            if cur_key is not None:
                stats[(cur_key, cur_dxcd)][1] += 1
                stats[(cur_key, cur_dxcd)][2] += cur_len
                cur_key = None; cur_dxcd = None; cur_len = 0
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

all_types = ['甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)', '丁(ZA<0)', '戊(ZA>0)', '戊(ZA<0)', '己(ZA>0)']
dxcds = ['上', '忐', '忠', '中', '忑', '下']

# 每DXCD合计（用于占比）
dxcd_tot_rows = defaultdict(int)
dxcd_tot_runs = defaultdict(int)
for (k, d), (rows, runs, days) in stats.items():
    dxcd_tot_rows[d] += rows
    dxcd_tot_runs[d] += runs

for dxcd in dxcds:
    print('=' * 78)
    print(f'DXCD={dxcd}  （{"DXZC>0" if dxcd in ("上","忐","忠") else "DXZC<0"}）')
    print('=' * 78)
    tot_rows = dxcd_tot_rows[dxcd]
    tot_runs = dxcd_tot_runs[dxcd]
    print(f'{"护型":<12} {"个数(行)":>10} {"机会段":>9} {"平均持续":>8} {"行占比":>8} {"段占比":>8}')
    print('-' * 62)
    # 按平均持续排序
    rows_with_data = [(k, stats[(k, dxcd)]) for k in all_types if stats[(k, dxcd)][0] > 0]
    rows_with_data.sort(key=lambda x: (x[1][0]/x[1][1] if x[1][1] else 0), reverse=True)
    for k, (rows, runs, days) in rows_with_data:
        avg = days / runs if runs else 0
        print(f'{k:<12} {rows:>10,} {runs:>9,} {avg:>7.1f}天 {rows/tot_rows*100:>7.2f}% {runs/tot_runs*100:>7.2f}%')
    print('-' * 62)
    print(f'{"合计":<12} {tot_rows:>10,} {tot_runs:>9,} {"":>8} {100:>7.2f}% {100:>7.2f}%')
    print()
