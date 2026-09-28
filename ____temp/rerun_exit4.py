import pandas as pd, os, json, warnings, numpy as np
warnings.filterwarnings('ignore')

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池 = {'Qic','Qim','Qit'}
with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)
files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('谕组日_') and f.endswith('.csv')])

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
dja_days = []
djb_days = []
for i, fname in enumerate(files):
    if i % 2000 == 0: print(f'[加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 高波池: continue
    try:
        df = pd.read_csv(os.path.join(DATA_DIR,fname), encoding='gbk', header=None, skiprows=[0], usecols=[9,13,62])
        df.columns = ['护型','日ZA','DTZB']
    except: continue
    for c in ['日ZA','DTZB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['日ZA'])
    if df.empty: continue
    df['hx'] = df['护型'].astype(str).str[0].map(HX)
    ab = df['hx'].isin(['甲','乙','己']).values
    cd = df['hx'].isin(['丙','丁','戊']).values
    za = df['日ZA'].values
    zb = df['DTZB'].values
    n = len(df)
    # 入管起点：甲乙己 且 日ZA>0
    entry = ab & (za > 0)
    # DJA出管：变非甲乙己 或 日ZA<0
    dja_exit = (~ab) | (za < 0)
    # DJB出管：变丙丁戊 或 DTZB<0
    djb_exit = cd | ((~np.isnan(zb)) & (zb < 0))
    # 对每个入管起点，找后续第一个出管点
    for idx in np.where(entry)[0]:
        # DJA
        after = dja_exit[idx+1:]
        hit = np.where(after)[0]
        if len(hit) > 0:
            dja_days.append(hit[0] + 1)
        # DJB
        after_b = djb_exit[idx+1:]
        hit_b = np.where(after_b)[0]
        if len(hit_b) > 0:
            djb_days.append(hit_b[0] + 1)

print(f'\nDJA出管: n={len(dja_days)}, 平均={np.mean(dja_days):.2f}天' if dja_days else 'DJA无数据')
print(f'DJB出管: n={len(djb_days)}, 平均={np.mean(djb_days):.2f}天' if djb_days else 'DJB无数据')
