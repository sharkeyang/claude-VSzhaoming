# -*- coding: utf-8 -*-
"""
补充细化2：等1连阳vs单阳 + 等2跌孕 + 等3触顶合顶
================================================
"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
高波池板块 = {'Qic', 'Qim', 'Qit'}

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    if not dxab_str: return ''
    c = dxab_str[0]
    return {'a':'甲','b':'乙','r':'己'}.get(c, '')

def classify_zp(zp):
    s = str(zp).strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_zx_detail(zx):
    """柱型[29]细分：单1=单个阳柱, 11=连阳, 单0=单阴, 22=连阴, 12=阳阴, 13=阳阴"""
    s = str(zx).strip()
    if not s: return None
    if len(s) >= 2:
        a, b = s[0], s[1]
        if a == b and a in '123': return f'{a}{b}连'
        return f'{a}{b}'
    return f'单{s}'

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

agg = defaultdict(lambda: [0,0,0.0])

def add(key, hr):
    if np.isnan(hr) or hr < -50 or hr > 50: return
    agg[key][0]+=1; agg[key][1]+= (1 if hr>=3 else 0); agg[key][2]+=hr

for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  [{i}/{len(files)}]...', flush=True)
    code = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    board = board_map.get(code, '')
    if board not in 高波池板块: continue
    try:
        df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','BT连阳','上身','柱排','柱型','顶型','日龟顶触'])
    except Exception:
        continue
    if len(df) < 5: continue
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    等s = df['BT连阳'].astype(str).values
    hrs = pd.to_numeric(df['上身'], errors='coerce').values
    zps = df['柱排'].astype(str).values
    zxs = df['柱型'].astype(str).values
    txs = df['顶型'].astype(str).values
    gts = df['日龟顶触'].astype(str).values

    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        等 = 等s[j]
        if 等 not in ('等1','等2','等3','等5','等6','等7'): continue
        hr = hrs[j]
        zp = classify_zp(zps[j])
        zxd = classify_zx_detail(zxs[j])
        tx = txs[j]
        gt = gts[j]

        # ===== 等1柱型细分 =====
        if 等 == '等1' and zxd:
            add(f'等1柱|{hx}|{zxd}', hr)
        # ===== 等2跌孕 =====
        if 等 == '等2' and zp == '跌孕':
            add(f'等2孕|{hx}', hr)
        # ===== 等3触顶(顶型=上) vs 非触顶 =====
        if 等 == '等3':
            if tx.startswith('上'):
                add(f'等3触|{hx}', hr)
            else:
                add(f'等3非触|{hx}', hr)
        # ===== 等3合顶(日龟顶触含G) =====
        if 等 == '等3':
            if gt.startswith('G'):
                add(f'等3G|{hx}', hr)
            else:
                add(f'等3非G|{hx}', hr)

def show(title, prefix, subkeys, hxs=('甲','乙','己')):
    print()
    print('='*80)
    print(f'【{title}】')
    print('='*80)
    for hx in hxs:
        print(f'\n{hx}护型:')
        print(f'{"分支":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
        for sk in subkeys:
            key = f'{prefix}|{hx}|{sk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{sk:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')

# ===== 等1柱型细分 =====
show('等1柱型细分（连阳 vs 单个阳柱 vs 连阴）', '等1柱', ['单1','11连','单0','22连','单2','单3','12','13','23','44','55'])

# ===== 等2跌孕 =====
print()
print('='*80)
print('【等2跌孕】')
print('='*80)
for hx in ['甲','乙','己']:
    s = agg[f'等2孕|{hx}']
    if s[0] >= MIN_SAMPLE:
        print(f'  {hx}: n={s[0]:,}  P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%')

# ===== 等3触顶 vs 非触顶 =====
print()
print('='*80)
print('【等3：触顶(顶型=上) vs 非触顶】')
print('='*80)
for hx in ['甲','乙','己']:
    for k in ['等3触','等3非触']:
        s = agg[f'{k}|{hx}']
        if s[0] >= MIN_SAMPLE:
            print(f'  {hx} {k}: n={s[0]:,}  P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%')

# ===== 等3合顶(G) vs 非G =====
print()
print('='*80)
print('【等3：合顶(日龟顶触含G) vs 非G】')
print('='*80)
for hx in ['甲','乙','己']:
    for k in ['等3G','等3非G']:
        s = agg[f'{k}|{hx}']
        if s[0] >= MIN_SAMPLE:
            print(f'  {hx} {k}: n={s[0]:,}  P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%')
