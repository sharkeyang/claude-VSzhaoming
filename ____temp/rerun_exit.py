import pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池 = {'Qic','Qim','Qit'}
with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)
files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('谕组日_') and f.endswith('.csv')])

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
# 统计：出管边界 -> 出管天数列表
dja_days = []
djb_days = []
for i, fname in enumerate(files):
    if i % 2000 == 0: print(f'[加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 高波池: continue
    try:
        df = pd.read_csv(os.path.join(DATA_DIR,fname), encoding='gbk', header=None, skiprows=[0], usecols=[9,13,14,62,64])
        df.columns = ['护型','日ZA','日ZC','DTZB','DTAB']
    except: continue
    for c in ['日ZA','日ZC','DTZB','DTAB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['日ZA'])
    if df.empty: continue
    df['hx'] = df['护型'].astype(str).str[0].map(HX)
    df['甲乙己'] = df['hx'].isin(['甲','乙','己'])
    df['丙丁戊'] = df['hx'].isin(['丙','丁','戊'])
    # 触哼入管：甲乙己 且 曾触哼（用上符串？这里用 DTZA>0 近似入管起点）
    # 简化：入管 = 甲乙己 且 日ZA>0（触哼后）
    # 出管DJA = 变非甲乙己 或 日ZA<0
    # 出管DJB = 变丙丁戊 或 DTZB<0
    # 跟踪：从入管开始，计算到出管的天数
    in_ab = False
    ab_start = None
    for idx in range(len(df)):
        row = df.iloc[idx]
        ab = row['甲乙己']
        za = row['日ZA']
        zb = row['DTZB']
        if not in_ab and ab and za > 0:
            in_ab = True
            ab_start = idx
        elif in_ab:
            # DJA出管：变非甲乙己 或 日ZA<0
            if (not ab) or za < 0:
                dja_days.append(idx - ab_start)
                in_ab = False
            # DJB出管：变丙丁戊 或 DTZB<0
            elif (row['丙丁戊']) or (zb is not None and zb < 0):
                djb_days.append(idx - ab_start)
                in_ab = False

print(f'\nDJA出管: n={len(dja_days)}, 平均={sum(dja_days)/len(dja_days):.2f}天' if dja_days else 'DJA无数据')
print(f'DJB出管: n={len(djb_days)}, 平均={sum(djb_days)/len(djb_days):.2f}天' if djb_days else 'DJB无数据')
