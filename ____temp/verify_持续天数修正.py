# -*- coding: utf-8 -*-
"""修正：从数据序列计算真正的护型持续天数 + 乙/丙按BTZA区分
数据：谕组周 CSV，GBK编码
列：护型[4](a甲/b乙/c丙/z丁/y戊/r己)、BTZA[13]、HR[3](下周=下一行)
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def huxing(hx):
    if not hx: return '?'
    c = hx[0]
    m = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
    return m.get(c, '?')

# 从数据序列计算护型持续天数（连续相同护型的周数）
# 统计：护型持续天数分层 × 下周冲高率
# 乙/丙按BTZA细分：乙ZA>0/乙ZA<=0，丙ZA>0/丙ZA<=0
stats = defaultdict(lambda: {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0})
base = {'n':0,'next_p3':[0,0],'next_hr_sum':0,'next_hr_n':0}

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    # 计算每行的护型持续天数（连续相同护型的周数）
    for i in range(len(rows)):
        cur = huxing(rows[i][4])
        # 从当前行往前数连续相同护型的周数
        dur = 1
        j = i - 1
        while j >= 0 and huxing(rows[j][4]) == cur:
            dur += 1
            j -= 1
        rows[i] = rows[i] + [dur]  # 追加持续天数到行尾
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        cur = huxing(row[4])
        dur = row[-1]  # 持续天数
        next_hr = None
        try: next_hr = float(nxt[3])
        except: pass
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1; base['next_hr_sum'] += next_hr
            if next_hr >= 3: base['next_p3'][0] += 1
            base['next_p3'][1] += 1
        if cur not in '甲乙丙丁戊己': continue
        # 乙/丙按BTZA细分
        try: btzc = int(row[15])
        except: btzc = None
        key = cur
        if cur == '乙':
            try:
                za = int(row[13])
                key = '乙ZA>0' if za > 0 else '乙ZA<=0'
            except: pass
        elif cur == '丙':
            try:
                za = int(row[13])
                key = '丙ZA>0' if za > 0 else '丙ZA<=0'
            except: pass
        # 持续天数分层
        if dur <= 2: layer = '1-2周'
        elif dur <= 5: layer = '3-5周'
        else: layer = '6+周'
        s = stats[f'{key}|{layer}']
        s['n'] += 1
        if next_hr is not None:
            s['next_hr_n'] += 1; s['next_hr_sum'] += next_hr
            if next_hr >= 3: s['next_p3'][0] += 1
            s['next_p3'][1] += 1
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线 (n={base["n"]}) ===')
print(f'  下周冲高率: {base["next_p3"][0]/base["next_p3"][1]*100:.2f}%  下周均HR: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')

print(f'\n=== 修正后：护型持续天数分层（从数据序列计算）× 下周冲高率 ===')
for key in ['甲','乙ZA>0','乙ZA<=0','丙ZA>0','丙ZA<=0','丁','戊','己']:
    for layer in ['1-2周','3-5周','6+周']:
        s = stats[f'{key}|{layer}']
        if s['n'] == 0: continue
        p3 = s['next_p3'][0]/s['next_p3'][1]*100 if s['next_p3'][1] else 0
        avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
        print(f'  [{key}|{layer}] n={s["n"]}: 下周冲高率={p3:.2f}% 下周均HR={avg_hr:.2f}%')