# -*- coding: utf-8 -*-
"""
DXAB广义正交护型（甲/乙/己）× 日等型（等1/等2/等3/等5/等6/等7）交叉分析
=====================================================================
数据列（pandas列名，与CSV表头一致）：
  DXAB[9] 第1字符 = 护型（a=甲, b=乙, r=己）
  BT连阳[44] = 日等型（等1/等2/等3/等5/等6/等7）
  上身[26] = 次日高幅（数值）
  柱排[10] = 柱排形态
  顶型[45] = 顶型
  柱型[29] = 柱型（数值）
  日ZA[13] = DTZA
  日ZC[14] = 日ZC
  宽哼JC[24] = 管宽JC
  BSHA[21] = 偏离DJA
  日龟顶触[55] = 触顶状态
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
    """DXAB第1字符：a=甲, b=乙, r=己"""
    if not dxab_str: return ''
    c = dxab_str[0]
    return {'a':'甲','b':'乙','r':'己'}.get(c, '')

def classify_zp(zp):
    """柱排分类"""
    s = str(zp).strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_zx(zx):
    """柱型[29]分类：0=阴,1=阳,2=阴,3=阴,4=枝,5=阳,9=连阳"""
    s = str(zx).strip()
    if not s: return None
    d = s[0]
    return {'9':'连阳','5':'阳','4':'枝','0':'阴','1':'阳','2':'阴','3':'阴'}.get(d, None)

def classify_顶型(tx):
    """顶型分类：触顶(上)/中/下/忐/忠/忑/无"""
    s = str(tx).strip()
    if not s or s == '无': return '无'
    return s[0]  # 上/中/下/忐/忠/忑

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

# 聚合: (护型, 等型) -> [n, hr3, sum_hr]
agg = defaultdict(lambda: [0,0,0.0])
# 各护型基线
agg_hx = defaultdict(lambda: [0,0,0.0])
# 各等型基线
agg_等 = defaultdict(lambda: [0,0,0.0])

for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  [{i}/{len(files)}]...', flush=True)
    code = os.path.basename(f).replace('谕组日_','').replace('.csv','')
    board = board_map.get(code, '')
    if board not in 高波池板块: continue
    try:
        df = pd.read_csv(f, encoding='gbk', usecols=['DXAB','BT连阳','上身','日ZA','日ZC'])
    except Exception:
        continue
    if len(df) < 5: continue
    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    等s = df['BT连阳'].astype(str).values
    hrs = pd.to_numeric(df['上身'], errors='coerce').values
    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        等 = 等s[j]
        if 等 not in ('等1','等2','等3','等5','等6','等7'): continue
        hr = hrs[j]
        if np.isnan(hr) or hr < -50 or hr > 50: continue
        agg[(hx, 等)][0]+=1; agg[(hx, 等)][1]+= (1 if hr>=3 else 0); agg[(hx, 等)][2]+=hr
        agg_hx[hx][0]+=1; agg_hx[hx][1]+= (1 if hr>=3 else 0); agg_hx[hx][2]+=hr
        agg_等[等][0]+=1; agg_等[等][1]+= (1 if hr>=3 else 0); agg_等[等][2]+=hr

print()
print('='*80)
print('【基础矩阵】甲/乙/己 × 日等型：P(次日高幅≥3%) / 均次日高幅')
print('='*80)
print(f'{"护型":<4} {"等1":>16} {"等2":>16} {"等3":>16} {"等5":>16} {"等6":>16} {"等7":>16} {"基线":>16}')
for hx in ['甲','乙','己']:
    row = []
    for 等 in ['等1','等2','等3','等5','等6','等7']:
        s = agg[(hx, 等)]
        if s[0] >= MIN_SAMPLE:
            row.append(f'{s[1]/s[0]*100:.1f}%/{s[2]/s[0]:.2f}%({s[0]:,})')
        else:
            row.append('-')
    s = agg_hx[hx]
    row.append(f'{s[1]/s[0]*100:.1f}%/{s[2]/s[0]:.2f}%({s[0]:,})')
    print(f'{hx:<4} ' + ' '.join(f'{x:>16}' for x in row))

print()
print('【各等型基线】')
for 等 in ['等1','等2','等3','等5','等6','等7']:
    s = agg_等[等]
    if s[0] >= MIN_SAMPLE:
        print(f'  {等}: P(≥3%)={s[1]/s[0]*100:.1f}%  均高幅={s[2]/s[0]:.2f}%  n={s[0]:,}')
