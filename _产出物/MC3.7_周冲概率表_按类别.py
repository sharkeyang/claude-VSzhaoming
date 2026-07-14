"""周冲条件系统性搜索 v2 — 按类别拆分 + 概率即分数

扫描7673只×4227230周，每个条件组合按类别(沪深300上证50/中证500/中证1000/中证2000/非板块/基金ETF/指数)拆分。
输出概率表可直接用于VBA查表赋值。
"""
import os, csv, sys, json, glob
from collections import defaultdict, OrderedDict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'
CAT_FILE = glob.glob(os.path.join('_产出物', '*MP1*.json'))
if CAT_FILE:
    CAT_FILE = CAT_FILE[0]
else:
    # Try direct listing
    import os as _os
    for _f in _os.listdir('_产出物'):
        if _f.endswith('.json') and 'MP1' in _f:
            CAT_FILE = _os.path.join('_产出物', _f)
            break

# ============================================================
# 加载分类映射
# ============================================================
cat_map = {}
ALL_CATS = ['非板块', '指数', '中证2000', '中证1000', '基金ETF', '中证500', '沪深300上证50', '未分类']

if CAT_FILE:
    with open(CAT_FILE, 'r', encoding='utf-8') as f:
        cat_map = json.load(f)
    # 实际存在的分类
    raw_json = json.dumps(cat_map, ensure_ascii=False)
    cats = [c for c in ALL_CATS if c in raw_json]
    print(f'已加载分类映射: {len(cat_map)}只')
    print(f'类别: {cats}')
else:
    cats = ['未分类']
    print('未找到分类映射文件')
print()

# ============================================================
# 定义待测试的条件组合（精简版 — 只测关键组合）
# ============================================================
TESTS = OrderedDict()

# 基准
TESTS['全量基准'] = {}

# 金系（原策分卡条件）
TESTS['金+甲乙己(多长)'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}}
TESTS['金+甲乙己+升排'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升'}
TESTS['金+甲乙己+升排+非孕'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True}
TESTS['金+甲乙己+升排+非孕+盈高'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True, 'yingtishi_high': True}
TESTS['最优(全部)'] = {'wxcd': '金', 'wxab_set': {'甲','乙','己'}, 'zhupai': '升', 'no_weifanyun': True, 'yingtishi_high': True, 'boxing_set': {'龙猪','龙管'}}

# 银系
TESTS['银_不限WXAB'] = {'wxcd': '银'}
TESTS['银+WXAB=己'] = {'wxcd': '银', 'wxab': '己'}
TESTS['银+WXAB=甲'] = {'wxcd': '银', 'wxab': '甲'}
TESTS['银+盈提示有'] = {'wxcd': '银', 'yingtishi_has': True}
TESTS['银+柱排=升'] = {'wxcd': '银', 'zhupai': '升'}
TESTS['银+龙猪'] = {'wxcd': '银', 'boxing_set': {'龙猪'}}
TESTS['银+龙猪/管+WXAB=甲'] = {'wxcd': '银', 'boxing_set': {'龙猪','龙管'}, 'wxab': '甲'}
TESTS['银+ZA5~10'] = {'wxcd': '银', 'za_min': 5, 'za_max': 10}

# WXAB=己系列
TESTS['WXAB=己(不限WXCD)'] = {'wxab': '己'}
TESTS['WXAB=甲(不限WXCD)'] = {'wxab': '甲'}
TESTS['WXAB=乙(不限WXCD)'] = {'wxab': '乙'}

# 波型系列
TESTS['龙猪/管+柱排=升'] = {'boxing_set': {'龙猪','龙管'}, 'zhupai': '升'}
TESTS['龙猪/管+盈提示有'] = {'boxing_set': {'龙猪','龙管'}, 'yingtishi_has': True}

# ============================================================
# 统计结构: {条件名: {类别名: {'total': int, 'surge': int, 'hrs': list}}}
# ============================================================
results = {k: {c: {'total': 0, 'surge': 0, 'hrs': []} for c in cats} for k in TESTS}


def match_condition(row, cond):
    """检查一行数据是否匹配条件"""
    wxcd = str(row.get('WXCD', '') or '')
    wxab = str(row.get('WXAB', '') or '')
    za = float(row.get('ZA周', '0') or '0')
    zhupai = str(row.get('柱排周', '') or '')
    yingtishi = str(row.get('盈提示', '') or '')
    boxing = str(row.get('波型', '') or '')

    if 'wxcd' in cond and cond['wxcd']:
        if cond['wxcd'] not in wxcd:
            return False
    if 'wxab' in cond and cond['wxab']:
        if cond['wxab'] not in wxab:
            return False
    if 'wxab_set' in cond:
        if not any(c in wxab for c in cond['wxab_set']):
            return False
    if 'za_min' in cond and 'za_max' in cond:
        if not (cond['za_min'] < za <= cond['za_max']):
            return False
    if 'zhupai' in cond:
        if cond['zhupai'] == '升' and not zhupai.startswith('升'):
            return False
        if cond['zhupai'] == '跌' and not zhupai.startswith('跌'):
            return False
        if cond['zhupai'] == '人' and not ('人' in zhupai and not zhupai.startswith('升') and not zhupai.startswith('跌')):
            return False
    if cond.get('no_weifanyun') and '尾反孕' in zhupai:
        return False
    if 'yingtishi_has' in cond and cond['yingtishi_has']:
        if not yingtishi or yingtishi == '空':
            return False
    if 'yingtishi_high' in cond and cond['yingtishi_high']:
        if '高' not in yingtishi:
            return False
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
print(f'分类数: {len(cats)}')
print()

for fi, fn in enumerate(files):
    code = fn.replace('谕组_', '').replace('.csv', '')
    cat = cat_map.get(code, '非板块')
    if cat not in cats:
        cat = '未分类'

    fp = os.path.join(TEMP, fn)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hr = float(row.get('HR', 0) or 0)
            except:
                continue

            for k, cond in TESTS.items():
                if match_condition(row, cond):
                    results[k][cat]['total'] += 1
                    results[k][cat]['surge'] += 1 if hr > 0 else 0
                    results[k][cat]['hrs'].append(hr)

    if (fi + 1) % 1000 == 0:
        print(f'  已处理 {fi+1}/{len(files)} 个文件...')

# ============================================================
# 输出结果 — 3个概率表
# ============================================================
# 显示列：全量(所有类别合计) + 6个主要类别
DISPLAY_CATS = ['全量', '中证2000', '中证1000', '沪深300上证50', '基金ETF', '指数']
# 条件显示名映射
DISPLAY_NAMES = {
    '全量基准': '全量基准',
    '金+甲乙己(多长)': '金+多长',
    '金+甲乙己+升排': '金+多长+升排',
    '金+甲乙己+升排+非孕': '金+多长+升排+非孕',
    '金+甲乙己+升排+非孕+盈高': '金+多长+升排+非孕+盈高',
    '最优(全部)': '最优(全部)',
    '银_不限WXAB': '银(全量)',
    '银+WXAB=己': '银+WXAB=己',
    '银+WXAB=甲': '银+WXAB=甲',
    '银+盈提示有': '银+盈提示有',
    '银+柱排=升': '银+柱排=升',
    '银+龙猪': '银+龙猪',
    '银+龙猪/管+WXAB=甲': '银+龙猪/管+WXAB=甲',
    '银+ZA5~10': '银+ZA5~10',
    'WXAB=己(不限WXCD)': 'WXAB=己(不限)',
    'WXAB=甲(不限WXCD)': 'WXAB=甲(不限)',
    'WXAB=乙(不限WXCD)': 'WXAB=乙(不限)',
    '龙猪/管+柱排=升': '龙猪/管+柱排=升',
    '龙猪/管+盈提示有': '龙猪/管+盈提示有',
}

def get_all_total(k):
    """所有类别的合计"""
    return sum(results[k][c]['total'] for c in cats)

def get_all_surge(k):
    return sum(results[k][c]['surge'] for c in cats)

def get_all_hrs(k):
    hrs = []
    for c in cats:
        hrs.extend(results[k][c]['hrs'])
    return hrs

def print_table(title, prob_func):
    """输出一个概率表"""
    print(f'\n## {title}')
    # 表头
    header = f'{"条件":<28s}'
    for c in DISPLAY_CATS:
        header += f'  {c:>8s}'
    print(header)
    print('-' * (28 + 2 + 10 * len(DISPLAY_CATS)))

    for k in TESTS:
        total_all = get_all_total(k)
        if total_all < 100:
            continue
        line = f'{DISPLAY_NAMES.get(k, k):<28s}'

        # 全量列
        val = prob_func(k)
        line += f'  {val:>7.1f}%'

        # 各分类列
        for c in cats:
            if c not in DISPLAY_CATS[1:]:
                continue
            if c == '非板块' or c == '中证500':
                continue
            v = results[k][c]
            if v['total'] >= 100:
                val = prob_func(k, c)
                line += f'  {val:>7.1f}%'
            else:
                line += f'  {"-":>8s}'
        print(line)


# 表1: 冲高概率(HR>0)
print('\n' + '='*100)
print('表1：下周冲高概率 P(HR>0)')
print('='*100)
print_table('P(HR>0)', lambda k, c=None: (get_all_surge(k)/get_all_total(k)*100) if c is None else (results[k][c]['surge']/results[k][c]['total']*100))

# 表2: P(>1%)
print('\n' + '='*100)
print('表2：下周冲高超过1%的概率')
print('='*100)
def p1(k, c=None):
    hrs = get_all_hrs(k) if c is None else results[k][c]['hrs']
    total = get_all_total(k) if c is None else results[k][c]['total']
    if not hrs: return 0
    return sum(1 for h in hrs if h > 1) / len(hrs) * 100
print_table('P(>1%)', p1)

# 表3: P(>3%)
print('\n' + '='*100)
print('表3：下周冲高超过3%的概率')
print('='*100)
def p3(k, c=None):
    hrs = get_all_hrs(k) if c is None else results[k][c]['hrs']
    if not hrs: return 0
    return sum(1 for h in hrs if h >= 3) / len(hrs) * 100
print_table('P(>3%)', p3)

# 表4: P(>5%)
print('\n' + '='*100)
print('表4：下周冲高超过5%的概率')
print('='*100)
def p5(k, c=None):
    hrs = get_all_hrs(k) if c is None else results[k][c]['hrs']
    if not hrs: return 0
    return sum(1 for h in hrs if h >= 5) / len(hrs) * 100
print_table('P(>5%)', p5)

print('\n' + '='*100)
print('说明：')
print('- 全量 = 所有7673只股票合计')
print('- 中证2000/中证1000/沪深300上证50/基金ETF/指数 = 按花册分类拆分')
print('- 非板块、中证500因篇幅未列入此表，可在详细版中查看')
print('- 概率即分数：策分 = 条件在下周冲高的概率值')
print('- 基础条件可设为WXZC>0 (全量基准 ~91.5%)，低于此不参与')
print('- 样本量<100的已过滤')
print('='*100)