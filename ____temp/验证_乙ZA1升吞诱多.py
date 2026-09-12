# -*- coding: utf-8 -*-
"""
验证乙(DXZA>0)DXZA=1+前跌排+升吞=诱多 + 等6鼎诱多（高波池）
====================================================
用户猜想1：乙(DXZA>0)，特别是DXZA=1，若柱排为该阳柱之前为跌排，且此阳柱为升吞，
则很有可能为诱多，一定不要在此阳柱介入。可等待回踩不破DJA或在DJA之上站稳后再介入。

用户猜想2：如果没有形成DXZA=1，而只是阳柱与DJA形成鼎（等6），也很有可能是诱多。
但因为等6本来就是不考虑介入的情况，所以可以不考虑介入。

验证：
1. 乙(DXZA>0) DXZA=1 + 前跌排 + 升吞 的冲高率（vs 基线）
2. 乙(DXZA>0) DXZA=1 + 升吞（不看前跌排）的冲高率
3. 等6（阳柱与DJA形成鼎）的冲高率
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

# ============ 统计容器 ============
# 1. 乙(DXZA>0) DXZA=1 + 前跌排 + 升吞
q1 = defaultdict(lambda: [0,0,0.0])
# 2. 乙(DXZA>0) DXZA=1 + 升吞（不看前跌排）
q2 = defaultdict(lambda: [0,0,0.0])
# 3. 等6（阳柱与DJA形成鼎）
q3 = defaultdict(lambda: [0,0,0.0])
# 4. 对照：乙(DXZA>0) DXZA=1 整体
q4 = defaultdict(lambda: [0,0,0.0])

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    for i in range(n):
        row = rows[i]
        if len(row) <= 44: continue
        hr = to_f(row[26]); za = to_f(row[13]); zc = to_f(row[14])
        if hr is None or za is None or zc is None: continue
        if hr < -50 or hr > 50: continue
        dxab = row[9].strip()
        hx = parse_hx(dxab)
        if not hx: continue
        等型 = row[44].strip()
        zp = row[10].strip()
        prev_zp = rows[i-1][10].strip() if i>0 and len(rows[i-1])>10 else ''

        # ===== 1. 乙(DXZA>0) DXZA=1 + 前跌排 + 升吞 =====
        if hx == '乙' and za > 0 and za == 1 and '升.尾吞' in zp:
            q2['乙ZA=1+升吞'][0]+=1; q2['乙ZA=1+升吞'][1]+= (1 if hr>=3 else 0); q2['乙ZA=1+升吞'][2]+=hr
            if '跌' in prev_zp:
                q1['乙ZA=1+前跌排+升吞'][0]+=1; q1['乙ZA=1+前跌排+升吞'][1]+= (1 if hr>=3 else 0); q1['乙ZA=1+前跌排+升吞'][2]+=hr
            else:
                q1['乙ZA=1+非跌排+升吞'][0]+=1; q1['乙ZA=1+非跌排+升吞'][1]+= (1 if hr>=3 else 0); q1['乙ZA=1+非跌排+升吞'][2]+=hr

        # ===== 4. 对照：乙(DXZA>0) DXZA=1 整体 =====
        if hx == '乙' and za > 0 and za == 1:
            q4['乙ZA=1整体'][0]+=1; q4['乙ZA=1整体'][1]+= (1 if hr>=3 else 0); q4['乙ZA=1整体'][2]+=hr

        # ===== 3. 等6（阳柱与DJA形成鼎） =====
        if 等型 == '等6':
            q3['等6整体'][0]+=1; q3['等6整体'][1]+= (1 if hr>=3 else 0); q3['等6整体'][2]+=hr
            if '升.尾吞' in zp:
                q3['等6+升吞'][0]+=1; q3['等6+升吞'][1]+= (1 if hr>=3 else 0); q3['等6+升吞'][2]+=hr

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<24} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*55)
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                print(f'{k:<24} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    print()

show(q1, '1. 乙(DXZA>0)DXZA=1+前跌排+升吞', ['乙ZA=1+前跌排+升吞','乙ZA=1+非跌排+升吞'])
show(q2, '2. 乙(DXZA>0)DXZA=1+升吞', ['乙ZA=1+升吞'])
show(q3, '3. 等6（阳柱与DJA形成鼎）', ['等6整体','等6+升吞'])
show(q4, '4. 对照：乙(DXZA>0)DXZA=1整体', ['乙ZA=1整体'])