# -*- coding: utf-8 -*-
"""
DXAB护型 × 日等型 交叉关系验证
================================
验证DXAB护型（正交/负交）与日等型（等1-等7）的交叉关系。
"""
import numpy as np, pandas as pd, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 200

高波池板块 = {'Qic', 'Qim', 'Qit'}
护型序 = {'甲':0,'乙':1,'丙':2,'丁':3,'戊':4,'己':5}

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    if len(dxab_str) >= 2 and dxab_str[1] in 护型序:
        return dxab_str[1]
    return ''

def calc_等型(dtza, 末符):
    """根据DTZA和末符计算日等型"""
    if dtza == 1:
        return '等1'
    elif dtza > 0:
        if dtza >= 2 and 末符 in 'AB':
            return '等3'
        elif dtza >= 2 and 末符 in 'CDEF':
            return '等2'
    elif dtza == -1:
        return '等5'
    elif dtza < 0:
        if dtza <= -2 and 末符 in 'EF':
            return '等7'
        elif dtza <= -2 and 末符 in 'ABCD':
            return '等6'
    return ''

class Agg:
    def __init__(self):
        self.n = 0; self.sum_pr = 0.0; self.n_win = 0
        self.sum_hr = 0.0; self.n_hr_gt3 = 0
    def add(self, pr, hr=None):
        self.n += 1; self.sum_pr += float(pr)
        if float(pr) > 0: self.n_win += 1
        if hr is not None:
            hr = float(hr); self.sum_hr += hr
            if hr > 3: self.n_hr_gt3 += 1
    def stats(self):
        if self.n < MIN_SAMPLE: return None
        return {'n': self.n, 'mean': self.sum_pr/self.n, 'win': self.n_win/self.n*100,
                'mean_hr': self.sum_hr/self.n, 'hr_gt3': self.n_hr_gt3/self.n*100}

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

# 聚合: (护型, 等型) -> Agg
agg = defaultdict(Agg)
# 正交/负交 × 等型
agg_orth = defaultdict(Agg)  # 正交(甲乙) × 等型
agg_neg = defaultdict(Agg)   # 负交(丙丁戊己) × 等型

for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  [{i}/{len(files)}]...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5: continue
    except: continue

    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池板块: continue

    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    dtza = df['日ZA'].astype(float).values
    中符串 = df['中符串'].astype(str).values
    prs = df['涨幅'].astype(float).values
    hrs = df['次日高幅'].astype(float).values

    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        末符 = 中符串[j][-1] if len(中符串[j]) > 0 else ''
        等型 = calc_等型(dtza[j], 末符)
        if not 等型: continue

        agg[(hx, 等型)].add(prs[j], hrs[j])
        if hx in '甲乙':
            agg_orth[等型].add(prs[j], hrs[j])
        else:
            agg_neg[等型].add(prs[j], hrs[j])

print()
print('='*70)
print('DXAB护型 × 日等型 交叉关系')
print('='*70)

# 输出护型×等型矩阵
print()
print('=== 各护型 × 各等型（均涨幅/涨率） ===')
print('| 护型 | 等1 | 等2 | 等3 | 等5 | 等6 | 等7 |')
print('|:----|:---:|:---:|:---:|:---:|:---:|:---:|')
for hx in '甲乙丙丁戊己':
    row = []
    for 等 in ['等1','等2','等3','等5','等6','等7']:
        s = agg[(hx, 等)].stats()
        if s:
            row.append(f'{s["mean"]:+.2f}%/{s["win"]:.0f}%')
        else:
            row.append('-')
    print(f'| {hx} | ' + ' | '.join(row) + ' |')

# 正交 vs 负交 × 等型
print()
print('=== 正交(甲乙) vs 负交(丙丁戊己) × 等型 ===')
print('| 等型 | 正交均涨 | 正交涨率 | 负交均涨 | 负交涨率 | 差异 |')
print('|:----|:--------:|:--------:|:--------:|:--------:|:----:|')
for 等 in ['等1','等2','等3','等5','等6','等7']:
    so = agg_orth[等].stats()
    sn = agg_neg[等].stats()
    if so and sn:
        diff = so['mean'] - sn['mean']
        print(f'| {等} | {so["mean"]:+.2f}% | {so["win"]:.1f}% | {sn["mean"]:+.2f}% | {sn["win"]:.1f}% | {diff:+.2f}pp |')
    elif so:
        print(f'| {等} | {so["mean"]:+.2f}% | {so["win"]:.1f}% | - | - | - |')
    elif sn:
        print(f'| {等} | - | - | {sn["mean"]:+.2f}% | {sn["win"]:.1f}% | - |')

# 关键交叉场景
print()
print('=== 关键交叉场景 ===')
print('| 场景 | 样本 | 均涨幅 | 涨率 | 均明高 | 明高>3% |')
print('|:----|:----:|:-----:|:---:|:-----:|:------:|')

# 场景1: 正交 + 等3（DJA上方强势）
s = agg_orth['等3'].stats()
if s: print(f'| 正交+等3(上方强势) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景2: 正交 + 等2（DJA上方回归）
s = agg_orth['等2'].stats()
if s: print(f'| 正交+等2(上方回归) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景3: 正交 + 等1（刚站上DJA）
s = agg_orth['等1'].stats()
if s: print(f'| 正交+等1(刚站上) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景4: 负交 + 等3（DJA上方强势但护型负交）
s = agg_neg['等3'].stats()
if s: print(f'| 负交+等3(上方强势) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景5: 负交 + 等6（DJA下方偏强）
s = agg_neg['等6'].stats()
if s: print(f'| 负交+等6(下方偏强) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景6: 负交 + 等7（DJA下方弱势）
s = agg_neg['等7'].stats()
if s: print(f'| 负交+等7(下方弱势) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景7: 己 + 等6（己在DJA下方偏强）
s = agg[('己', '等6')].stats()
if s: print(f'| 己+等6(下方偏强) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景8: 己 + 等1（己刚站上DJA）
s = agg[('己', '等1')].stats()
if s: print(f'| 己+等1(刚站上) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景9: 丁 + 等6（丁在DJA下方偏强）
s = agg[('丁', '等6')].stats()
if s: print(f'| 丁+等6(下方偏强) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 场景10: 戊 + 等6（戊在DJA下方偏强）
s = agg[('戊', '等6')].stats()
if s: print(f'| 戊+等6(下方偏强) | {s["n"]} | {s["mean"]:+.2f}% | {s["win"]:.1f}% | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')