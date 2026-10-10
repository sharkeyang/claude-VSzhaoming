# -*- coding: utf-8 -*-
"""验证日层漏提示[64]的下日冲高率，对比基线与日层联动
数据：谕组日 CSV，GBK编码
列：日层漏提示[64]、日层联动[7]、涨幅[5]、高幅[6]、次日高幅[26](下一行高幅)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}
lou_stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0})
# 按日细分类型（上漏/首防诱/上持/丙漏/被/乙e漏）
type_stats = defaultdict(lambda: {'n':0,'next_p3':[0,0]})
# 日漏 × 日层联动操作
lou_op = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0]}))

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        row, nxt = rows[i], rows[i+1]
        lou = row[64]
        lian = row[7]
        next_hr = parse_float(nxt[6])
        # 基线
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        # 日漏非空
        if lou:
            s = lou_stats['有日漏']
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
                if next_hr >= 3: s['next_p3'][0] += 1
                s['next_p3'][1] += 1
            # 按日细分类型
            for t in ['上漏','首防诱','上持','丙漏','被','乙e漏']:
                if t in lou:
                    ts = type_stats[t]
                    ts['n'] += 1
                    if next_hr is not None:
                        if next_hr >= 3: ts['next_p3'][0] += 1
                        ts['next_p3'][1] += 1
            # 日漏 × 日层联动操作
            if lian:
                op = lian[-1]
                if op in '持减清观勿':
                    os_ = lou_op[op]['有日漏']
                    os_['n'] += 1
                    if next_hr is not None:
                        if next_hr >= 3: os_['next_p3'][0] += 1
                        os_['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下日冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  (n={base["next_p3"][1]})')
print(f'  下日均高幅: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 日漏提示 (非空) ===')
for k, s in lou_stats.items():
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    print(f'  [{k}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}%')

print(f'\n=== 日漏提示 按日细分类型 ===')
for t in ['上漏','首防诱','上持','丙漏','被','乙e漏']:
    s = type_stats[t]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    print(f'  [{t}] n={s["n"]}: 下日冲高率={p3:.2f}%')

print(f'\n=== 日漏提示 × 日层联动操作 ===')
for op in ['持','减','清','观','勿']:
    os_ = lou_op[op]['有日漏']
    if os_['n'] == 0: continue
    p3 = os_['next_p3'][0]/os_['next_p3'][1]*100 if os_['next_p3'][1] else 0
    print(f'  [日漏+{op}] n={os_["n"]}: 下日冲高率={p3:.2f}%')