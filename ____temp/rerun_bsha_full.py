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
    for et in ['7','6']:
        d = df[df['等型']==et]
        if d.empty: continue
        for hx in ['乙','丙','丁']:
            sub = d[d['hx']==hx]
            if sub.empty: continue
            for gw_name, gw_cond in [('<0', sub['管宽']<0), ('0-10', (sub['管宽']>=0)&(sub['管宽']<10)), ('≥10', sub['管宽']>=10)]:
                s = sub[gw_cond]
                for bs_name, bs_cond in [('<3', s['BSHA']<3), ('3-8', (s['BSHA']>=3)&(s['BSHA']<8)), ('≥8', s['BSHA']>=8)]:
                    b = s[bs_cond]
                    stat[f'等{et}_{hx}_{gw_name}_{bs_name}'][0]+=len(b)
                    stat[f'等{et}_{hx}_{gw_name}_{bs_name}'][1]+=int(b['hit'].sum())

# 输出表格格式
print(f'\n=== 等7 BSHA三档（按护型×管宽）===')
print(f'{"护型":<8}{"管宽":<6}{"BSHA<3":>8}{"BSHA3-8":>8}{"BSHA≥8":>8}')
for hx in ['乙','丙','丁']:
    for gw in ['<0','0-10','≥10']:
        row = []
        for bs in ['<3','3-8','≥8']:
            k = f'等7_{hx}_{gw}_{bs}'
            n,h = stat[k]
            row.append(f'{h/n*100:>7.1f}%' if n>0 else '   —  ')
        print(f'{hx:<8}{gw:<6}{row[0]}{row[1]}{row[2]}')

print(f'\n=== 等6 BSHA三档（按护型×管宽）===')
print(f'{"护型":<8}{"管宽":<6}{"BSHA<3":>8}{"BSHA3-8":>8}{"BSHA≥8":>8}')
for hx in ['乙','丙','丁']:
    for gw in ['<0','0-10','≥10']:
        row = []
        for bs in ['<3','3-8','≥8']:
            k = f'等6_{hx}_{gw}_{bs}'
            n,h = stat[k]
            row.append(f'{h/n*100:>7.1f}%' if n>0 else '   —  ')
        print(f'{hx:<8}{gw:<6}{row[0]}{row[1]}{row[2]}')
