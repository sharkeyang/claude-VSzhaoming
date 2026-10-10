# -*- coding: utf-8 -*-
"""验证日层联动(位谕of日层联动[7])的操作(持/减/清/观/勿)对下日冲高的区分度
数据：谕组日 CSV，GBK编码
列：日层联动[7]、涨幅[5]、高幅[6]、次日高幅[26](下一行高幅)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def parse_float(s):
    try: return float(s)
    except: return None

# 统计：按操作 + 按周向
# 指标：下日冲高率(次日高幅>=3%)、下日均高幅、下日涨幅<0率
op_stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0,'next_pr_neg':[0,0]})
zhou_stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0,'next_pr_neg':[0,0]})
op_zhou = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0]}))
base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0,'next_pr_neg':[0,0]}

files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):  # 需要下一行
        row, nxt = rows[i], rows[i+1]
        lian = row[7]
        if not lian: continue
        # 解析操作(最后一位)和周向(第一位)
        op = lian[-1] if lian else ''
        zhou = lian[0] if lian else ''
        next_hr = parse_float(nxt[6])  # 下一行高幅
        next_pr = parse_float(nxt[5])  # 下一行涨幅
        # 基线
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
            if next_pr is not None and next_pr < 0: base['next_pr_neg'][0] += 1
            base['next_pr_neg'][1] += 1
        # 按操作
        if op in '持减清观勿':
            s = op_stats[op]
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
                if next_hr >= 3: s['next_p3'][0] += 1
                s['next_p3'][1] += 1
                if next_pr is not None and next_pr < 0: s['next_pr_neg'][0] += 1
                s['next_pr_neg'][1] += 1
        # 按周向
        if zhou in '龙武雀虎':
            s = zhou_stats[zhou]
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
                if next_hr >= 3: s['next_p3'][0] += 1
                s['next_p3'][1] += 1
                if next_pr is not None and next_pr < 0: s['next_pr_neg'][0] += 1
                s['next_pr_neg'][1] += 1
            # 操作×周向
            if op in '持减清观勿':
                os_ = op_zhou[zhou][op]
                os_['n'] += 1
                if next_hr is not None:
                    if next_hr >= 3: os_['next_p3'][0] += 1
                    os_['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下日冲高率(次日高幅>=3%): {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  (n={base["next_p3"][1]})')
print(f'  下日均高幅: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')
print(f'  下日涨幅<0率: {base["next_pr_neg"][0]/base["next_pr_neg"][1]*100:.2f}%')

print(f'\n=== 按操作 (持/减/清/观/勿) ===')
for op in ['持','减','清','观','勿']:
    s = op_stats[op]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    pr_neg = s['next_pr_neg'][0]/s['next_pr_neg'][1]*100 if s['next_pr_neg'][1] else 0
    print(f'  [{op}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}% 下日跌率={pr_neg:.2f}%')

print(f'\n=== 按周向 (龙/武/雀/虎) ===')
for zhou in ['龙','武','雀','虎']:
    s = zhou_stats[zhou]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    pr_neg = s['next_pr_neg'][0]/s['next_pr_neg'][1]*100 if s['next_pr_neg'][1] else 0
    print(f'  [{zhou}] n={s["n"]}: 下日冲高率={p3:.2f}% 下日均高幅={avg_hr:.2f}% 下日跌率={pr_neg:.2f}%')

print(f'\n=== 操作×周向 (下日冲高率) ===')
for zhou in ['龙','武','雀','虎']:
    for op in ['持','减','清','观','勿']:
        os_ = op_zhou[zhou][op]
        if os_['n'] == 0: continue
        p3 = os_['next_p3'][0]/os_['next_p3'][1]*100 if os_['next_p3'][1] else 0
        print(f'  [{zhou}{op}] n={os_["n"]}: 下日冲高率={p3:.2f}%')