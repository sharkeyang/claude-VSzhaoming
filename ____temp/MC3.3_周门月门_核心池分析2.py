# -*- coding: utf-8 -*-
"""§3.1周门验证 + §3.2月门交叉 核心池全量分析"""
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
print(f'核心池文件: {len(core_files)}')

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
# §3.1: 满足周门n / 满足周门且ZE>0 / 不满足周门n / 不满足周门且ZE>0
z1 = defaultdict(lambda: {'zm_n':0,'zm_ze':0,'nzm_n':0,'nzm_ze':0})
# §3.2: ZE>0样本/冲2/冲3, ZE≤0样本/冲2
z2 = defaultdict(lambda: {'ze_n':0,'ze_nh2':0,'ze_nh3':0,'nze_n':0,'nze_nh2':0})

for fi, f in enumerate(core_files):
    try:
        df = pd.read_csv(f, encoding='gbk', low_memory=False,
                         usecols=['日ZA','中符串','次日高幅','日ZC','DXCD','日ZE'])
    except: continue
    if len(df) < 100: continue
    za = df['日ZA'].astype(float); mid = df['中符串'].astype(str)
    last = mid.str[-1]; nh = df['次日高幅'].astype(float)
    zc = df['日ZC'].astype(float); ze = df['日ZE'].astype(float)
    dxcd = df['DXCD'].astype(str)
    zhoumen = (zc > 0) & (dxcd == '上')
    yuemeng = ze > 0

    for idx in df.index:
        c6 = classify_6(za[idx], last[idx])
        if c6 == 'NA': continue
        nhv = nh[idx]; zm = zhoumen[idx]; ym = yuemeng[idx]
        # §3.1
        s = z1[c6]
        if zm:
            s['zm_n'] += 1
            if ym: s['zm_ze'] += 1
        else:
            s['nzm_n'] += 1
            if ym: s['nzm_ze'] += 1
        # §3.2
        s2 = z2[c6]
        if ym:
            s2['ze_n'] += 1
            if not pd.isna(nhv):
                if nhv > 2: s2['ze_nh2'] += 1
                if nhv > 3: s2['ze_nh3'] += 1
        else:
            s2['nze_n'] += 1
            if not pd.isna(nhv) and nhv > 2: s2['nze_nh2'] += 1

    if (fi+1) % 1000 == 0: print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s')

print(f'\n全量处理完成, 耗时 {time.time()-t0:.0f}s')

print('\n=== §3.1 周门验证 ===')
print(f'{"分类":<12} {"满足周门n":>10} {"→ZE>0":>7} {"不满足周门n":>10} {"→ZE>0":>7}')
for c in ['等1','等2','等3','等5','等6','等7']:
    s = z1[c]
    zm_pct = s['zm_ze']/s['zm_n']*100 if s['zm_n'] else 0
    nzm_pct = s['nzm_ze']/s['nzm_n']*100 if s['nzm_n'] else 0
    print(f'{c:<12} {s["zm_n"]:>10,} {zm_pct:>6.1f}% {s["nzm_n"]:>10,} {nzm_pct:>6.1f}%')

print('\n=== §3.2 月门与等高线交叉 ===')
print(f'{"分类":<12} {"ZE>0样本":>10} {"冲≥2%":>8} {"冲≥3%":>8} {"ZE≤0冲≥2%":>10}')
for c in ['等1','等2','等3','等5','等6','等7']:
    s = z2[c]
    ze2 = s['ze_nh2']/s['ze_n']*100 if s['ze_n'] else 0
    ze3 = s['ze_nh3']/s['ze_n']*100 if s['ze_n'] else 0
    nze2 = s['nze_nh2']/s['nze_n']*100 if s['nze_n'] else 0
    print(f'{c:<12} {s["ze_n"]:>10,} {ze2:>7.1f}% {ze3:>7.1f}% {nze2:>9.1f}%')