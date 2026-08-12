# -*- coding: utf-8 -*-
"""§2.4 下柱≥2%天数比 + 下柱高幅/低幅均值 核心池全量"""
import numpy as np, pandas as pd, os, glob, json, time, warnings
from collections import defaultdict
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
MAPPING_FILE = r'D:\@VSwork\VS昭明计划VBA优化\_产出物\MP1_花册分类映射.json'
CORE_BOARDS = {'中证500', '中证小盘', '中证非'}
with open(MAPPING_FILE, encoding='utf-8') as f:
    huace = json.load(f)
core_codes = set(k for k, v in huace.items() if v in CORE_BOARDS)
all_files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
core_files = [f for f in all_files if os.path.basename(f).replace('谕组日_','').replace('.csv','') in core_codes]

def classify_6(za, last):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); lc = str(last) if pd.notna(last) else ''
    ab = lc in 'AB'; cdef = lc in 'CDEF'; abcd = lc in 'ABCD'; ef = lc in 'EF'
    if za > 0:
        if za == 1: return '等1'
        elif za >= 2 and ab: return '等3'
        elif za >= 2 and cdef: return '等2'
    elif za < 0:
        if za == -1: return '等5'
        elif za <= -2 and abcd: return '等6'
        elif za <= -2 and ef: return '等7'
    return 'NA'

t0 = time.time()
stats = defaultdict(lambda: {'n':0, 'nh2':0, 'h_sum':0.0, 'l_sum':0.0, 'r_sum':0.0})

for fi, f in enumerate(core_files):
    try:
        df = pd.read_csv(f, encoding='gbk', low_memory=False, usecols=['日ZA','中符串','次日高幅','收','低','涨幅'])
    except: continue
    if len(df) < 100: continue
    za = df['日ZA'].astype(float); mid = df['中符串'].astype(str)
    last = mid.str[-1]; nh = df['次日高幅'].astype(float)
    low = df['低'].astype(float); close = df['收'].astype(float)
    # 计算次日低幅和次日涨幅
    next_low = low.shift(-1); next_close = close.shift(-1)
    nl_pct = (next_low - close) / close * 100  # 次日低幅
    nc_pct = (next_close - close) / close * 100  # 次日涨幅

    for idx in df.index:
        c6 = classify_6(za[idx], last[idx])
        if c6 == 'NA': continue
        s = stats[c6]; s['n'] += 1
        hv = nh[idx]; lv = nl_pct[idx]; rv = nc_pct[idx]
        if not pd.isna(hv):
            if hv > 2: s['nh2'] += 1
            s['h_sum'] += hv
        if not pd.isna(lv): s['l_sum'] += abs(lv)  # 低幅取绝对值
        if not pd.isna(rv): s['r_sum'] += rv

    if (fi+1) % 1000 == 0: print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s')

print(f'\n耗时 {time.time()-t0:.0f}s')
print(f'\n{"分类":<8} {"样本":>10} {"≥2%天数比":>10} {"高幅均值":>8} {"低幅均值":>8} {"幅度比":>8} {"期望收益/天":>10}')
for c in ['等1','等2','等3','等5','等6','等7']:
    s = stats[c]
    n = s['n']
    pct2 = s['nh2']/n*100
    h_avg = s['h_sum']/n if n else 0
    l_avg = s['l_sum']/n if n else 0
    ratio = h_avg/l_avg if l_avg else 0
    # 期望收益 = 高幅均值 - 低幅均值
    exp = h_avg - l_avg
    print(f'{c:<8} {n:>10,} {pct2:>9.1f}% {h_avg:>7.2f}% {l_avg:>7.2f}% {ratio:>7.2f} {exp:>+9.3f}%')