"""周冲周冲策分梯度分析 — 按分数档统计真高幅表现"""
import os, csv, sys
from collections import defaultdict, OrderedDict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'

# 周冲周冲策分计算函数 — 与VBA神谕 3397-3445行逻辑一致
def calc_score(wxcd, wxab, za, zhupai, yingtishi, boxing):
    score = 0

    # ① 四域 (20分)
    is_jin = '金' in wxcd
    is_yin = '银' in wxcd
    is_jia_yi_ji = any(c in wxab for c in ['甲','乙','己'])
    if is_jin and is_jia_yi_ji:
        score += 20
    elif is_yin and is_jia_yi_ji:
        score += 15
    elif is_jin:
        score += 5

    # ② ZA区间 (30分)
    za = float(za) if za else 0
    if 5 < za <= 10:
        score += 30
    elif (3 <= za <= 5) or za > 10:
        score += 20
    elif 1 <= za < 3:
        score += 10

    # ③ 柱排+盈提示 (25分)
    is_sheng = zhupai.startswith('升')
    is_wei_fan_yun = '尾反孕' in zhupai
    is_gao = '高' in yingtishi
    is_ren = '人' in zhupai and not is_sheng
    is_die = zhupai.startswith('跌')
    if not is_wei_fan_yun and is_gao and is_sheng:
        score += 25
    elif is_sheng:
        score += 15
    elif is_ren:
        score += 8
    elif is_die:
        score += 5

    # ④ 波型 (25分)
    is_longzhu = '龙猪' in boxing
    is_longguan = '龙管' in boxing
    is_touzheng = '头正' in boxing
    is_toufu = '头负' in boxing
    is_zhenfu = '震负' in boxing
    is_zhenzheng = '震正' in boxing
    if is_longzhu or is_longguan:
        score += 25
    elif is_touzheng:
        score += 15
    elif is_toufu or is_zhenfu:
        score += 10
    elif is_zhenzheng:
        score += 5

    return score


# 范围定义
RANGES = OrderedDict([
    ('🏆 最优 85~100', (85, 100)),
    ('🟢 次优 70~84',  (70, 84)),
    ('🟡 中等 50~69',  (50, 69)),
    ('🟠 偏低 30~49',  (30, 49)),
    ('🔴 最差  0~29',  (0, 29)),
])

# 统计数据结构: {范围名: {'weeks': [HR值列表], 'codes': set}}
stats = {k: {'weeks': [], 'codes': set()} for k in RANGES}
total_weeks = 0
total_codes = set()

# 扫描所有谕组CSV
files = sorted([f for f in os.listdir(TEMP) if f.startswith('谕组_') and f.endswith('.csv')])
print(f'扫描文件: {len(files)}')

for fi, fn in enumerate(files):
    code = fn.replace('谕组_', '').replace('.csv', '')
    fp = os.path.join(TEMP, fn)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hr = float(row.get('HR', 0) or 0)
            except:
                continue

            wxcd = str(row.get('WXCD', '') or '')
            wxab = str(row.get('WXAB', '') or '')
            za = str(row.get('ZA周', '0') or '0')
            zhupai = str(row.get('柱排周', '') or '')
            yingtishi = str(row.get('盈提示', '') or '')
            boxing = str(row.get('波型', '') or '')

            score = calc_score(wxcd, wxab, za, zhupai, yingtishi, boxing)
            total_weeks += 1
            total_codes.add(code)

            for rname, (rmin, rmax) in RANGES.items():
                if rmin <= score <= rmax:
                    stats[rname]['weeks'].append(hr)
                    stats[rname]['codes'].add(code)
                    break

    if (fi + 1) % 1000 == 0:
        print(f'  已处理: {fi+1}/{len(files)} 文件, {total_weeks} 周')

# 输出统计
print(f'\n{"="*95}')
print(f'  周冲周冲策分梯度分析 (全量 {len(total_codes)}只 × {total_weeks}周)')
print(f'{"="*95}')
print(f'{"分数档":<20} {"代码数":>7} {"周数":>8} {"HR>0(真冲高)":>12} {"HR≥1%":>7} {"HR≥3%":>7} {"HR≥5%":>7} {"HR≥7%":>7} {"真均幅":>7} {"成功均幅":>9}')
print(f'{"-"*95}')

# 也显示累计（≥某分数）
cum_codes = set()
cum_weeks = 0
cum_hrs = []
# 按分数从高到低累计
score_order = ['🏆 最优 85~100', '🟢 次优 70~84', '🟡 中等 50~69', '🟠 偏低 30~49', '🔴 最差  0~29']

for rname in score_order:
    sw = stats[rname]
    n = len(sw['weeks'])
    if n == 0:
        print(f'{rname:<20} {len(sw["codes"]):>7} {n:>8} {"—":>12} {"—":>7} {"—":>7} {"—":>7} {"—":>7} {"—":>7} {"—":>9}')
        continue
    hrs = sw['weeks']
    hr_gt0 = sum(1 for h in hrs if h > 0) / n * 100
    hr_ge1 = sum(1 for h in hrs if h >= 1) / n * 100
    hr_ge3 = sum(1 for h in hrs if h >= 3) / n * 100
    hr_ge5 = sum(1 for h in hrs if h >= 5) / n * 100
    hr_ge7 = sum(1 for h in hrs if h >= 7) / n * 100
    avg_hr = sum(hrs) / n
    successful = [h for h in hrs if h > 0]
    avg_success = sum(successful) / len(successful) if successful else 0

    print(f'{rname:<20} {len(sw["codes"]):>7} {n:>8} {hr_gt0:>11.1f}% {hr_ge1:>6.1f}% {hr_ge3:>6.1f}% {hr_ge5:>6.1f}% {hr_ge7:>6.1f}% {avg_hr:>6.2f}% {avg_success:>8.2f}%')

print(f'{"-"*95}')
print(f'{"全量(基准)":<20} {len(total_codes):>7} {total_weeks:>8} {"—":>12}', end=' ')

# 全量基准
total_hrs = []
for rname in score_order:
    total_hrs.extend(stats[rname]['weeks'])
n_all = len(total_hrs)
if n_all > 0:
    hr_gt0 = sum(1 for h in total_hrs if h > 0) / n_all * 100
    hr_ge3 = sum(1 for h in total_hrs if h >= 3) / n_all * 100
    hr_ge5 = sum(1 for h in total_hrs if h >= 5) / n_all * 100
    hr_ge7 = sum(1 for h in total_hrs if h >= 7) / n_all * 100
    avg_all = sum(total_hrs) / n_all
    print(f'{hr_gt0:>11.1f}% {hr_ge3:>6.1f}% {hr_ge5:>6.1f}% {hr_ge7:>6.1f}% {avg_all:>6.2f}%')
else:
    print(f'{"—":>12} {"—":>7} {"—":>7} {"—":>7} {"—":>7}')

# 累计分析：≥各阈值
print(f'\n{"="*95}')
print(f'  累计分析 (≥某分数阈值的所有周)')
print(f'{"="*95}')
print(f'{"条件":<20} {"代码数":>7} {"周数":>8} {"HR>0(真冲高)":>12} {"HR≥1%":>7} {"HR≥3%":>7} {"HR≥5%":>7} {"HR≥7%":>7} {"真均幅":>7} {"成功均幅":>9}')
print(f'{"-"*95}')

# 定义累计阈值
CUM_THRESHOLDS = [
    ('≥85 (最优)', 85),
    ('≥70 (次优+)', 70),
    ('≥50 (中等+)', 50),
    ('≥30 (偏低+)', 30),
    ('全量', 0),
]

# 按分数档累积统计
cum_all_weeks = []  # 所有周(用于全量基准)
for rname in score_order:
    cum_all_weeks.extend(stats[rname]['weeks'])

for label, threshold in CUM_THRESHOLDS:
    cum_hrs = []
    cum_codes = set()
    for rname, (rmin, rmax) in RANGES.items():
        if rmin >= threshold:
            cum_hrs.extend(stats[rname]['weeks'])
            cum_codes.update(stats[rname]['codes'])
    n = len(cum_hrs)
    if n == 0:
        continue
    hr_gt0 = sum(1 for h in cum_hrs if h > 0) / n * 100
    hr_ge1 = sum(1 for h in cum_hrs if h >= 1) / n * 100
    hr_ge3 = sum(1 for h in cum_hrs if h >= 3) / n * 100
    hr_ge5 = sum(1 for h in cum_hrs if h >= 5) / n * 100
    hr_ge7 = sum(1 for h in cum_hrs if h >= 7) / n * 100
    avg_hr = sum(cum_hrs) / n
    successful = [h for h in cum_hrs if h > 0]
    avg_success = sum(successful) / len(successful) if successful else 0
    print(f'{label:<20} {len(cum_codes):>7} {n:>8} {hr_gt0:>11.1f}% {hr_ge1:>6.1f}% {hr_ge3:>6.1f}% {hr_ge5:>6.1f}% {hr_ge7:>6.1f}% {avg_hr:>6.2f}% {avg_success:>8.2f}%')

# 各维度独立贡献分析
print(f'\n\n{"="*95}')
print(f'  各维度独立贡献 (全量数据、非递进条件)')
print(f'{"="*95}')

# 重新遍历全部数据，按维度统计
dim_stats = defaultdict(lambda: {'weeks': []})
for fi, fn in enumerate(files[:]):
    code = fn.replace('谕组_', '').replace('.csv', '')
    fp = os.path.join(TEMP, fn)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hr = float(row.get('HR', 0) or 0)
            except:
                continue
            wxcd = str(row.get('WXCD', '') or '')
            wxab = str(row.get('WXAB', '') or '')
            za = str(row.get('ZA周', '0') or '0')
            zhupai = str(row.get('柱排周', '') or '')
            yingtishi = str(row.get('盈提示', '') or '')
            boxing = str(row.get('波型', '') or '')

            is_jin = '金' in wxcd
            is_jia_yi_ji = any(c in wxab for c in ['甲','乙','己'])
            za_val = float(za) if za else 0
            is_za5_10 = 5 < za_val <= 10
            is_sheng = zhupai.startswith('升')
            is_wei_fan_yun = '尾反孕' in zhupai
            is_gao = '高' in yingtishi
            is_longzhu_or_guan = '龙猪' in boxing or '龙管' in boxing
            is_touzheng = '头正' in boxing
            is_zhenzheng = '震正' in boxing

            # 维度1: 四域
            if is_jin and is_jia_yi_ji:
                dim_stats['四域:多长']['weeks'].append(hr)
            elif '银' in wxcd and is_jia_yi_ji:
                dim_stats['四域:银+甲乙己']['weeks'].append(hr)

            # 维度2: ZA
            if 5 < za_val <= 10:
                dim_stats['ZA:5~10']['weeks'].append(hr)
            elif 3 <= za_val <= 5:
                dim_stats['ZA:3~5']['weeks'].append(hr)
            elif 10 < za_val:
                dim_stats['ZA:>10']['weeks'].append(hr)
            elif 1 <= za_val < 3:
                dim_stats['ZA:1~3']['weeks'].append(hr)

            # 维度3: 柱排+盈
            if is_sheng and not is_wei_fan_yun and is_gao:
                dim_stats['柱排:升+非孕+盈高']['weeks'].append(hr)
            elif is_sheng:
                dim_stats['柱排:升(含孕)']['weeks'].append(hr)
            elif '人' in zhupai:
                dim_stats['柱排:人']['weeks'].append(hr)
            elif zhupai.startswith('跌'):
                dim_stats['柱排:跌']['weeks'].append(hr)

            # 维度4: 波型
            if is_longzhu_or_guan:
                dim_stats['波型:龙猪/龙管']['weeks'].append(hr)
            elif is_touzheng:
                dim_stats['波型:头正']['weeks'].append(hr)
            elif is_zhenzheng:
                dim_stats['波型:震正']['weeks'].append(hr)
            elif '头负' in boxing or '震负' in boxing:
                dim_stats['波型:头负/震负']['weeks'].append(hr)

    if (fi + 1) % 2000 == 0:
        print(f'  维度分析进度: {fi+1}/{len(files)}')

print(f'{"维度项":<24} {"周数":>8} {"HR>0":>8} {"HR≥3%":>7} {"HR≥5%":>7} {"真均幅":>7}')
print(f'{"-"*62}')
for dname in sorted(dim_stats.keys()):
    hrs = dim_stats[dname]['weeks']
    n = len(hrs)
    if n == 0:
        continue
    hr_gt0 = sum(1 for h in hrs if h > 0) / n * 100
    hr_ge3 = sum(1 for h in hrs if h >= 3) / n * 100
    hr_ge5 = sum(1 for h in hrs if h >= 5) / n * 100
    avg = sum(hrs) / n
    print(f'{dname:<24} {n:>8} {hr_gt0:>7.1f}% {hr_ge3:>6.1f}% {hr_ge5:>6.1f}% {avg:>6.2f}%')

# 关键组合条件 (从宽到严)
print(f'\n\n{"="*95}')
print(f'  条件递进组合 (从宽到严)')
print(f'{"="*95}')
print(f'{"条件铺叠":<32} {"周数":>8} {"HR>0":>8} {"HR≥3%":>7} {"HR≥5%":>7} {"HR≥7%":>7} {"真均幅":>7} {"成功真均幅":>9}')
print(f'{"-"*87}')

combos = OrderedDict()
combos['全量(基准)'] = lambda w: True
combos['四域=多长'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己'])
combos['多长 + ZA=3~10'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 3 <= w[2] <= 10
combos['多长 + ZA=5~10'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10
combos['多长 + ZA5~10 + 升排'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升')
combos['多长 + ZA5~10 + 升+非孕'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升') and '尾反孕' not in w[3]
combos['多长 + ZA5~10 + 升+非孕+盈高'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升') and '尾反孕' not in w[3] and '高' in w[4]
combos['多长 + ZA5~10 + 升+非孕+盈高 +龙猪/管'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升') and '尾反孕' not in w[3] and '高' in w[4] and ('龙猪' in w[5] or '龙管' in w[5])
combos['多长 + ZA5~10 + 升+非孕+盈高 +头正'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升') and '尾反孕' not in w[3] and '高' in w[4] and '头正' in w[5]
combos['多长 + ZA5~10 + 升+非孕+盈高 +震正'] = lambda w: '金' in w[0] and any(c in w[1] for c in ['甲','乙','己']) and 5 < w[2] <= 10 and w[3].startswith('升') and '尾反孕' not in w[3] and '高' in w[4] and '震正' in w[5]

# Collect data for combos
combo_data = {k: [] for k in combos}
for fn in files:
    fp = os.path.join(TEMP, fn)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hr = float(row.get('HR', 0) or 0)
            except:
                continue
            wxcd = str(row.get('WXCD', '') or '')
            wxab = str(row.get('WXAB', '') or '')
            za_str = str(row.get('ZA周', '0') or '0')
            zhupai = str(row.get('柱排周', '') or '')
            yingtishi = str(row.get('盈提示', '') or '')
            boxing = str(row.get('波型', '') or '')
            za_val = float(za_str) if za_str else 0

            w = (wxcd, wxab, za_val, zhupai, yingtishi, boxing)
            for cname, cfn in combos.items():
                if cfn(w):
                    combo_data[cname].append(hr)

for cname in combos:
    hrs = combo_data[cname]
    n = len(hrs)
    if n == 0:
        continue
    hr_gt0 = sum(1 for h in hrs if h > 0) / n * 100
    hr_ge3 = sum(1 for h in hrs if h >= 3) / n * 100
    hr_ge5 = sum(1 for h in hrs if h >= 5) / n * 100
    hr_ge7 = sum(1 for h in hrs if h >= 7) / n * 100
    avg = sum(hrs) / n
    successful = [h for h in hrs if h > 0]
    avg_suc = sum(successful) / len(successful) if successful else 0
    print(f'{cname:<32} {n:>8} {hr_gt0:>7.1f}% {hr_ge3:>6.1f}% {hr_ge5:>6.1f}% {hr_ge7:>6.1f}% {avg:>6.2f}% {avg_suc:>8.2f}%')

print(f'\n✅ 分析完成')