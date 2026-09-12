# -*- coding: utf-8 -*-
"""
DXAB负转正特权 + 诱多识别 + 转负比例 + 上影退出 综合验证（高波池）
====================================================
1. DXAB负转正后特权：阴柱回调至DJA附近仍会上升（全局/DXZE>0/DXZE>0且DXEF>0）
2. 乙(DXZA>0)DXZA=1+前跌排+升吞=诱多
3. DJA之上跌连后升吞=诱多还是上升中继
4. DXAB负转正后DXAB≤5/≤9内转负比例（分DXZE>0/DXZE<0）
5. 升连过程中上影阳柱/上影跌孕是否需退出
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

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','',None)
    hx = hxmap.get(dxab[0], '')
    zj = dxab[2]
    dirch = dxab[3] if len(dxab) > 3 else ''
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    val = int(m.group(1)) if m else None
    return (hx, zj, dirch, val)

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def extract_ef(月策带日):
    if not 月策带日: return ''
    m = re.search(r'\(([^)]+)\)', 月策带日)
    return m.group(1) if m else ''

# ============ 统计容器 ============
# 1. DXAB负转正后特权
q1 = defaultdict(lambda: [0,0,0.0])  # key: 情况 -> [n, hr>=3, sum_hr]
# 2. 乙ZA1前跌排升吞
q2 = defaultdict(lambda: [0,0,0.0])
# 3. DJA之上跌连后升吞
q3 = defaultdict(lambda: [0,0,0.0])
# 4. DXAB负转正后转负比例
q4 = defaultdict(lambda: [0,0])  # key: 情况|阈值 -> [n, 转负]
# 5. 升连上影阳柱/跌孕
q5 = defaultdict(lambda: [0,0,0.0])

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
    dxabs = [parse_dxab(rows[i][9].strip()) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    zes = [to_f(rows[i][15]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]
    zps = [rows[i][10].strip() if len(rows[i])>10 else '' for i in range(n)]

    # ===== 1. DXAB负转正后特权 =====
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if val is None or val_prev is None: continue
        if not (val_prev < 0 and val > 0): continue
        # 在其后找第一个"阴柱回调至DJA附近"（日ZA<=1且阴柱）
        for j in range(i, n):
            za = zas[j]; zf = zfs[j]
            if za is None or zf is None: continue
            if za <= 1 and zf < 0:
                hr = hrs[j]; ze = zes[j]
                if hr is None: break
                if hr < -50 or hr > 50: break
                ef = extract_ef(月策带日s[j])
                if ze is None:
                    case = '全局'
                elif ze > 0 and ef in ('金','银','唏'):
                    case = 'DXZE>0且DXEF>0'
                elif ze > 0:
                    case = 'DXZE>0'
                else:
                    case = 'DXZE≤0'
                q1[case][0]+=1; q1[case][1]+= (1 if hr>=3 else 0); q1[case][2]+=hr
                break

    # ===== 2. 乙ZA1前跌排升吞 =====
    for i in range(n):
        hx = parse_hx(rows[i][9].strip())
        za = zas[i]; hr = hrs[i]; zf = zfs[i]
        if hx != '乙' or za is None or hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        if za == 1 and '升.尾吞' in zps[i]:
            prev_zp = zps[i-1] if i>0 else ''
            if '跌' in prev_zp:
                q2['乙ZA=1+前跌排+升吞'][0]+=1; q2['乙ZA=1+前跌排+升吞'][1]+= (1 if hr>=3 else 0); q2['乙ZA=1+前跌排+升吞'][2]+=hr
            else:
                q2['乙ZA=1+非跌排+升吞'][0]+=1; q2['乙ZA=1+非跌排+升吞'][1]+= (1 if hr>=3 else 0); q2['乙ZA=1+非跌排+升吞'][2]+=hr

    # ===== 3. DJA之上跌连后升吞 =====
    for i in range(n):
        za = zas[i]; hr = hrs[i]; zf = zfs[i]
        if za is None or hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        # DJA之上（日ZA>0）且未出现DXZA=-1（即日ZA>0持续）
        if za > 0 and '升.尾吞' in zps[i]:
            prev_zp = zps[i-1] if i>0 else ''
            prev_za = zas[i-1] if i>0 else None
            if '跌.尾连' in prev_zp and prev_za is not None and prev_za > 0:
                q3['DJA之上+跌连后升吞'][0]+=1; q3['DJA之上+跌连后升吞'][1]+= (1 if hr>=3 else 0); q3['DJA之上+跌连后升吞'][2]+=hr
            elif '跌' in prev_zp and prev_za is not None and prev_za > 0:
                q3['DJA之上+其他跌后升吞'][0]+=1; q3['DJA之上+其他跌后升吞'][1]+= (1 if hr>=3 else 0); q3['DJA之上+其他跌后升吞'][2]+=hr

    # ===== 4. DXAB负转正后转负比例 =====
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if val is None or val_prev is None: continue
        if not (val_prev < 0 and val > 0): continue
        ze = zes[i]
        # 转正后DXAB≤5/≤9内转负
        for threshold in [5, 9]:
            turned = False
            for k in range(1, threshold+1):
                if i+k >= n: break
                hx2, zj2, dirch2, val2 = dxabs[i+k]
                if val2 is not None and val2 < 0:
                    turned = True; break
            if ze is None:
                case = '全局'
            elif ze > 0:
                case = 'DXZE>0'
            else:
                case = 'DXZE<0'
            if turned:
                q4[f'{case}|≤{threshold}'][0]+=1; q4[f'{case}|≤{threshold}'][1]+=1
            else:
                q4[f'{case}|≤{threshold}'][0]+=1

    # ===== 5. 升连上影阳柱/跌孕 =====
    for i in range(n):
        hr = hrs[i]; zf = zfs[i]
        if hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        if '升.尾连' not in zps[i]: continue
        # 上影阳柱 = 阳柱 + 上影（高幅>涨幅，即冲高回落）
        zf2 = zfs[i]
        if zf2 is not None and zf2 > 0:
            # 上影 = 高幅 > 涨幅（盘中冲高但收盘回落）
            hr_high = to_f(rows[i][6])  # 高幅
            if hr_high is not None and hr_high > zf2:
                q5['升连+上影阳柱'][0]+=1; q5['升连+上影阳柱'][1]+= (1 if hr>=3 else 0); q5['升连+上影阳柱'][2]+=hr
            else:
                q5['升连+无上影阳柱'][0]+=1; q5['升连+无上影阳柱'][1]+= (1 if hr>=3 else 0); q5['升连+无上影阳柱'][2]+=hr
        if '孕' in zps[i]:
            q5['升连+跌孕'][0]+=1; q5['升连+跌孕'][1]+= (1 if hr>=3 else 0); q5['升连+跌孕'][2]+=hr

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

show(q1, '1. DXAB负转正后阴柱回调至DJA附近，次日冲高率', ['全局','DXZE>0','DXZE>0且DXEF>0','DXZE≤0'])
show(q2, '2. 乙(DXZA>0)DXZA=1+前跌排+升吞', ['乙ZA=1+前跌排+升吞','乙ZA=1+非跌排+升吞'])
show(q3, '3. DJA之上跌连后升吞', ['DJA之上+跌连后升吞','DJA之上+其他跌后升吞'])
show(q5, '5. 升连上影阳柱/跌孕', ['升连+上影阳柱','升连+无上影阳柱','升连+跌孕'])

# 4. 转负比例
print('='*75)
print('【4. DXAB负转正后转负比例】')
print('='*75)
print(f'{"类别":<16} {"n":>10} {"转负":>10} {"转负率":>8}')
print('-'*50)
for k in ['全局|≤5','全局|≤9','DXZE>0|≤5','DXZE>0|≤9','DXZE<0|≤5','DXZE<0|≤9']:
    if k in q4:
        s = q4[k]
        if s[0] >= 100:
            print(f'{k:<16} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()