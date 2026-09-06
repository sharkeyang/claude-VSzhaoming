# -*- coding: utf-8 -*-
"""
验证"在管中"运行模式假设（C6 6.6 管中形态与管宽）— 第2版，修正语义

数据列序（旧列序，勿看表头）：
  [0]日期 [1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [10]柱排 [13]日ZA(DTZA,在DJA上方天数) [14]日ZC [19]BSHA(管宽哼JA代理)
  [26]次日高幅 [30]上符串 [55]顶触

语义修正：
  - 日ZA = DTZA（在DJA上方天数），非连续值。日ZA=1=刚上破DJA，日ZA=2=第2天
  - 触下沿DJA = 日ZA小正（1或2），价格贴近DJA
  - 首次触DJA = 日ZA=1（刚上破）
  - 下破DJA = 前日ZA>0 且 今日ZA<=0
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'
def is_sheng(zp): return '升' in zp
def is_die(zp): return '跌' in zp

stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr

def report(title, keys):
    print(f'\n{"="*78}')
    print(title)
    print('='*78)
    print(f'{"条件":<46} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*72)
    for k in keys:
        if k in stats:
            s = stats[k]
            print(f'{k:<46} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

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
            for i,row in enumerate(rows):
                if len(row) <= 55: continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                zpa = to_f(row[13]); zc = to_f(row[14]); bsha = to_f(row[19])
                if zpa is None or zc is None or bsha is None: continue
                sfs = row[30].strip(); zp = row[10].strip()
                prev = rows[i-1] if i>0 else None
                prev_za = to_f(prev[13]) if prev else None
                prev_close = to_f(prev[1]) if prev else None
                o = to_f(row[2]); c = to_f(row[1]); h = to_f(row[3]); gf = to_f(row[6])
                upper_shadow = None
                if o is not None and c is not None and h is not None and c>0:
                    upper_shadow = (h - max(o,c))/c*100
                high_open_bear = False
                if o is not None and c is not None and prev_close is not None:
                    high_open_bear = (o > c) and (o > prev_close)
                touch = is_touch(sfs)
                hetop = 0
                if touch:
                    for ch in reversed(sfs):
                        if ch=='A': hetop+=1
                        else: break

                # ============ A. 触顶时 ============
                if touch:
                    if is_sheng(zp): add('A1 触顶+升排', hr)
                    elif is_die(zp): add('A1 触顶+跌排', hr)
                    else: add('A1 触顶+非升非跌', hr)
                    # A2 长上影（冲高后长上影）
                    if upper_shadow is not None:
                        if upper_shadow >= 3: add('A2 触顶+长上影(≥3%)', hr)
                        else: add('A2 触顶+无长上影(<3%)', hr)
                    # A3 高开阴柱
                    if high_open_bear: add('A3 触顶+高开阴柱', hr)
                    else: add('A3 触顶+非高开阴柱', hr)
                    # A4 合顶天数（推高顶部）
                    if hetop>=3: add('A4 触顶+合顶≥3(连续推高)', hr)
                    elif hetop==1: add('A4 触顶+合顶=1(未推高)', hr)
                    else: add('A4 触顶+合顶=2', hr)
                    # A5 升排+巨柱（极限冲高）
                    if is_sheng(zp) and gf is not None:
                        if gf>=8: add('A5 触顶+升排+巨柱(高幅≥8)', hr)
                        else: add('A5 触顶+升排+非巨柱(高幅<8)', hr)
                    # A6 升排+长上影（冲高后长上影，升排中）
                    if is_sheng(zp) and upper_shadow is not None:
                        if upper_shadow>=3: add('A6 触顶+升排+长上影', hr)
                        else: add('A6 触顶+升排+无长上影', hr)

                # ============ B. 触下沿DJA（日ZA=1或2，贴近DJA） ============
                if zpa is not None and 0 < zpa <= 2:
                    if is_die(zp): add('B1 触DJA+跌排(压低)', hr)
                    elif is_sheng(zp): add('B1 触DJA+升排', hr)
                    else: add('B1 触DJA+非升非跌', hr)
                    # B2 首次触DJA（日ZA=1）vs 多次（日ZA=2）
                    if zpa==1: add('B2 触DJA+首次(ZA=1刚上破)', hr)
                    else: add('B2 触DJA+多次(ZA=2)', hr)
                    # B3 升排后大阴柱触DJA后小阳柱止跌（需前2日）
                    if i>=2:
                        p2 = rows[i-2]
                        p2_zp = p2[10].strip(); p2_c = to_f(p2[1]); p2_o = to_f(p2[2])
                        p1 = rows[i-1]; p1_c = to_f(p1[1]); p1_o = to_f(p1[2])
                        # 前2日升排，前1日大阴柱，今日小阳柱
                        if is_sheng(p2_zp) and p1_c is not None and p1_o is not None and p1_c < p1_o and c is not None and o is not None and c > o:
                            add('B3 升排→大阴→小阳(止跌)', hr)
                        else:
                            add('B3 其他触DJA形态', hr)

                # ============ C. 刚下破DJA（前ZA>0且今ZA<=0） ============
                if prev_za is not None and prev_za > 0 and zpa <= 0:
                    if is_sheng(zp): add('C1 下破DJA+升排', hr)
                    elif is_die(zp): add('C1 下破DJA+跌排', hr)
                    else: add('C1 下破DJA+非升非跌', hr)
                    # C2 升排/升吞 上破DJA后是否持续（看次日是否回到DJA上方）
                    if is_sheng(zp): add('C2 下破DJA+升排(次日冲高)', hr)

                # ============ D. 管宽假设（BSHA代理管宽哼JA） ============
                if touch and zpa is not None and 0 < zpa <= 2:
                    add('D1 触顶+触DJA(窄管)', hr)
                if touch and zpa is not None and zpa > 2:
                    add('D1 触顶+远离DJA(宽管)', hr)
                if bsha >= 5: add('D2 BSHA≥5(管宽哼JA≥5)', hr)
                else: add('D2 BSHA<5(管宽哼JA<5)', hr)
                if bsha >= 5 and gf is not None:
                    if gf < 3: add('D3 宽管(BSHA≥5)+今高幅<3(DSHA回落)', hr)
                    else: add('D3 宽管(BSHA≥5)+今高幅≥3(DSHA未回落)', hr)

                # ============ E. 升势运行模式 ============
                # E1 单向连续触顶（连续多日触顶+升排）
                if touch and hetop>=3 and is_sheng(zp):
                    add('E1 连续触顶≥3+升排(单向推高)', hr)
                # E2 阶梯上升（触顶推高+触下沿平移交替）
                # 检测：前日触DJA(ZA=1/2)，今日触顶
                if touch and prev_za is not None and 0 < prev_za <= 2:
                    add('E2 前日触DJA→今日触顶(阶梯)', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')

report('A. 触顶时（上符串末位A）', [
    'A1 触顶+升排','A1 触顶+跌排','A1 触顶+非升非跌',
    'A2 触顶+长上影(≥3%)','A2 触顶+无长上影(<3%)',
    'A3 触顶+高开阴柱','A3 触顶+非高开阴柱',
    'A4 触顶+合顶≥3(连续推高)','A4 触顶+合顶=2','A4 触顶+合顶=1(未推高)',
    'A5 触顶+升排+巨柱(高幅≥8)','A5 触顶+升排+非巨柱(高幅<8)',
    'A6 触顶+升排+长上影','A6 触顶+升排+无长上影',
])
report('B. 触下沿DJA时（日ZA=1或2）', [
    'B1 触DJA+升排','B1 触DJA+非升非跌','B1 触DJA+跌排(压低)',
    'B2 触DJA+首次(ZA=1刚上破)','B2 触DJA+多次(ZA=2)',
    'B3 升排→大阴→小阳(止跌)','B3 其他触DJA形态',
])
report('C. 刚下破DJA（前ZA>0且今ZA≤0）', [
    'C1 下破DJA+升排','C1 下破DJA+非升非跌','C1 下破DJA+跌排',
    'C2 下破DJA+升排(次日冲高)',
])
report('D. 管宽假设（BSHA代理管宽哼JA）', [
    'D1 触顶+触DJA(窄管)','D1 触顶+远离DJA(宽管)',
    'D2 BSHA≥5(管宽哼JA≥5)','D2 BSHA<5(管宽哼JA<5)',
    'D3 宽管(BSHA≥5)+今高幅<3(DSHA回落)','D3 宽管(BSHA≥5)+今高幅≥3(DSHA未回落)',
])
report('E. 升势运行模式', [
    'E1 连续触顶≥3+升排(单向推高)',
    'E2 前日触DJA→今日触顶(阶梯)',
])
