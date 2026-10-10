# -*- coding: utf-8 -*-
"""分析2：持续天数分层的转移矩阵（非齐次）+ 分析3：护型+下周冲高率
数据：谕组周 CSV，GBK编码
列：护型[4](a甲/b乙/c丙/z丁/y戊/r己+方向+护级+持续天数)、HR[3](下周=下一行)
"""
import sys, csv, glob, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def huxing(hx):
    if not hx: return '?'
    c = hx[0]
    m = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
    return m.get(c, '?')

def chixu(hx):
    # 提取持续天数：护级(上中下忐忠忑)后的数字
    if not hx: return None
    m = re.search(r'[上中下忐忠忑](-?\d+)', hx)
    if m:
        try: return int(m.group(1))
        except: return None
    return None

def chixu_layer(d):
    if d is None: return '?'
    d = abs(d)  # 丁/戊/己持续天数为负数，用绝对值分层
    if d <= 2: return '1-2周'
    if d <= 5: return '3-5周'
    return '6+周'

# 分析2：持续天数分层 × 护型转移
trans_layer = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
huxing_cnt_layer = defaultdict(lambda: defaultdict(int))
# 分析3：护型 × 下周冲高率
huxing_p3 = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0})
# 分析3：护型转移 × 下周冲高率（当前护型→下周护型）
trans_p3 = defaultdict(lambda: defaultdict(lambda: {'n':0,'next_p3':[0,0]}))
base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i in range(len(rows)-1):
        cur = huxing(rows[i][4])
        nxt = huxing(rows[i+1][4])
        d = chixu(rows[i][4])
        layer = chixu_layer(d)
        next_hr = None
        try: next_hr = float(rows[i+1][3])
        except: pass
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        if cur in '甲乙丙丁戊己':
            # 分析2：持续天数分层转移
            if nxt in '甲乙丙丁戊己':
                trans_layer[layer][cur][nxt] += 1
                huxing_cnt_layer[layer][cur] += 1
            # 分析3：护型下周冲高率
            s = huxing_p3[cur]
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
                if next_hr >= 3: s['next_p3'][0] += 1
                s['next_p3'][1] += 1
            # 分析3：护型转移 × 下周冲高率
            if nxt in '甲乙丙丁戊己':
                ts = trans_p3[cur][nxt]
                ts['n'] += 1
                if next_hr is not None:
                    if next_hr >= 3: ts['next_p3'][0] += 1
                    ts['next_p3'][1] += 1
    if (fi+1) % 2000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

states = ['甲','乙','丙','丁','戊','己']
print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下周冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  下周均HR: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 分析2：持续天数分层的护型转移矩阵（非齐次）===')
for layer in ['1-2周','3-5周','6+周']:
    print(f'\n--- {layer} ---')
    print('当前\\下周'.ljust(6) + ''.join(f'{s:>8}' for s in states))
    for cur in states:
        row = []
        for nxt in states:
            cnt = trans_layer[layer][cur][nxt]
            total = huxing_cnt_layer[layer][cur]
            p = cnt/total*100 if total else 0
            row.append(f'{p:>7.1f}%')
        print(f'{cur:<6}' + ''.join(row))

print(f'\n=== 分析3：各护型下周冲高率 ===')
for cur in states:
    s = huxing_p3[cur]
    if s['n'] == 0: continue
    p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    print(f'  [{cur}] n={s["n"]}: 下周冲高率={p3:.2f}% 下周均HR={avg_hr:.2f}%')

print(f'\n=== 分析3：护型转移 × 下周冲高率 ===')
for cur in states:
    for nxt in states:
        ts = trans_p3[cur][nxt]
        if ts['n'] == 0: continue
        p3 = ts['next_p3'][0]/ts['next_p3'][1]*100 if ts['next_p3'][1] else 0
        print(f'  [{cur}→{nxt}] n={ts["n"]}: 下周冲高率={p3:.2f}%')