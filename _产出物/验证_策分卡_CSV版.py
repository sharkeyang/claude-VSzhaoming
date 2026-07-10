"""策分验证：全维度统计（真高幅/代高幅/下周涨等）"""
import os, csv, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'

# 读取所有CSV
all_weeks = []
for f in sorted(os.listdir(TEMP)):
    if not f.startswith('谕组_') or not f.endswith('.csv'): continue
    code = f.replace('谕组_','').replace('.csv','')
    fp = os.path.join(TEMP, f)
    with open(fp, 'r', encoding='gbk') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                row['HR'] = float(row.get('HR',0) or 0)
                row['PR'] = float(row.get('PR',0) or 0)
                row['ZA'] = float(row.get('ZA周',0) or 0)
            except:
                row['HR'] = 0
                row['PR'] = 0
                row['ZA'] = 0
            row['code'] = code
            all_weeks.append(row)

# 按代码分组，按顺序计算下周指标
by_code = defaultdict(list)
for w in all_weeks:
    by_code[w['code']].append(w)

for code, weeks in by_code.items():
    for i in range(len(weeks)-1):
        w = weeks[i]
        nw = weeks[i+1]
        w['下周HR'] = nw['HR']
        w['下周PR'] = nw['PR']
        w['下周涨'] = nw['PR'] > 0

# 策分计算
def calc_score(row):
    f = 0; j = str(row.get('WXCD','')); h = str(row.get('WXAB',''))
    za = row['ZA']; zp = str(row.get('柱排周','')); yt = str(row.get('盈提示','')); bx = str(row.get('波型',''))
    if '金' in j and ('甲' in h or '乙' in h or '己' in h): f += 20
    elif '银' in j and ('甲' in h or '乙' in h or '己' in h): f += 15
    elif '金' in j: f += 5
    if 5 < za <= 10: f += 30
    elif (3 <= za <= 5) or za > 10: f += 20
    elif 1 <= za < 3: f += 10
    if '尾反孕' not in zp and '高' in yt and zp.startswith('升'): f += 25
    elif zp.startswith('升'): f += 15
    elif '人' in zp: f += 8
    elif zp.startswith('跌'): f += 5
    if '龙猪' in bx or '龙管' in bx: f += 25
    elif '头正' in bx: f += 15
    elif '头负' in bx or '震负' in bx: f += 10
    elif '震正' in bx: f += 5
    return f

for w in all_weeks:
    w['score'] = calc_score(w)

# 分档
levels = [(85,'85~100'),(70,'70~84'),(50,'50~69'),(30,'30~49'),(0,'<30')]
def get_level(s):
    for th, name in levels:
        if s >= th: return name
    return '<30'

# 统计
bands = ['85~100','70~84','50~69','30~49','<30']
stats = {}
for b in bands:
    stats[b] = {'n':0, 'hrs':[], 'prs':[], 'hr_ok':0, 'hr3':0, 'hr5':0, 'pr_ok':0, 'pr3':0, 'pr5':0, 'nw_up':0, 'nw_hr':0}

for w in all_weeks:
    b = get_level(w['score'])
    s = stats[b]
    s['n'] += 1
    s['hrs'].append(w['HR'])
    s['prs'].append(w['PR'])
    if w['HR'] > 0: s['hr_ok'] += 1
    if w['HR'] >= 3: s['hr3'] += 1
    if w['HR'] >= 5: s['hr5'] += 1
    if w['PR'] > 0: s['pr_ok'] += 1
    if w['PR'] >= 3: s['pr3'] += 1
    if w['PR'] >= 5: s['pr5'] += 1
    if w.get('下周涨', False): s['nw_up'] += 1
    if w.get('下周HR', 0) > 0: s['nw_hr'] += 1

# 基准
base_n = len(all_weeks)
base_hr = sum(w['HR'] for w in all_weeks)/base_n if base_n else 0
base_pr = sum(w['PR'] for w in all_weeks)/base_n if base_n else 0
base_hr_ok = sum(1 for w in all_weeks if w['HR']>0)/base_n*100 if base_n else 0
base_pr_ok = sum(1 for w in all_weeks if w['PR']>0)/base_n*100 if base_n else 0
base_hr3 = sum(1 for w in all_weeks if w['HR']>=3)/base_n*100 if base_n else 0
base_nw_up = sum(1 for w in all_weeks if w.get('下周涨',False))/base_n*100 if base_n else 0
base_nw_hr = sum(1 for w in all_weeks if w.get('下周HR',0)>0)/base_n*100 if base_n else 0

print(f'57只ETF, {base_n}周')
print()
print(f'{"分档":>8} {"周数":>6} {"真冲高":>7} {"真均幅":>7} {"真≥3%":>7} {"真≥5%":>7} {"代冲高":>7} {"代均幅":>7} {"下周涨":>7} {"下周冲高":>8}')
for b in bands:
    s = stats[b]
    n = s['n']
    if n == 0: continue
    hr_ok = s['hr_ok']/n*100
    hr_avg = sum(s['hrs'])/n
    hr3 = s['hr3']/n*100
    hr5 = s['hr5']/n*100
    pr_ok = s['pr_ok']/n*100
    pr_avg = sum(s['prs'])/n
    nw_up = s['nw_up']/n*100
    nw_hr = s['nw_hr']/n*100
    print(f'{b:>8} {n:>6} {hr_ok:>6.0f}% {hr_avg:>6.2f}% {hr3:>6.0f}% {hr5:>6.0f}% {pr_ok:>6.0f}% {pr_avg:>6.2f}% {nw_up:>6.0f}% {nw_hr:>7.0f}%')

print(f'{"基准":>8} {base_n:>6} {base_hr_ok:>6.0f}% {base_hr:>6.2f}% {base_hr3:>6.0f}% {base_nw_up:>6.0f}% {base_nw_hr:>7.0f}%')
" 2>&1