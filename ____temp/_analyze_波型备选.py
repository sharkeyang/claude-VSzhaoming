# -*- coding: utf-8 -*-
"""分析龙头/龙震系列波型是否适合周日联合备选 + 是否易诱多
数据：谕组周 CSV（旧编码：龙头芽/龙头根/龙震芽/龙震根）
"""
import sys, csv, glob
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 目标波型（旧编码，对应新编码：龙头交/龙头返/龙震芽/龙震根）
TARGETS = {
    'Dd龙头芽': '龙头交(近似)',
    'De龙头根': '龙头返(近似)',
    'Fd龙震芽': '龙震芽',
    'Fe龙震根': '龙震根',
}

def parse_float(s):
    try:
        return float(s)
    except:
        return None

# 统计
# 每个目标波型：样本数、下周P3、下周均HR、0<ZA<=3比例、诱多率(0<ZA<=3且下周ZA<0)
stats = {k: {'n': 0, 'next_p3': 0, 'next_hr_sum': 0, 'next_hr_n': 0,
             'za_1_3': 0, 'za_1_3_next_neg': 0, 'next_za_neg': 0} for k in TARGETS}
# 基线
base = {'n': 0, 'next_p3': 0, 'next_hr_sum': 0, 'next_hr_n': 0,
        'za_1_3': 0, 'za_1_3_next_neg': 0, 'next_za_neg': 0}

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
for fi, f in enumerate(files):
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        header = next(r)
        rows = list(r)
    for i in range(len(rows) - 1):  # 需要下一行
        row = rows[i]
        nxt = rows[i+1]
        b = row[5]
        if not b:
            continue
        name = b.split('.')[0]
        # 下周 HR
        next_hr = parse_float(nxt[3])
        # 本周 ZA
        try:
            za = int(row[13])
        except:
            za = None
        # 下周 ZA
        try:
            next_za = int(nxt[13])
        except:
            next_za = None

        # 基线统计
        base['n'] += 1
        if next_hr is not None:
            base['next_hr_n'] += 1
            base['next_hr_sum'] += next_hr
            if next_hr >= 3:
                base['next_p3'] += 1
        if za is not None and 0 < za <= 3:
            base['za_1_3'] += 1
            if next_za is not None and next_za < 0:
                base['za_1_3_next_neg'] += 1
        if next_za is not None and next_za < 0:
            base['next_za_neg'] += 1

        # 目标波型统计
        if name in TARGETS:
            s = stats[name]
            s['n'] += 1
            if next_hr is not None:
                s['next_hr_n'] += 1
                s['next_hr_sum'] += next_hr
                if next_hr >= 3:
                    s['next_p3'] += 1
            if za is not None and 0 < za <= 3:
                s['za_1_3'] += 1
                if next_za is not None and next_za < 0:
                    s['za_1_3_next_neg'] += 1
            if next_za is not None and next_za < 0:
                s['next_za_neg'] += 1
    if (fi+1) % 1000 == 0:
        print(f'  已处理 {fi+1} 文件...', file=sys.stderr)

print(f'\n=== 基线（全部，n={base["n"]}）===')
print(f'  下周P3: {base["next_p3"]/base["next_hr_n"]*100:.2f}%  (n={base["next_hr_n"]})')
print(f'  下周均HR: {base["next_hr_sum"]/base["next_hr_n"]:.2f}%')
print(f'  0<ZA<=3比例: {base["za_1_3"]/base["n"]*100:.2f}%')
print(f'  下周ZA<0比例: {base["next_za_neg"]/base["n"]*100:.2f}%')
print(f'  诱多率(0<ZA<=3且下周ZA<0): {base["za_1_3_next_neg"]/base["n"]*100:.2f}%')

print(f'\n=== 目标波型 ===')
for name, label in TARGETS.items():
    s = stats[name]
    if s['n'] == 0:
        print(f'\n{name} ({label}): 无样本')
        continue
    p3 = s['next_p3']/s['next_hr_n']*100 if s['next_hr_n'] else 0
    avg_hr = s['next_hr_sum']/s['next_hr_n'] if s['next_hr_n'] else 0
    za13 = s['za_1_3']/s['n']*100
    next_neg = s['next_za_neg']/s['n']*100
    youduo = s['za_1_3_next_neg']/s['n']*100
    print(f'\n{name} ({label}): n={s["n"]}')
    print(f'  下周P3: {p3:.2f}%  (n={s["next_hr_n"]})')
    print(f'  下周均HR: {avg_hr:.2f}%')
    print(f'  0<ZA<=3比例: {za13:.2f}%')
    print(f'  下周ZA<0比例: {next_neg:.2f}%')
    print(f'  诱多率(0<ZA<=3且下周ZA<0): {youduo:.2f}%')
