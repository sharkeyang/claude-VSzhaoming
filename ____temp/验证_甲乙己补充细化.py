# -*- coding: utf-8 -*-
"""
补充细化：等3跌排DXAB范围 + 等5柱型 + 等7/等6管宽×BSHA
=====================================================
DXAB格式：a甲↗上3.A4 → 提取数值3（上=正ZA）
"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings, re
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

def parse_dxab_val(dxab_str):
    """提取DXAB数值：a甲↗上3.A4 → 3"""
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

def classify_zx2(zx):
    """柱型[29]两位数字：11=连阳, 22=连阴, 12=阳阴, 13=阳阴, 23=阴阴, 单=单柱"""
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
        df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','BT连阳','上身','柱排','柱型','宽哼JC','BSHA'])
    except Exception:
        continue
    if len(df) < 5: continue
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    dxvals = [parse_dxab_val(s) for s in df['DXAB'].astype(str).values]
    等s = df['BT连阳'].astype(str).values
    hrs = pd.to_numeric(df['上身'], errors='coerce').values
    zps = df['柱排'].astype(str).values
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
        zx2 = classify_zx2(zxs[j])
        dxv = dxvals[j]
        kw = kws[j]
        bsha = bshas[j]

        # ===== 等3跌排 × DXAB数值 =====
        if 等 == '等3' and zp in ('跌连','跌吞','跌孕') and dxv is not None:
            if dxv <= 4:
                add(f'等3跌|{hx}|DXAB≤4', hr)
            else:
                add(f'等3跌|{hx}|DXAB>4', hr)
        # ===== 等5柱型 =====
        if 等 == '等5' and zx2:
            add(f'等5柱型|{hx}|{zx2}', hr)
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

def show(title, prefix, subkeys, hxs=('甲','乙','己')):
    print()
    print('='*80)
    print(f'【{title}】')
    print('='*80)
    for hx in hxs:
        print(f'\n{hx}护型:')
        print(f'{"分支":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
        for sk in subkeys:
            key = f'{prefix}|{hx}|{sk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{sk:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')

# ===== 等3跌排 × DXAB =====
show('等3跌排：DXAB≤4 vs DXAB>4（验证跌排是否维持升势）', '等3跌', ['DXAB≤4','DXAB>4'])

# ===== 等5柱型 =====
show('等5柱型（连阴/单阴/阴阳阴）', '等5柱型', ['单1','单0','单2','单3','11连','22连','33连','12','13','23','44','55'])

# ===== 等7管宽×BSHA =====
print()
print('='*80)
print('【等7：管宽 × BSHA（下跌通道）】')
print('='*80)
for hx in ['甲','乙','己']:
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
for hx in ['甲','乙','己']:
    print(f'\n{hx}护型:')
    print(f'{"管宽":<10} {"BSHA":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    for kwk in ['管宽<0','管宽0-10','管宽≥10']:
        for bsk in ['BSHA<3','BSHA3-8','BSHA≥8']:
            key = f'等6|{hx}|{kwk}|{bsk}'
            s = agg[key]
            if s[0] >= MIN_SAMPLE:
                print(f'{kwk:<10} {bsk:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.1f}% {s[2]/s[0]:>7.2f}%')
