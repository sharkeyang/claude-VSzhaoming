# -*- coding: utf-8 -*-
"""§2.4 下柱指标 核心池全量 v2"""
import numpy as np, pandas as pd, os, glob, json, time, warnings
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
# Use separate float accumulators
n_arr = [0]*7
nh2_arr = [0.0]*7
h_sum_arr = [0.0]*7
l_sum_arr = [0.0]*7
r_sum_arr = [0.0]*7
cls_map = {'等1':0,'等2':1,'等3':2,'等5':3,'等6':4,'等7':5}
cls_list = ['等1','等2','等3','等5','等6','等7']

for fi, f in enumerate(core_files):
    try:
        df = pd.read_csv(f, encoding='gbk', low_memory=False, usecols=['日ZA','中符串','次日高幅','收','低'])
    except: continue
    if len(df) < 100: continue
    za = df['日ZA'].astype(float).values
    mid = df['中符串'].astype(str).values
    nh = df['次日高幅'].astype(float).values
    close = df['收'].astype(float).values
    low = df['低'].astype(float).values

    # 次日低幅 = (shift(-1)低 - 收) / 收 * 100
    next_low = np.roll(low, -1)
    next_low[-1] = np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        nl_pct = (next_low - close) / close * 100
    nl_pct[(close == 0) | np.isnan(close)] = np.nan  # 收=0数据错，剔除

    for idx in range(len(df)):
        last = str(mid[idx])[-1] if pd.notna(mid[idx]) else ''
        c6 = classify_6(za[idx], last)
        if c6 == 'NA': continue
        ci = cls_map[c6]
        n_arr[ci] += 1
        hv = nh[idx]; lv = nl_pct[idx]
        if not pd.isna(hv):
            if hv > 2: nh2_arr[ci] += 1
            h_sum_arr[ci] += hv
        if not pd.isna(lv):
            l_sum_arr[ci] += abs(lv)

    if (fi+1) % 1000 == 0: print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s')

print(f'\n耗时 {time.time()-t0:.0f}s')
print(f'\n{"分类":<8} {"样本":>10} {"≥2%天数比":>10} {"高幅均值":>8} {"低幅均值":>8} {"幅度比":>8} {"期望收益/天":>10}')
for i, c in enumerate(cls_list):
    n = n_arr[i]
    if n == 0: continue
    pct2 = nh2_arr[i]/n*100
    h_avg = h_sum_arr[i]/n
    l_avg = l_sum_arr[i]/n
    ratio = h_avg/l_avg if l_avg else 0
    exp = h_avg - l_avg
    print(f'{c:<8} {n:>10,} {pct2:>9.1f}% {h_avg:>7.2f}% {l_avg:>7.2f}% {ratio:>7.2f} {exp:>+9.3f}%')