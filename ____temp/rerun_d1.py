import pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池 = {'Qic','Qim','Qit'}
with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)
files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('谕组日_') and f.endswith('.csv')])

HX = {'a':'甲','b':'乙','r':'己'}
stat = defaultdict(lambda: [0,0])
for i, fname in enumerate(files):
    if i % 2000 == 0: print(f'[加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_','').replace('.csv','')
    if board_map.get(cidl,'') not in 高波池: continue
    try:
        df = pd.read_csv(os.path.join(DATA_DIR,fname), encoding='gbk', header=None, skiprows=[0], usecols=[9,13,14,26,27,44])
        df.columns = ['护型','日ZA','日ZC','次日高幅','柱型','日等型']
    except: continue
    for c in ['日ZA','日ZC','次日高幅']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['日ZA','次日高幅'])
    if df.empty: continue
    df['等型'] = df['日等型'].astype(str).str[1]
    df['hx'] = df['护型'].astype(str).str[0].map(HX)
    df['hit'] = (df['次日高幅']>=3).astype(int)
    zx = df['柱型'].astype(str)
    df['连阳'] = zx.str.contains('连')
    df['单阳'] = zx.str.contains('单') & ~zx.str.contains('阴')
    d = df[(df['等型']=='1') & (df['日ZC']>0) & (df['hx'].notna())]
    if d.empty: continue
    for hx in ['甲','乙','己']:
        sub = d[d['hx']==hx]
        for tag, m in [('连阳','连阳'),('单阳','单阳')]:
            s = sub[sub[m]]
            stat[f'{hx}_{tag}'][0]+=len(s)
            stat[f'{hx}_{tag}'][1]+=int(s['hit'].sum())

print(f'\n{"数据点":<12}{"n":>8}{"P(≥3%)":>8}')
for k,(n,h) in sorted(stat.items()):
    print(f'{k:<12}{n:>8}{h/n*100:>7.2f}%')
