# -*- coding: utf-8 -*-
"""§2.2 逐层对比 核心池全量"""
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
stats = defaultdict(lambda: {'n':0,'nh0':0,'nh1':0,'nh2':0,'nh3':0,'nh5':0})
for fi, f in enumerate(core_files):
    try:
        df = pd.read_csv(f, encoding='gbk', low_memory=False, usecols=['日ZA','中符串','次日高幅'])
    except: continue
    if len(df) < 100: continue
    za = df['日ZA'].astype(float); mid = df['中符串'].astype(str)
    last = mid.str[-1]; nh = df['次日高幅'].astype(float)
    for idx in df.index:
        c6 = classify_6(za[idx], last[idx])
        if c6 == 'NA': continue
        s = stats[c6]; nhv = nh[idx]
        s['n'] += 1
        if not pd.isna(nhv):
            if nhv >= 0: s['nh0'] += 1
            if nhv >= 1: s['nh1'] += 1
            if nhv >= 2: s['nh2'] += 1
            if nhv >= 3: s['nh3'] += 1
            if nhv >= 5: s['nh5'] += 1
    if (fi+1) % 1000 == 0: print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s')

print(f'\n耗时 {time.time()-t0:.0f}s')
print(f'\n分类,样本,占比,≥0%,≥1%,≥2%,≥3%,≥5%')
for c in ['等1','等2','等3','等5','等6','等7']:
    s = stats[c]
    n0 = s['nh0']/s['n']*100; n1 = s['nh1']/s['n']*100
    n2 = s['nh2']/s['n']*100; n3 = s['nh3']/s['n']*100; n5 = s['nh5']/s['n']*100
    print(f'{c},{s["n"]},,{n0:.1f}%,{n1:.1f}%,{n2:.1f}%,{n3:.1f}%,{n5:.1f}%')