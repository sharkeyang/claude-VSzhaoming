"""周冲策分验证：按代码类型分类统计（基金/指数/沪深300/中证500/中证1000/中证2000/非板块）"""
import os, csv, json
from collections import defaultdict

# 输出编码
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'
MAP_FILE = r'd:\@VSwork\VS昭明计划VBA优化\_产出物\花册分类映射.json'

# 加载分类映射
with open(MAP_FILE, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

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
            row['cat'] = mapping.get(code, '非板块')
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

# 周冲策分计算
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

# 类别顺序
CAT_ORDER = ['基金ETF', '指数', '沪深300上证50', '中证500', '中证1000', '中证2000', '非板块']
CAT_LABELS = {
    '基金ETF': '基金ETF',
    '指数': '指数',
    '沪深300上证50': '沪深300',
    '中证500': '中证500',
    '中证1000': '中证1000',
    '中证2000': '中证2000',
    '非板块': '非板块',
}

bands = ['85~100','70~84','50~69','30~49','<30']

def print_stat_header(title):
    print()
    print(f'╔═ {title} ═╗')
    print(f'{"分档":>8} {"周数":>8} {"股数":>7} {"均周":>6} {"真冲高":>8} {"真均幅":>8} {">=1%":>8} {">=3%":>8} {">=5%":>8} {">=7%":>8} {"下周涨":>8} {"下周冲高":>8}')

def print_stat_line(b, s):
    n = s['n']
    if n == 0: return
    n_codes = len(s['codes'])
    avg_weeks = n / n_codes if n_codes else 0
    hr_ok = s['hr_ok']/n*100
    hr_avg = sum(s['hrs'])/n
    hr1 = s['hr1']/n*100
    hr3 = s['hr3']/n*100
    hr5 = s['hr5']/n*100
    hr7 = s['hr7']/n*100
    nw_up = s['nw_up']/n*100
    nw_hr = s['nw_hr']/n*100
    print(f'{b:>8} {n:>8} {n_codes:>7} {avg_weeks:>5.0f} {hr_ok:>7.0f}% {hr_avg:>7.2f}% {hr1:>7.0f}% {hr3:>7.0f}% {hr5:>7.0f}% {hr7:>7.0f}% {nw_up:>7.0f}% {nw_hr:>7.0f}%')

def print_stat_base(n, n_codes, hr_avg, hr_ok, hr1, hr3, hr5, hr7, nw_up, nw_hr):
    avg_weeks = n / n_codes if n_codes else 0
    print(f'{"基准":>8} {n:>8} {n_codes:>7} {avg_weeks:>5.0f} {hr_ok:>7.0f}% {hr_avg:>7.2f}% {hr1:>7.0f}% {hr3:>7.0f}% {hr5:>7.0f}% {hr7:>7.0f}% {nw_up:>7.0f}% {nw_hr:>7.0f}%')

def init_stats_dict():
    return {'n':0, 'codes':set(), 'hrs':[], 'prs':[], 'hr_ok':0, 'hr1':0, 'hr3':0, 'hr5':0, 'hr7':0, 'nw_up':0, 'nw_hr':0}

# ===== 全量统计 =====
print('\n' + '='*70)
print('📊 全量统计')
print('='*70)
stats = {}
for b in bands:
    stats[b] = init_stats_dict()
for w in all_weeks:
    b = get_level(w['score'])
    s = stats[b]
    s['n'] += 1
    s['codes'].add(w['code'])
    s['hrs'].append(w['HR'])
    s['prs'].append(w['PR'])
    if w['HR'] > 0: s['hr_ok'] += 1
    if w['HR'] >= 1: s['hr1'] += 1
    if w['HR'] >= 3: s['hr3'] += 1
    if w['HR'] >= 5: s['hr5'] += 1
    if w['HR'] >= 7: s['hr7'] += 1
    if w.get('下周涨', False): s['nw_up'] += 1
    if w.get('下周HR', 0) > 0: s['nw_hr'] += 1

base_n = len(all_weeks)
base_codes = len(by_code)
base_hr = sum(w['HR'] for w in all_weeks)/base_n if base_n else 0
base_hr_ok = sum(1 for w in all_weeks if w['HR']>0)/base_n*100 if base_n else 0
base_hr1 = sum(1 for w in all_weeks if w['HR']>=1)/base_n*100 if base_n else 0
base_hr3 = sum(1 for w in all_weeks if w['HR']>=3)/base_n*100 if base_n else 0
base_hr5 = sum(1 for w in all_weeks if w['HR']>=5)/base_n*100 if base_n else 0
base_hr7 = sum(1 for w in all_weeks if w['HR']>=7)/base_n*100 if base_n else 0
base_nw_up = sum(1 for w in all_weeks if w.get('下周涨',False))/base_n*100 if base_n else 0
base_nw_hr = sum(1 for w in all_weeks if w.get('下周HR',0)>0)/base_n*100 if base_n else 0

print_stat_header(f'全量 ({base_n}周, 共{base_codes}只)')
for b in bands:
    print_stat_line(b, stats[b])
print_stat_base(base_n, base_codes, base_hr, base_hr_ok, base_hr1, base_hr3, base_hr5, base_hr7, base_nw_up, base_nw_hr)

# ===== 按类别分类统计 =====
print('\n' + '='*70)
print('📊 按代码类型分类统计')
print('='*70)

for cat in CAT_ORDER:
    cat_weeks = [w for w in all_weeks if w['cat'] == cat]
    if not cat_weeks:
        continue

    cat_stats = {}
    for b in bands:
        cat_stats[b] = init_stats_dict()

    for w in cat_weeks:
        b = get_level(w['score'])
        s = cat_stats[b]
        s['n'] += 1
        s['codes'].add(w['code'])
        s['hrs'].append(w['HR'])
        s['prs'].append(w['PR'])
        if w['HR'] > 0: s['hr_ok'] += 1
        if w['HR'] >= 1: s['hr1'] += 1
        if w['HR'] >= 3: s['hr3'] += 1
        if w['HR'] >= 5: s['hr5'] += 1
        if w['HR'] >= 7: s['hr7'] += 1
        if w.get('下周涨', False): s['nw_up'] += 1
        if w.get('下周HR', 0) > 0: s['nw_hr'] += 1

    cat_n = len(cat_weeks)
    cat_codes_set = set(w['code'] for w in cat_weeks)
    cat_n_codes = len(cat_codes_set)
    cat_hr = sum(w['HR'] for w in cat_weeks)/cat_n if cat_n else 0
    cat_hr_ok = sum(1 for w in cat_weeks if w['HR']>0)/cat_n*100 if cat_n else 0
    cat_hr1 = sum(1 for w in cat_weeks if w['HR']>=1)/cat_n*100 if cat_n else 0
    cat_hr3 = sum(1 for w in cat_weeks if w['HR']>=3)/cat_n*100 if cat_n else 0
    cat_hr5 = sum(1 for w in cat_weeks if w['HR']>=5)/cat_n*100 if cat_n else 0
    cat_hr7 = sum(1 for w in cat_weeks if w['HR']>=7)/cat_n*100 if cat_n else 0
    cat_nw_up = sum(1 for w in cat_weeks if w.get('下周涨',False))/cat_n*100 if cat_n else 0
    cat_nw_hr = sum(1 for w in cat_weeks if w.get('下周HR',0)>0)/cat_n*100 if cat_n else 0

    label = CAT_LABELS.get(cat, cat)
    print_stat_header(f'{label} ({cat_n}周, {cat_n_codes}只)')
    for b in bands:
        print_stat_line(b, cat_stats[b])
    print_stat_base(cat_n, cat_n_codes, cat_hr, cat_hr_ok, cat_hr1, cat_hr3, cat_hr5, cat_hr7, cat_nw_up, cat_nw_hr)