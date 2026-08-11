import csv, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datadir = r'昭明算展\谕组周'
files = sorted(os.listdir(datadir))
total_files = len(files)
print(f'总文件: {total_files}')

# 逐文件读取，逐文件计算
# 策略条件
def is_金升(w): return '金升' in str(w.get('WXCD', ''))
def is_银升(w): return '银升' in str(w.get('WXCD', ''))
def is_甲乙己(w): return any(c in str(w.get('WXAB', '')) for c in ['甲','乙','己'])
def is_多长(w):
    zc = float(w.get('ZC周', 0) or 0)
    zb = float(w.get('ZB周', 0) or 0)
    return zc > 0 and zb > 0 and ('金' in str(w.get('WXCD', '')))
def has_升排(w): return str(w.get('柱排周', '')).startswith('升')
def has_非孕(w): return '孕' not in str(w.get('柱排周', ''))
def has_盈高(w): return '高' in str(w.get('盈提示', ''))
def has_龙猪(w): return '龙猪' in str(w.get('波型', ''))
def has_龙管(w): return '龙管' in str(w.get('波型', ''))

# 条件组
def cond_金最优(w): return is_金升(w) and is_甲乙己(w) and has_升排(w) and has_非孕(w) and has_盈高(w) and (has_龙猪(w) or has_龙管(w))
def cond_金盈高(w): return is_金升(w) and is_甲乙己(w) and has_升排(w) and has_非孕(w) and has_盈高(w)
def cond_金升排非孕(w): return is_金升(w) and is_甲乙己(w) and has_升排(w) and has_非孕(w)
def cond_金升排(w): return is_金升(w) and is_甲乙己(w) and has_升排(w)
def cond_金多长(w): return is_金升(w) and is_多长(w)
def cond_银盈高(w): return is_银升(w) and has_盈高(w)
def cond_银龙猪(w): return is_银升(w) and has_龙猪(w)
def cond_银升排(w): return is_银升(w) and has_升排(w)
def cond_银ZA(w): return is_银升(w) and 5 <= float(w.get('ZA周', 0) or 0) <= 10
def cond_银己(w): return is_银升(w) and '己' in str(w.get('WXAB', ''))

conds = [
    ('金最优(全部)', cond_金最优),
    ('金+升排+非孕+盈高', cond_金盈高),
    ('金+升排+非孕', cond_金升排非孕),
    ('金+升排', cond_金升排),
    ('金+多长', cond_金多长),
    ('银+盈提示有', cond_银盈高),
    ('银+龙猪', cond_银龙猪),
    ('银+柱排升', cond_银升排),
    ('银+ZA5~10', cond_银ZA),
    ('银+WXAB=己', cond_银己),
]

# 按市板分类
board_map = {'Qe': 'ETF', 'Qd': '指数', 'Qif': '沪深300', 'Qic': '中证500',
             'Qim': '中证1000', 'Qit': '中证2000', 'Qin': '非成分'}

# 统计数据
stats = {name: {'total': 0, 'sum_hr': 0.0, 'hr3': 0, 'hr5': 0, 'hr0': 0} for name, _ in conds}
board_stats = {name: {b: {'total': 0, 'hr3': 0} for b in board_map} for name, _ in conds}
all_total = 0
all_sum_hr = 0.0
all_hr3 = 0
all_hr5 = 0

processed = 0
for fname in files:
    fp = os.path.join(datadir, fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except:
        continue

    for i in range(len(rows) - 1):
        w = rows[i]
        next_hr = float(rows[i+1].get('HR', 0) or 0)
        市板 = str(w.get('市板', ''))

        # 全量基准
        all_total += 1
        all_sum_hr += next_hr
        if next_hr >= 3: all_hr3 += 1
        if next_hr >= 5: all_hr5 += 1

        # 各策略
        for name, cond in conds:
            if cond(w):
                stats[name]['total'] += 1
                stats[name]['sum_hr'] += next_hr
                if next_hr >= 3: stats[name]['hr3'] += 1
                if next_hr >= 5: stats[name]['hr5'] += 1
                if next_hr > 0: stats[name]['hr0'] += 1
                if 市板 in board_stats[name]:
                    board_stats[name][市板]['total'] += 1
                    if next_hr >= 3: board_stats[name][市板]['hr3'] += 1

    processed += 1
    if processed % 500 == 0:
        print(f'  已处理: {processed}/{total_files}', flush=True)

# 输出结果
print('\n' + '='*60)
print('全量策略概率表')
print('='*60)
print(f'\n全量基准: {all_total}周, 均高幅={all_sum_hr/all_total:.2f}%, P(>=3%)={all_hr3/all_total*100:.1f}%, P(>=5%)={all_hr5/all_total*100:.1f}%')
print()

print(f'{"策略":<22} {"周数":>8} {"均高幅":>8} {"P(>=3%)":>10} {"P(>=5%)":>10}')
print('-' * 60)
for name, _ in conds:
    d = stats[name]
    if d['total'] < 100:
        continue
    avg = d['sum_hr']/d['total']
    p3 = d['hr3']/d['total']*100
    p5 = d['hr5']/d['total']*100
    p0 = d['hr0']/d['total']*100
    print(f'{name:<22} {d["total"]:>8} {avg:>7.2f}% {p3:>8.1f}% {p5:>8.1f}%')

# 金最优按市板
print(f'\n=== 金最优(全部) 按市板 ===')
for bc, bn in board_map.items():
    bd = board_stats['金最优(全部)'][bc]
    if bd['total'] >= 100:
        p3 = bd['hr3']/bd['total']*100
        print(f'  {bn}: {bd["total"]:>8}周, P(>=3%)={p3:>5.1f}%')