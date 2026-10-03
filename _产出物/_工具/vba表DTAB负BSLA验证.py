# -*- coding: utf-8 -*-
"""
验证：DTAB<0 时按 DTAB 真实值分段，看 BSLA（最低偏离）与 BSHA（最高偏离）
====================================================
用户要求（2026-09-30）：
1. 持续天数改为负值，用 DTAB 真实值（DTAB<0 表示 JA<JB 负交已持续天数）
2. DTAB<0 时应讨论 BSLA（最低偏离），而非 BSHA（最高偏离）——负交期间 BSHA 无意义

列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_日类.md）：
    [19] BSHA（最高偏离）
    [26] 次日高幅
    [38] BSLA（最低偏离）
    [64] DTAB（JA vs JB 交叉天数，2026-09-24 新增）
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

OUT_CSV = '____temp/DTAB负BSLA验证结果.csv'

# 高波池板块
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# 统计: (DTAB段) -> [样本, BSLA和, BSHA和, P(次日HR>=3%), HR和]
stats = defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0])

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    for i in range(len(rows) - 1):
        row = rows[i]; nxt = rows[i + 1]
        if len(row) <= 64 or len(nxt) <= 26: continue
        dtab = to_f(row[64])
        bsla = to_f(row[38])
        bsha = to_f(row[19])
        nxt_hr = to_f(nxt[26])
        if dtab is None or bsla is None or bsha is None or nxt_hr is None: continue
        # 只看 DTAB<0（负交期间）
        if dtab >= 0: continue
        if dtab >= -5: bucket = 'DTAB -1~-5'
        elif dtab >= -10: bucket = 'DTAB -6~-10'
        elif dtab >= -15: bucket = 'DTAB -11~-15'
        elif dtab >= -20: bucket = 'DTAB -16~-20'
        elif dtab >= -30: bucket = 'DTAB -21~-30'
        else: bucket = 'DTAB <-30'
        s = stats[bucket]
        s[0] += 1
        s[1] += bsla
        s[2] += bsha
        if nxt_hr >= 3: s[3] += 1
        s[4] += nxt_hr

print(f'高波池文件: {files_core}')
print()
print('DTAB<0 时按DTAB真实值分段，看BSLA（最低偏离）与BSHA（最高偏离）')
print(f'{"DTAB段":<14}{"样本":>10}{"平均BSLA":>10}{"平均BSHA":>10}{"P(次日HR>=3%)":>16}{"均高幅":>8}')
print('-' * 70)
buckets = ['DTAB -1~-5', 'DTAB -6~-10', 'DTAB -11~-15', 'DTAB -16~-20', 'DTAB -21~-30', 'DTAB <-30']
for b in buckets:
    n, bsla_s, bsha_s, hit, hr_s = stats[b]
    if n == 0: continue
    print(f'{b:<14}{n:>10,}{bsla_s/n:>10.2f}{bsha_s/n:>10.2f}{hit/n*100:>15.2f}%{hr_s/n:>7.2f}%')

# 写 CSV
with open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['DTAB段', '样本', '平均BSLA', '平均BSHA', 'P(次日HR>=3%)', '均高幅'])
    for b in buckets:
        n, bsla_s, bsha_s, hit, hr_s = stats[b]
        if n == 0: continue
        w.writerow([b, n, f'{bsla_s/n:.2f}', f'{bsha_s/n:.2f}', f'{hit/n*100:.2f}%', f'{hr_s/n:.2f}%'])
print(f'\n结果已写入: {OUT_CSV}')
