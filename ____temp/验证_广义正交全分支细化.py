# -*- coding: utf-8 -*-
"""
广义正交护型（甲/乙/己/戊ZA>0/丙）× 日等型 全分支细化
====================================================
广义正交定义：己、戊(ZA>0)、甲、乙(ZA>0)、乙(ZA<0)、丙
非广义：戊(ZA<0)、丁
"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings, re
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
高波池板块 = {'Qic', 'Qim', 'Qit'}
hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    if not dxab_str: return ''
    return hxmap.get(dxab_str[0], '')

def parse_dxab_val(dxab_str):
    m = re.search(r'[上下忐忠忑]\s*(-?\d+)', str(dxab_str))
    if m: return int(m.group(1))
    return None

def classify_zp(zp):
    s = str(zp).strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_zx_detail(zx):
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
        df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','BT连阳','上身','柱排','柱型','顶型','日龟顶触','宽哼JC','BSHA','日ZA','日ZC'])
    except Exception:
        continue
    if len(df) < 5: continue
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    dxvals = [parse_dxab_val(s) for s in df['DXAB'].astype(str).values]
    等s = df['BT连阳'].astype(str).values
    hrs = pd.to_numeric(df['上身'], errors='coerce').values
    zps = df['柱排'].astype(str).values
    zxs = df['柱型'].astype(str).values
    txs = df['顶型'].astype(str).values
    gts = df['日龟顶触'].astype(str).values
    kws = pd.to_numeric(df['宽哼JC'], errors='coerce').values
    bshas = pd.to_numeric(df['BSHA'], errors='coerce').values
    zas = pd.to_numeric(df['日ZA'], errors='coerce').values
    zcs = pd.to_numeric(df['日ZC'], errors='coerce').values

    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        # 限定DXZC>0（广义正交护型优选的前提）
        zc = zcs[j]
        if np.isnan(zc) or zc <= 0: continue
        # 广义正交过滤：戊只取ZA>0
        if hx == '戊':
            za = zas[j]
            if np.isnan(za) or za <= 0: continue
        等 = 等s[j]
        if 等 not in ('等1','等2','等3','等5','等6','等7'): continue
        hr = hrs[j]
        zp = classify_zp(zps[j])
        zxd = classify_zx_detail(zxs[j])
        tx = txs[j]
        gt = gts[j]
        kw = kws[j]
        bsha = bshas[j]
        dxv = dxvals[j]

        # ===== 等1柱型 =====
        if 等 == '等1' and zxd:
            add(f'等1柱|{hx}|{zxd}', hr)
        # ===== 等2柱排 =====
        if 等 == '等2' and zp != '其他':
            add(f'等2柱排|{hx}|{zp}', hr)
        # ===== 等3柱排 =====
        if 等 == '等3' and zp != '其他':
            add(f'等3柱排|{hx}|{zp}', hr)
        # ===== 等3触顶 =====
        if 等 == '等3':
            if tx.startswith('上'):
                add(f'等3触|{hx}', hr)
            else:
                add(f'等3非触|{hx}', hr)
        # ===== 等3跌排×DXAB =====
        if 等 == '等3' and zp in ('跌连','跌吞','跌孕') and dxv is not None:
            if dxv <= 4:
                add(f'等3跌|{hx}|DXAB≤4', hr)
            else:
                add(f'等3跌|{hx}|DXAB>4', hr)
        # ===== 等5柱排 =====
        if 等 == '等5' and zp != '其他':
            add(f'等5柱排|{hx}|{zp}', hr)
        # ===== 等5柱型 =====
        if 等 == '等5' and zxd:
            add(f'等5柱型|{hx}|{zxd}', hr)
        # ===== 等7管宽×BSHA =====
        if 等 == '等7' and not np.isnan(kw) and not np.isnan(bsha):
            kwk = '管宽<0' if kw < 0 else ('管宽0-10' if kw < 10 else '管宽≥10')
            bsk = 'BSHA<3' if bsha < 3 else ('BSHA3-8' if bsha < 8 else 'BSHA≥8')
            add(f'等7|{hx}|{kwk}|{bsk}', hr)
        # ===== 等6管宽×BSHA =====
        if 等 == '等6' and not np.isnan(kw) and not np.isnan(bsha):
            kwk = '管宽<0' if kw < 0 else ('管宽0-10' if kw < 10 else '管宽≥10')
            bsk = 'BSHA<3' if bsha < 3 else ('BSHA3-8' if bsha < 8 else 'BSHA≥8')
            add(f'等6|{hx}|{kwk}|{bsk}', hr)

HXS = ('甲','乙','己','戊','丙')

def show(title, prefix, subkeys, hxs=HXS):
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

# ===== 等1柱型 =====
show('等1柱型（连阳 vs 单个阳柱）', '等1柱', ['单1','11连','单0','22连','单2','单3','12','13','23','44','55'])

# ===== 等2柱排 =====
show('等2柱排', '等2柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 等3柱排 =====
show('等3柱排', '等3柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 等3触顶 =====
print()
print('='*80)
print('【等3：触顶(顶型=上) vs 非触顶】')
print('='*80)
for hx in HXS:
    for k in ['等3触','等3非触']:
        s = agg[f'{k}|{hx}']
        if s[0] >= MIN_SAMPLE:
            print(f'  {hx} {k}: n={s[0]:,}  P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%')

# ===== 等3跌排×DXAB =====
show('等3跌排：DXAB≤4 vs DXAB>4', '等3跌', ['DXAB≤4','DXAB>4'])

# ===== 等5柱排 =====
show('等5柱排', '等5柱排', ['升排','人排','跌连','跌吞','跌孕'])

# ===== 等5柱型 =====
show('等5柱型（连阴/单阴/阴阳阴）', '等5柱型', ['单1','单0','单2','单3','11连','22连','33连','12','13','23','44','55'])

# ===== 等7管宽×BSHA =====
print()
print('='*80)
print('【等7：管宽 × BSHA（下跌通道）】')
print('='*80)
for hx in HXS:
    print(f'\n{hx}护型:')
    print(f'{"管宽":<10} {"BSHA":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    for kwk in ['管宽<0','管宽0-10','管宽≥10']:
        for bsk in ['BSHA<3','BSHA3-8','BSHA≥8']:
            key = f'等7|{hx}|{kwk}|{bsk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{kwk:<10} {bsk:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')

# ===== 等6管宽×BSHA =====
print()
print('='*80)
print('【等6：管宽 × BSHA（打破通道）】')
print('='*80)
for hx in HXS:
    print(f'\n{hx}护型:')
    print(f'{"管宽":<10} {"BSHA":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    for kwk in ['管宽<0','管宽0-10','管宽≥10']:
        for bsk in ['BSHA<3','BSHA3-8','BSHA≥8']:
            key = f'等6|{hx}|{kwk}|{bsk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{kwk:<10} {bsk:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')
