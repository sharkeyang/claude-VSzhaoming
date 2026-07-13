"""周冲条件系统性搜索 — 银/龙猪/WXAB/条件组合 下周冲高概率全量测试

扫描7673只×4227230周，输出所有具有统计意义的条件组合。
"""
import os, csv, sys
from collections import defaultdict, OrderedDict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'

# ============================================================
# 定义待测试的条件组合
# 每个组合是一个 dict，描述一种筛选条件
# ============================================================
TESTS = OrderedDict()

# ---- 1. 银(WXCD) 系列 ----
for wxab_val in ['甲','乙','丙','丁','戊','己','']:
    key = f'银_WXAB={wxab_val}' if wxab_val else '银_不限WXAB'
    TESTS[key] = {'wxcd': '银', 'wxab': wxab_val}

# 银 + 柱排方向
for zhupai_dir in ['升', '跌', '人']:
    TESTS[f'银_柱排={zhupai_dir}'] = {'wxcd': '银', 'zhupai': zhupai_dir}

# 银 + 波型
for box in ['龙猪', '龙管', '头正', '头负', '震负', '震正']:
    TESTS[f'银_波型={box}'] = {'wxcd': '银', 'boxing_set': {box}}

# 银 + ZA区间
for za_range, za_min, za_max in [('ZA≤0', -999, 0), ('ZA1~3', 1, 3), ('ZA3~5', 3, 5), ('ZA5~10', 5, 10), ('ZA>10', 10, 999)]:
    TESTS[f'银_{za_range}'] = {'wxcd': '银', 'za_min': za_min, 'za_max': za_max}

# ---- 2. 龙猪/龙管 波型系列 ----
TESTS['金+甲乙己+龙猪/管'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'boxing_set': {'龙猪','龙管'}}
TESTS['银+龙猪/管'] = {'wxcd': '银', 'boxing_set': {'龙猪','龙管'}}
TESTS['不限WXCD+龙猪/管'] = {'boxing_set': {'龙猪','龙管'}}

# 龙猪/龙管 + 柱排方向
for zhupai_dir in ['升', '跌', '人']:
    TESTS[f'龙猪/管_柱排={zhupai_dir}'] = {'boxing_set': {'龙猪','龙管'}, 'zhupai': zhupai_dir}

# ---- 3. WXAB 护型系列 ----
for wxcd_val in ['金', '银', '']:
    for wxab_val in ['甲','乙','丙','丁','戊','己']:
        label = f'WXCD={wxcd_val}_WXAB={wxab_val}' if wxcd_val else f'不限WXCD_WXAB={wxab_val}'
        TESTS[label] = {'wxcd': wxcd_val, 'wxab': wxab_val}

# ---- 4. 组合条件（多维度叠加） ----
# 银+龙猪/管+不同WXAB
for wxab_val in ['甲','乙','己','丙','丁','戊']:
    TESTS[f'银+龙猪/管+WXAB={wxab_val}'] = {'wxcd': '银', 'boxing_set': {'龙猪','龙管'}, 'wxab': wxab_val}

# 银+升排+不同WXAB
for wxab_val in ['甲','乙','己','丙','丁','戊']:
    TESTS[f'银+升排+WXAB={wxab_val}'] = {'wxcd': '银', 'zhupai': '升', 'wxab': wxab_val}

# 金+不同WXAB+龙猪/管
for wxab_val in ['甲','乙','己','丙','丁','戊']:
    TESTS[f'金+WXAB={wxab_val}+龙猪/管'] = {'wxcd': '金', 'wxab': wxab_val, 'boxing_set': {'龙猪','龙管'}}

# ---- 5. 盈提示组合 ----
TESTS['银+盈提示有'] = {'wxcd': '银', 'yingtishi_has': True}
TESTS['金+甲乙己+盈提示有'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'yingtishi_has': True}
TESTS['龙猪/管+盈提示有'] = {'boxing_set': {'龙猪','龙管'}, 'yingtishi_has': True}

# ---- 6. 最优条件组合 ----
# 多长+各ZA区间
for za_range, za_min, za_max in [('ZA≤0', -999, 0), ('ZA1~3', 1, 3), ('ZA3~5', 3, 5), ('ZA5~10', 5, 10), ('ZA>10', 10, 999)]:
    TESTS[f'金+甲乙己_{za_range}'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'za_min': za_min, 'za_max': za_max}

# 多长+升排
TESTS['金+甲乙己+升排'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升'}

# 多长+升排+非孕
TESTS['金+甲乙己+升排+非孕'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True}

# 多长+升排+非孕+盈高
TESTS['金+甲乙己+升排+非孕+盈高'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True, 'yingtishi_high': True}

# 多长+升排+非孕+盈高+龙猪/管
TESTS['最优(全部条件)'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True, 'yingtishi_high': True, 'boxing_set': {'龙猪','龙管'}}

# ============================================================
# 统计结构
# ============================================================
results = {k: {'total': 0, 'surge': 0, 'hrs': []} for k in TESTS}


def match_condition(row, cond):
    """检查一行数据是否匹配条件"""
    wxcd = str(row.get('WXCD', '') or '')
    wxab = str(row.get('WXAB', '') or '')
    za = float(row.get('ZA周', '0') or '0')
    zhupai = str(row.get('柱排周', '') or '')
    yingtishi = str(row.get('盈提示', '') or '')
    boxing = str(row.get('波型', '') or '')

    # WXCD
    if 'wxcd' in cond and cond['wxcd']:
        if cond['wxcd'] not in wxcd:
            return False

    # WXAB
    if 'wxab' in cond and cond['wxab']:
        if cond['wxab'] not in wxab:
            return False

    # WXAB set
    if 'wxab_set' in cond:
        if not any(c in wxab for c in cond['wxab_set']):
            return False

    # ZA区间
    if 'za_min' in cond:
        if not (cond['za_min'] < za <= cond['za_max']):
            return False

    # 柱排
    if 'zhupai' in cond:
        if cond['zhupai'] == '升' and not zhupai.startswith('升'):
            return False
        if cond['zhupai'] == '跌' and not zhupai.startswith('跌'):
            return False
        if cond['zhupai'] == '人' and not ('人' in zhupai and not zhupai.startswith('升') and not zhupai.startswith('跌')):
            return False

    # 非尾反孕
    if cond.get('no_weifanyun'):
        if '尾反孕' in zhupai:
            return False

    # 盈提示
    if 'yingtishi_has' in cond and cond['yingtishi_has']:
        if not yingtishi or yingtishi == '空':
            return False

    if 'yingtishi_high' in cond and cond['yingtishi_high']:
        if '高' not in yingtishi:
            return False

    # 波型
    if 'boxing_set' in cond:
        if not any(b in boxing for b in cond['boxing_set']):
            return False

    return True


# ============================================================
# 扫描所有谕组CSV
# ============================================================
files = sorted([f for f in os.listdir(TEMP) if f.startswith('谕组_') and f.endswith('.csv')])
print(f'扫描文件数: {len(files)}')
print(f'测试条件数: {len(TESTS)}')
print()

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

            # 对每个测试条件检查
            for k, cond in TESTS.items():
                if match_condition(row, cond):
                    results[k]['total'] += 1
                    results[k]['surge'] += 1 if hr > 0 else 0
                    results[k]['hrs'].append(hr)

    if (fi + 1) % 1000 == 0:
        print(f'  已处理 {fi+1}/{len(files)} 个文件...')

# ============================================================
# 输出结果
# ============================================================
print('\n' + '='*100)
print('周冲条件系统性搜索 — 结果报告')
print('='*100)

# 按成功率降序排列
sorted_results = sorted(results.items(), key=lambda x: x[1]['surge']/max(x[1]['total'],1) if x[1]['total'] > 0 else 0, reverse=True)

print(f'\n{"条件":<40s} {"样本量":>8s} {"冲高次数":>8s} {"成功率":>8s} {"真均幅":>8s} {"HR≥3%":>8s} {"HR≥5%":>8s}')
print('-'*100)

for k, v in sorted_results:
    total = v['total']
    if total < 100:  # 过滤样本太小
        continue
    surge = v['surge']
    rate = surge / total * 100
    hrs = v['hrs']
    avg_hr = sum(hrs) / len(hrs) if hrs else 0
    hr3 = sum(1 for h in hrs if h >= 3) / len(hrs) * 100 if hrs else 0
    hr5 = sum(1 for h in hrs if h >= 5) / len(hrs) * 100 if hrs else 0

    print(f'{k:<40s} {total:>8d} {surge:>8d} {rate:>7.1f}% {avg_hr:>7.2f}% {hr3:>7.1f}% {hr5:>7.1f}%')

print('\n' + '='*100)
print('筛选条件说明：')
print('  - 成功率 = 下周冲高(HR>0)的周数 / 总周数')
print('  - 真均幅 = 所有满足条件的周中，下周最高涨幅的平均值')
print('  - HR≥3% = 下周冲高≥3%的周占比')
print('  - 样本量<100的条件的已被过滤')
print('='*100)