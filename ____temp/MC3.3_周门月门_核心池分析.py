# -*- coding: utf-8 -*-
"""§3.2~§3.4 周门×月门 核心池全量分析"""
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
stats = defaultdict(lambda: {'n':0,'nh2':0,'nh3':0,'nh_sum':0.0})
total_n = 0; total_nh2 = 0

def add(key, nh):
    global total_n, total_nh2
    s = stats[key]
    s['n'] += 1
    total_n += 1
    if not pd.isna(nh):
        if nh > 2: s['nh2'] += 1; total_nh2 += 1
        if nh > 3: s['nh3'] += 1
        s['nh_sum'] += nh

for fi, f in enumerate(core_files):
    try:
        df = pd.read_csv(f, encoding='gbk', low_memory=False,
                         usecols=['日ZA','中符串','次日高幅','日ZC','DXCD','日ZE','BSHA','BT连阳'])
    except: continue
    if len(df) < 100: continue
    za = df['日ZA'].astype(float); mid = df['中符串'].astype(str)
    last = mid.str[-1]; nh = df['次日高幅'].astype(float)
    zc = df['日ZC'].astype(float); ze = df['日ZE'].astype(float)
    dxcd = df['DXCD'].astype(str)
    bsha = df['BSHA'].astype(float); btly = df['BT连阳'].astype(float)

    zhoumen = (zc > 0) & (dxcd == '上')
    yuemeng = ze > 0
    bsha5 = bsha > 5; bsha3 = bsha > 3
    ly = btly > 0

    for idx in df.index:
        c6 = classify_6(za[idx], last[idx])
        if c6 == 'NA': continue
        nhv = nh[idx]
        zm = zhoumen[idx]; ym = yuemeng[idx]
        bs5 = bsha5[idx]; l = ly[idx]

        if zm and ym: add('门_周门+月门', nhv)
        elif zm and not ym: add('门_周门+无月门', nhv)
        elif not zm and ym: add('门_无周门+月门', nhv)
        else: add('门_无周门+无月门', nhv)

        if zm: add('门_仅周门', nhv)
        if ym: add('门_仅月门', nhv)

        if c6 in ['等2','等3']:
            add(f'门_{c6}_基准', nhv)
            if zm: add(f'门_{c6}_周门', nhv)
            if ym: add(f'门_{c6}_月门', nhv)
            if zm and ym: add(f'门_{c6}_周门+月门', nhv)

        if zm and bs5 and l: add('门_周门+BSHA5+连阳', nhv)
        if ym and bs5 and l: add('门_月门+BSHA5+连阳', nhv)
        if zm and ym and bs5 and l: add('门_周门+月门+BSHA5+连阳', nhv)
        if bs5 and l and not zm: add('门_BSHA5+连阳(无门)', nhv)

    if (fi+1) % 1000 == 0: print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s')

print(f'\n全量处理完成 {len(core_files)} 文件, 耗时 {time.time()-t0:.0f}s')

def pct(s):
    n2 = s['nh2']/s['n']*100 if s['n'] else 0
    n3 = s['nh3']/s['n']*100 if s['n'] else 0
    return s['n'], n2, n3

print(f'\n全样本基准: {total_n:,}, ≥2%={total_nh2/total_n*100:.1f}%')

print('\n=== §3.3 周门×月门 4格组合 ===')
print(f'{"组合":<20} {"样本":>10} {"占比":>8} {"≥2%":>8}')
for k, label in [('门_周门+月门','周门✓+月门✓'),('门_周门+无月门','周门✓+月门✗'),
                 ('门_无周门+月门','周门✗+月门✓'),('门_无周门+无月门','周门✗+月门✗')]:
    if k in stats:
        n, n2, _ = pct(stats[k])
        print(f'{label:<20} {n:>10,} {n/total_n:>7.1%} {n2:>7.1f}%')

print('\n=== 仅周门/仅月门 ===')
for k, label in [('门_仅周门','仅周门'),('门_仅月门','仅月门')]:
    if k in stats:
        n, n2, _ = pct(stats[k])
        print(f'{label:<10} {n:>10,} {n/total_n:>7.1%} {n2:>7.1f}%')

print('\n=== §3.2 等高线×周门/月门 ===')
for c in ['等2','等3']:
    kb = f'门_{c}_基准'
    if kb not in stats: continue
    nb, n2b, n3b = pct(stats[kb])
    print(f'{c} 基准: {n2b:.1f}%({n3b:.1f}%)')
    for cond, label in [('周门','+周门'),('月门','+月门'),('周门+月门','+周门+月门')]:
        k = f'门_{c}_{cond}'
        if k in stats:
            n, n2, n3 = pct(stats[k])
            print(f'  {label:<10} {n:>10,} {n2:>7.1f}%({n3:.1f}%)')

print('\n=== §3.4 每日筛选对比 ===')
for k, label in [('门_周门+BSHA5+连阳','周门+BSHA5+连阳'),('门_月门+BSHA5+连阳','月门+BSHA5+连阳'),
                 ('门_周门+月门+BSHA5+连阳','周门+月门+BSHA5+连阳'),('门_BSHA5+连阳(无门)','BSHA5+连阳(无门)')]:
    if k in stats:
        n, n2, _ = pct(stats[k])
        print(f'{label:<25} {n:>10,} {n/total_n:>7.1%} {n2:>7.1f}%')