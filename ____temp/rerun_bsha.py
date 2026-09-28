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
stat = defaultdict(lambda: [0,0])
for i, fname in enumerate(files):
    if i % 2000 == 0: print(f'[加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 高波池: continue
    try:
        df = pd.read_csv(os.path.join(DATA_DIR,fname), encoding='gbk', header=None, skiprows=[0], usecols=[9,13,19,21,26,44])
        df.columns = ['护型','日ZA','BSHA','管宽','次日高幅','日等型']
    except: continue
    for c in ['日ZA','BSHA','管宽','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['日ZA','次日高幅'])
    if df.empty: continue
    df['等型'] = df['日等型'].astype(str).str[1]
    df['hx'] = df['护型'].astype(str).str[0].map(HX)
    df['hit'] = (df['次日高幅']>=3).astype(int)
    # 等7/等6，BSHA<3
    for et in ['7','6']:
        d = df[(df['等型']==et) & (df['BSHA']<3)]
        if d.empty: continue
        for hx in ['乙','丙','丁']:
            sub = d[d['hx']==hx]
            if sub.empty: continue
            # 管宽分档
            for gw_name, gw_cond in [('<0', sub['管宽']<0), ('0-10', (sub['管宽']>=0)&(sub['管宽']<10)), ('≥10', sub['管宽']>=10)]:
                s = sub[gw_cond]
                stat[f'等{et}_{hx}_{gw_name}'][0]+=len(s)
                stat[f'等{et}_{hx}_{gw_name}'][1]+=int(s['hit'].sum())

print(f'\n{"数据点":<20}{"n":>8}{"P(≥3%)":>8}')
for k,(n,h) in sorted(stat.items()):
    if n>0:
        print(f'{k:<20}{n:>8}{h/n*100:>7.2f}%')
