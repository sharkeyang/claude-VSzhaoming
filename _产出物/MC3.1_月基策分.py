"""月基策分：多长进 → WXZC<0出，逐ETF模拟交易"""
import os, csv, sys
from collections import defaultdict
from statistics import mean
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

TEMP = r'd:\@VSwork\VS昭明计划VBA优化\____temp'

all_weeks = []
for f in sorted(os.listdir(TEMP)):
    if not f.startswith('谕组_') or not f.endswith('.csv'):
        continue
    code = f.replace('谕组_', '').replace('.csv', '')
    fp = os.path.join(TEMP, f)
    with open(fp, 'r', encoding='gbk') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                row['HR'] = float(row.get('HR', 0) or 0)
                row['ZC'] = float(row.get('ZC周', 0) or 0)
            except:
                row['HR'] = 0
                row['ZC'] = 0
            row['code'] = code
            all_weeks.append(row)

print(f'总ETF: {len(set(w["code"] for w in all_weeks))}只, 总周数: {len(all_weeks)}')

by_code = defaultdict(list)
for w in all_weeks:
    by_code[w['code']].append(w)

results = []
for code, weeks in by_code.items():
    weeks.sort(key=lambda w: str(w.get('主期', '')))
    in_pos = False
    entry_hr = 0
    trades = []
    柱排反转 = 0
    多长周数 = 0
    prev_dir = ''
    hr涨比列表 = []  # 所有持仓周的高幅/涨幅比例

    for w in weeks:
        j = str(w.get('WXCD', ''))
        h = str(w.get('WXAB', ''))
        zc = w['ZC']
        HR = w['HR']
        try:
            周涨 = float(w.get('周涨', 0) or 0)
        except:
            周涨 = 0
        zp = str(w.get('柱排周', ''))

        is_多长 = '金' in j and ('甲' in h or '乙' in h or '己' in h)

        if not in_pos:
            if is_多长:
                in_pos = True
                持仓累积 = 1.0  # 从1开始累积
                多长周数 = 1
                cur_dir = ''
                if zp.startswith('升'):
                    cur_dir = '升'
                elif zp.startswith('跌'):
                    cur_dir = '跌'
                prev_dir = cur_dir
        else:
            多长周数 += 1
            持仓累积 *= (1 + 周涨 / 100)  # 累积周收益

            # 柱排反转计数
            cur_dir = ''
            if zp.startswith('升'):
                cur_dir = '升'
            elif zp.startswith('跌'):
                cur_dir = '跌'
            if cur_dir and prev_dir and cur_dir != prev_dir:
                柱排反转 += 1
            if cur_dir:
                prev_dir = cur_dir

            if zc < 0:
                收益 = 持仓累积 - 1  # 总收益%
                trades.append(收益)
                in_pos = False

            # 记录HR/涨比例（持仓期间每周）
            if 周涨 != 0:
                hr涨比 = HR / 周涨
            else:
                hr涨比 = 0
            hr涨比列表.append(hr涨比)

    if len(trades) == 0:
        results.append((code, 0, 0, 0, 0, 0, 0, 0, 0, '无数据'))
        continue

    总收益 = sum(trades)
    年化 = 总收益 / max(len(weeks) / 52, 0.1)
    胜率 = sum(1 for t in trades if t > 0) / len(trades)
    盈利 = [t for t in trades if t > 0]
    亏损 = [t for t in trades if t < 0]
    均盈 = sum(盈利)/len(盈利) if 盈利 else 0
    均亏 = abs(sum(亏损)/len(亏损)) if 亏损 else 0
    盈亏比 = 99 if not 亏损 else (0 if not 盈利 else 均盈/均亏)
    均单次 = sum(trades) / len(trades)
    震仓 = 柱排反转 / max(多长周数, 1)
    均HR涨比 = mean(hr涨比列表) if hr涨比列表 else 0

    股性 = 年化 * 胜率 * 盈亏比 * 均单次 / (1 + 震仓)

    if 股性 >= 0.8:
        评级 = '🏆仁慈'
    elif 股性 >= 0.3:
        评级 = '✅正常'
    elif 股性 >= 0:
        评级 = '⚠️震荡'
    else:
        评级 = '❌凶残'

    results.append((code, 股性, 年化, 胜率, 盈亏比, 均单次, 震仓, len(trades), 均HR涨比, 评级))

results.sort(key=lambda r: -r[1])
print(f'\n{"代码":>10} {"月基策分":>8} {"年化":>7} {"胜率":>6} {"盈亏比":>6} {"均单次":>7} {"震仓":>6} {"次数":>5} {"HR/涨":>7} {"评级":>6}')
print('-' * 75)
for r in results[:30]:
    print(f'{r[0]:>10} {r[1]:>8.4f} {r[2]:>7.4f} {r[3]:>6.2f} {r[4]:>6.2f} {r[5]:>7.4f} {r[6]:>6.4f} {r[7]:>5} {r[8]:>7.2f} {r[9]:>6}')

top = sum(1 for r in results if r[9] == '🏆仁慈')
good = sum(1 for r in results if r[9] == '✅正常')
mid = sum(1 for r in results if r[9] == '⚠️震荡')
bad = sum(1 for r in results if r[9] == '❌凶残')
no = sum(1 for r in results if r[9] == '无数据')
print(f'\n🏆仁慈: {top}只  ✅正常: {good}只  ⚠️震荡: {mid}只  ❌凶残: {bad}只  ➖无数据: {no}只')

# 输出到CSV
csv_out = os.path.join(TEMP, '..', '_产出物', '月基策分结果.csv')
with open(csv_out, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['代码','月基策分','年化','胜率','盈亏比','均单次','震仓','次数','HR涨比','评级'])
    for r in results:
        w.writerow(r)
print(f'\n已保存: {csv_out}')

# HR/涨比分布
有数据的 = [r for r in results if r[8] > 0]
hr高 = sum(1 for r in 有数据的 if r[8] >= 3)
hr中 = sum(1 for r in 有数据的 if 2 <= r[8] < 3)
hr低 = sum(1 for r in 有数据的 if r[8] < 2)
print(f'\nHR/涨比分布(>3=适合做T, 2~3=可做T, <2=趋势平滑):')
print(f'  HR/涨≥3(冲高型): {hr高}只')
print(f'  HR/涨2~3(适中): {hr中}只')
print(f'  HR/涨<2(平滑型): {hr低}只')