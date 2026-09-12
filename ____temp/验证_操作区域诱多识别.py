# -*- coding: utf-8 -*-
"""
操作区域内 诱多/转坏 信号识别
====================================================
操作区域：DXCD=上/忐 + 甲/乙ZA>0/己/乙ZA<0
诱多信号：区域内 P(≥3%) 显著低的柱排/触顶组合，需退出

柱排[10]：跌.尾连(跌连)/跌.尾反孕(跌孕)/跌.尾吞(跌吞)/(跌)人.连后吞(人排)/升.尾连(升连)...
上符串[30]：A=触顶, B=哼, v=哈, w=底, _=无

磁盘CSV列序：1=收, 2=开, 8=DXCD, 9=DXAB, 13=日ZA, 26=次日高幅, 10=柱排, 30=上符串
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

def in_region(dxcd, hx):
    if dxcd not in ('上', '忐'): return False
    if hx in ('甲', '乙', '己'): return True
    return False

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def has_touch(sfs):
    return 'A' in sfs  # 触顶

# 统计: (柱排, 触顶) -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 30: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not in_region(dxcd, hx): continue
                zp = classify_zp(row[10])
                touch = has_touch(row[30])
                key = f'{zp}-{"触顶" if touch else "非触顶"}'
                stats[key][0]+=1; stats[key][1]+= (1 if hr>=3 else 0); stats[key][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 70)
print('操作区域内 柱排×触顶 P(≥3%)（识别诱多）')
print('=' * 70)
print(f'{"柱排×触顶":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 50)
# 排序：P(≥3%) 从低到高（诱多=低）
rows = [(k, s) for k, s in stats.items() if s[0] >= 500]
rows.sort(key=lambda x: x[1][1]/x[1][0])
for k, s in rows:
    print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
