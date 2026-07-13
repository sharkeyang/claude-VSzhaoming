"""分析：多长连续时，下周冲高是否连续出现"""
import os, csv, json
from collections import defaultdict

import sys
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
                row['ZC周'] = float(row.get('ZC周',0) or 0)
            except:
                row['HR'] = 0
                row['ZC周'] = 0
            row['code'] = code
            all_weeks.append(row)

# 按代码分组，按时间排序
by_code = defaultdict(list)
for w in all_weeks:
    by_code[w['code']].append(w)

# 判断多长
def is_多长(row):
    j = str(row.get('WXCD',''))
    h = str(row.get('WXAB',''))
    return '金' in j and ('甲' in h or '乙' in h or '己' in h)

# 分析每只股票的多长连续段
total_runs = 0
run_lengths = []
scores_by_pos = defaultdict(list)  # 多长第N周 → [下周冲高概率]

nw_hr_consec_ok = 0  # 连续多长中，下周冲高连续出现次数
nw_hr_consec_total = 0

for code, weeks in by_code.items():
    weeks.sort(key=lambda w: str(w.get('主期','')))

    # 先计算下周HR
    for i in range(len(weeks)-1):
        weeks[i]['下周HR'] = weeks[i+1]['HR']
        weeks[i]['下周冲高'] = weeks[i+1]['HR'] > 0

    # 找多长连续段
    in_run = False
    run_start = -1
    run_weeks = []

    for i, w in enumerate(weeks):
        if is_多长(w):
            if not in_run:
                in_run = True
                run_start = i
                run_weeks = [w]
            else:
                run_weeks.append(w)
        else:
            if in_run and len(run_weeks) >= 2:  # 至少连续2周才算
                run_lengths.append(len(run_weeks))
                total_runs += 1

                # 分析这个连续段内下周冲高的情况
                for pos, rw in enumerate(run_weeks):
                    if '下周HR' in rw:
                        scores_by_pos[pos].append(1 if rw.get('下周冲高', False) else 0)

                # 连续冲高统计：连续多长中连续下周冲高的比例
                if len(run_weeks) >= 2:
                    cons = 0
                    for rw in run_weeks:
                        if '下周HR' in rw:
                            nw_hr_consec_total += 1
                            if rw.get('下周冲高', False):
                                nw_hr_consec_ok += 1

            in_run = False
            run_weeks = []

# 输出结果
print('='*70)
print('📊 多长连续段分析')
print('='*70)

total_stocks = len(by_code)
print(f'总股票数: {total_stocks}只')
print(f'总多长连续段(≥2周): {total_runs}段')
print(f'平均段长: {sum(run_lengths)/len(run_lengths):.1f}周' if run_lengths else '0')
print()

# 段长分布
print('--- 多长连续段长度分布 ---')
len_dist = defaultdict(int)
for l in run_lengths:
    if l <= 5: len_dist[str(l)] += 1
    elif l <= 10: len_dist['6-10'] += 1
    elif l <= 20: len_dist['11-20'] += 1
    else: len_dist['21+'] += 1
for l in ['2','3','4','5','6-10','11-20','21+']:
    if l in len_dist:
        print(f'  连续{l}周: {len_dist[l]}段 ({len_dist[l]/total_runs*100:.1f}%)')

print()
# 总体：连续多长中的下周冲高概率
total_ok = sum(len(v) for v in scores_by_pos.values() if sum(v) > 0)
total_all = sum(len(v) for v in scores_by_pos.values())
print(f'--- 多长信号期间下周冲高概率 ---')
print(f'  总多长周数: {total_all}')
print(f'  下周冲高次数: {nw_hr_consec_ok}')
print(f'  下周冲高概率: {nw_hr_consec_ok/total_all*100:.1f}%' if total_all else '0%')
print()

# 按多长第N周统计下周冲高概率
print('--- 多长第N周的下周冲高概率 ---')
for pos in sorted(scores_by_pos.keys())[:20]:  # 最多显示前20周
    vals = scores_by_pos[pos]
    if vals:
        ok = sum(vals)
        n = len(vals)
        print(f'  多长第{pos+1}周: {ok}/{n} = {ok/n*100:.0f}%')

print()
# 连续性分析：连续多长中，连续冲高的比例
print('--- 连续性分析 ---')
cons_ok = 0  # 连续多长中连续下周冲高的周数
cons_total = 0

for code, weeks in by_code.items():
    weeks.sort(key=lambda w: str(w.get('主期','')))
    for i in range(len(weeks)-1):
        weeks[i]['下周HR'] = weeks[i+1]['HR']
        weeks[i]['下周冲高'] = weeks[i+1]['HR'] > 0

    in_run = False
    run_weeks = []
    for i, w in enumerate(weeks):
        if is_多长(w):
            if not in_run:
                in_run = True
                run_weeks = [w]
            else:
                run_weeks.append(w)
        else:
            if in_run and len(run_weeks) >= 2:
                # 检查连续冲高比例
                for j in range(len(run_weeks)-1):
                    if '下周HR' in run_weeks[j] and '下周HR' in run_weeks[j+1]:
                        cons_total += 1
                        if run_weeks[j].get('下周冲高', False) and run_weeks[j+1].get('下周冲高', False):
                            cons_ok += 1
            in_run = False
            run_weeks = []

print(f'  连续多长前后周都已知下周HR: {cons_total}对')
print(f'  其中连续两周下周都冲高: {cons_ok}对')
print(f'  连续冲高概率: {cons_ok/cons_total*100:.1f}%' if cons_total else '0%')
print(f'  单独一周冲高概率: {nw_hr_consec_ok/total_all*100:.1f}%' if total_all else '0%')

# 条件概率：如果这周下周冲高了，下周继续冲高的概率
cond_ok = 0
cond_total = 0
for code, weeks in by_code.items():
    weeks.sort(key=lambda w: str(w.get('主期','')))
    for i in range(len(weeks)):
        weeks[i]['下周HR'] = weeks[i+1]['HR'] if i < len(weeks)-1 else 0
        weeks[i]['下周冲高'] = weeks[i+1]['HR'] > 0 if i < len(weeks)-1 else False

    in_run = False
    run_weeks = []
    for i, w in enumerate(weeks):
        if is_多长(w):
            if not in_run:
                in_run = True
                run_weeks = [w]
            else:
                run_weeks.append(w)
        else:
            if in_run and len(run_weeks) >= 2:
                for j in range(len(run_weeks)-1):
                    if run_weeks[j].get('下周冲高', False) and run_weeks[j+1].get('下周HR', -1) >= 0:
                        cond_total += 1
                        if run_weeks[j+1].get('下周冲高', False):
                            cond_ok += 1
            in_run = False
            run_weeks = []

print(f'\n--- 条件概率 ---')
print(f'  多长期间，本周下周冲高 → 下周继续冲高: {cond_ok}/{cond_total} = {cond_ok/cond_total*100:.1f}%' if cond_total else '0%')
print(f'  无条件冲高概率: {nw_hr_consec_ok/total_all*100:.1f}%' if total_all else '0%')
print()
print('结论：如果条件概率 > 无条件概率，说明有连续性')
print('如果两者接近，说明是随机分布（散落出现）')