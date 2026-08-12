import csv, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datadir = r'昭明算展\谕组周'
files = sorted(os.listdir(datadir))[:500]

stock_data = defaultdict(list)

for fname in files:
    code = fname.replace('谕组周_', '').replace('.csv', '')
    fp = os.path.join(datadir, fname)
    with open(fp, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stock_data[code].append({
                'wxab': str(row.get('WXAB', '')),
                'wxcd': str(row.get('WXCD', '')),
            })

# 分析1: WXAB各状态下WXCD分布
print('='*60)
print('1. WXAB各状态 → WXCD金银率')
print('='*60)
ab_states = {'甲': 0, '乙': 0, '丙': 0, '丁': 0, '戊': 0, '己': 0}
ab_cd_good = {'甲': 0, '乙': 0, '丙': 0, '丁': 0, '戊': 0, '己': 0}

for code, weeks in stock_data.items():
    for w in weeks:
        for ab in ['甲','乙','丙','丁','戊','己']:
            if ab in w['wxab']:
                ab_states[ab] += 1
                if '金' in w['wxcd'] or '银' in w['wxcd']:
                    ab_cd_good[ab] += 1
                break

for ab in ['甲','乙','丙','丁','戊','己']:
    pct = ab_cd_good[ab]/ab_states[ab]*100 if ab_states[ab] > 0 else 0
    print(f'  WXAB={ab}: {ab_states[ab]:>7}次, 金银率 {pct:>5.1f}%')

# 分析2: WXAB变化后WXCD跟随概率
print('\n' + '='*60)
print('2. WXAB变化后WXCD多周跟随概率')
print('='*60)

forward_1w_good = 0; forward_1w_t = 0
forward_1w_jin = 0
forward_2w_good = 0; forward_2w_t = 0
forward_3w_good = 0; forward_3w_t = 0
forward_4w_good = 0; forward_4w_t = 0

reverse_1w_bad = 0; reverse_1w_t = 0
reverse_2w_bad = 0; reverse_2w_t = 0
reverse_3w_bad = 0; reverse_3w_t = 0
reverse_4w_bad = 0; reverse_4w_t = 0

for code, weeks in stock_data.items():
    for i in range(len(weeks) - 4):
        if i == 0: continue
        curr = weeks[i]
        prev = weeks[i-1]

        curr_ab_good = '甲' in curr['wxab'] or '乙' in curr['wxab']
        prev_ab_good = '甲' in prev['wxab'] or '乙' in prev['wxab']

        curr_cd_good = '金' in curr['wxcd'] or '银' in curr['wxcd']
        prev_cd_good = '金' in prev['wxcd'] or '银' in prev['wxcd']
        curr_cd_jin = '金升' in curr['wxcd']

        # 正向变化
        if not prev_ab_good and curr_ab_good:
            for wk in [1, 2, 3, 4]:
                target = weeks[i + wk]
                t_cd_good = '金' in target['wxcd'] or '银' in target['wxcd']
                t_cd_jin = '金升' in target['wxcd']
                if wk == 1:
                    forward_1w_t += 1
                    if t_cd_good: forward_1w_good += 1
                    if t_cd_jin: forward_1w_jin += 1
                elif wk == 2:
                    forward_2w_t += 1
                    if t_cd_good: forward_2w_good += 1
                elif wk == 3:
                    forward_3w_t += 1
                    if t_cd_good: forward_3w_good += 1
                elif wk == 4:
                    forward_4w_t += 1
                    if t_cd_good: forward_4w_good += 1

        # 反向变化
        if prev_ab_good and not curr_ab_good:
            for wk in [1, 2, 3, 4]:
                target = weeks[i + wk]
                t_cd_bad = not ('金' in target['wxcd'] or '银' in target['wxcd'])
                if wk == 1:
                    reverse_1w_t += 1
                    if t_cd_bad: reverse_1w_bad += 1
                elif wk == 2:
                    reverse_2w_t += 1
                    if t_cd_bad: reverse_2w_bad += 1
                elif wk == 3:
                    reverse_3w_t += 1
                    if t_cd_bad: reverse_3w_bad += 1
                elif wk == 4:
                    reverse_4w_t += 1
                    if t_cd_bad: reverse_4w_bad += 1

print('正向带动（丙丁戊己→甲乙 后WXCD变化）：')
print(f'  1周后 → 金银: {forward_1w_good}/{forward_1w_t} = {forward_1w_good/forward_1w_t*100:.1f}%')
print(f'  1周后 → 金升: {forward_1w_jin}/{forward_1w_t} = {forward_1w_jin/forward_1w_t*100:.1f}%')
print(f'  2周后 → 金银: {forward_2w_good}/{forward_2w_t} = {forward_2w_good/forward_2w_t*100:.1f}%')
print(f'  3周后 → 金银: {forward_3w_good}/{forward_3w_t} = {forward_3w_good/forward_3w_t*100:.1f}%')
print(f'  4周后 → 金银: {forward_4w_good}/{forward_4w_t} = {forward_4w_good/forward_4w_t*100:.1f}%')

print('\n反向带动（甲乙→丙丁戊己 后WXCD变化）：')
print(f'  1周后 → 非金银: {reverse_1w_bad}/{reverse_1w_t} = {reverse_1w_bad/reverse_1w_t*100:.1f}%')
print(f'  2周后 → 非金银: {reverse_2w_bad}/{reverse_2w_t} = {reverse_2w_bad/reverse_2w_t*100:.1f}%')
print(f'  3周后 → 非金银: {reverse_3w_bad}/{reverse_3w_t} = {reverse_3w_bad/reverse_3w_t*100:.1f}%')
print(f'  4周后 → 非金银: {reverse_4w_bad}/{reverse_4w_t} = {reverse_4w_bad/reverse_4w_t*100:.1f}%')

# 分析3: 策略对比
print('\n' + '='*60)
print('3. 策略对比')
print('='*60)

# 方案A: 只等WXAB转好就介入
ab_甲乙 = 0
ab_甲乙_cd_good = 0
ab_甲乙_cd_jin = 0
for code, weeks in stock_data.items():
    for w in weeks:
        if '甲' in w['wxab'] or '乙' in w['wxab']:
            ab_甲乙 += 1
            if '金' in w['wxcd'] or '银' in w['wxcd']:
                ab_甲乙_cd_good += 1
            if '金升' in w['wxcd']:
                ab_甲乙_cd_jin += 1

print(f'\n方案A: WXAB=甲乙时介入')
print(f'  WXCD金银率: {ab_甲乙_cd_good}/{ab_甲乙} = {ab_甲乙_cd_good/ab_甲乙*100:.1f}%')
print(f'  WXCD金升率: {ab_甲乙_cd_jin}/{ab_甲乙} = {ab_甲乙_cd_jin/ab_甲乙*100:.1f}%')

# 方案B: 只等WXAB=乙
乙_only = 0
乙_cd_good = 0
乙_cd_jin = 0
for code, weeks in stock_data.items():
    for w in weeks:
        if '乙' in w['wxab']:
            乙_only += 1
            if '金' in w['wxcd'] or '银' in w['wxcd']:
                乙_cd_good += 1
            if '金升' in w['wxcd']:
                乙_cd_jin += 1

print(f'\n方案B: 只等WXAB=乙时介入')
print(f'  WXCD金银率: {乙_cd_good}/{乙_only} = {乙_cd_good/乙_only*100:.1f}%')
print(f'  WXCD金升率: {乙_cd_jin}/{乙_only} = {乙_cd_jin/乙_only*100:.1f}%')

# 分析4: 条件概率 - WXAB转好但WXCD没好
print('\n' + '='*60)
print('4. 关键决策：WXAB转好但WXCD尚未转好，是否介入？')
print('='*60)

ab_转好_cd_未好_1w = 0
ab_转好_cd_未好_1w_t = 0

for code, weeks in stock_data.items():
    for i in range(len(weeks) - 1):
        if i == 0: continue
        curr = weeks[i]
        prev = weeks[i-1]

        prev_ab_good = '甲' in prev['wxab'] or '乙' in prev['wxab']
        curr_ab_good = '甲' in curr['wxab'] or '乙' in curr['wxab']
        prev_cd_good = '金' in prev['wxcd'] or '银' in prev['wxcd']
        curr_cd_good = '金' in curr['wxcd'] or '银' in curr['wxcd']

        # AB刚转好，但CD还没好
        if not prev_ab_good and curr_ab_good and not prev_cd_good and not curr_cd_good:
            ab_转好_cd_未好_1w_t += 1
            # 1周后CD转好
            if i + 1 < len(weeks):
                next_w = weeks[i + 1]
                if '金' in next_w['wxcd'] or '银' in next_w['wxcd']:
                    ab_转好_cd_未好_1w += 1

print(f'  AB转好但CD尚未好: {ab_转好_cd_未好_1w_t}次')
print(f'  1周后CD转好: {ab_转好_cd_未好_1w}/{ab_转好_cd_未好_1w_t} = {ab_转好_cd_未好_1w/ab_转好_cd_未好_1w_t*100:.1f}%')
print(f'  结论: WXAB转好但WXCD未好，等1周有{ab_转好_cd_未好_1w/ab_转好_cd_未好_1w_t*100:.1f}%概率CD转好')