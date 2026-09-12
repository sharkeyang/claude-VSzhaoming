# -*- coding: utf-8 -*-
"""
甲乙己 × 日等型 各分支微观指标细化
=================================
1. 等1：柱型（连阳 vs 单个阳柱）
2. 等3：柱排（升排/人排/跌排）+ 顶型（触顶/合顶）
3. 等2：柱排（跌排中的升孕）
4. 等5：柱排（连阴/单阴/阴阳阴）
5. 等7：管宽（下跌通道）
6. 等6：管宽（打破通道）
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

def classify_zx(zx):
    """柱型[29]：0=阴,1=阳,2=阴,3=阴,4=枝,5=阳,9=连阳"""
    s = str(zx).strip()
    if not s: return None
    d = s[0]
    return {'9':'连阳','5':'阳','4':'枝','0':'阴','1':'阳','2':'阴','3':'阴'}.get(d, None)

def classify_顶型(tx):
    s = str(tx).strip()
    if not s or s == '无': return '无'
    return s[0]

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

# 聚合结构: key -> [n, hr3, sum_hr]
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
        df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','BT连阳','上身','柱排','顶型','柱型','宽哼JC','BSHA','日ZA'])
    except Exception:
        continue
    if len(df) < 5: continue
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    等s = df['BT连阳'].astype(str).values
    hrs = pd.to_numeric(df['上身'], errors='coerce').values
    zps = df['柱排'].astype(str).values
    txs = df['顶型'].astype(str).values
    zxs = df['柱型'].astype(str).values
    kws = pd.to_numeric(df['宽哼JC'], errors='coerce').values
    bshas = pd.to_numeric(df['BSHA'], errors='coerce').values

    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        等 = 等s[j]
        if 等 not in ('等1','等2','等3','等5','等6','等7'): continue
        hr = hrs[j]
        zp = classify_zp(zps[j])
        zx = classify_zx(zxs[j])
        tx = classify_顶型(txs[j])
        kw = kws[j]
        bsha = bshas[j]

        # ===== 1. 等1：柱型（连阳 vs 单阳）=====
        if 等 == '等1' and zx:
            add(f'等1|柱型|{hx}|{zx}', hr)
        # ===== 2. 等3：柱排 + 顶型 =====
        if 等 == '等3' and zp != '其他':
            add(f'等3|柱排|{hx}|{zp}', hr)
            if tx != '无':
                add(f'等3|柱排顶|{hx}|{zp}|{tx}', hr)
        # ===== 3. 等2：柱排 =====
        if 等 == '等2' and zp != '其他':
            add(f'等2|柱排|{hx}|{zp}', hr)
        # ===== 4. 等5：柱排 =====
        if 等 == '等5' and zp != '其他':
            add(f'等5|柱排|{hx}|{zp}', hr)
        # ===== 5. 等7：管宽 =====
        if 等 == '等7' and not np.isnan(kw):
            kwk = '管宽<0' if kw < 0 else ('管宽0-10' if kw < 10 else '管宽≥10')
            add(f'等7|管宽|{hx}|{kwk}', hr)
        # ===== 6. 等6：管宽 =====
        if 等 == '等6' and not np.isnan(kw):
            kwk = '管宽<0' if kw < 0 else ('管宽0-10' if kw < 10 else '管宽≥10')
            add(f'等6|管宽|{hx}|{kwk}', hr)

def show(title, prefix, subkeys, hxs=('甲','乙','己')):
    print()
    print('='*80)
    print(f'【{title}】')
    print('='*80)
    for hx in hxs:
        print(f'\n{hx}护型:')
        print(f'{"分支":<14} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
        for sk in subkeys:
            key = f'{prefix}|{hx}|{sk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{sk:<14} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')

# ===== 1. 等1：柱型 =====
show('等1：柱型（连阳 vs 单个阳柱）', '等1|柱型', ['连阳','阳','阴','枝'])

# ===== 2. 等3：柱排 =====
show('等3：柱排（升排/人排/跌排）', '等3|柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 3. 等2：柱排 =====
show('等2：柱排', '等2|柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 4. 等5：柱排 =====
show('等5：柱排（连阴/单阴/阴阳阴）', '等5|柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 5. 等7：管宽 =====
show('等7：管宽（下跌通道）', '等7|管宽', ['管宽<0','管宽0-10','管宽≥10'])

# ===== 6. 等6：管宽 =====
show('等6：管宽（打破通道）', '等6|管宽', ['管宽<0','管宽0-10','管宽≥10'])

# ===== 等3：柱排×顶型（触顶/合顶）=====
print()
print('='*80)
print('【等3：柱排 × 顶型（触顶/合顶）】')
print('='*80)
for hx in ['甲','乙','己']:
    print(f'\n{hx}护型:')
    print(f'{"柱排":<8} {"顶型":<6} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    for zp in ['升排','人排','跌连','跌吞','跌孕']:
        for tx in ['上','中','下','忐','忠','忑']:
            key = f'等3|柱排顶|{hx}|{zp}|{tx}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{zp:<8} {tx:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')
