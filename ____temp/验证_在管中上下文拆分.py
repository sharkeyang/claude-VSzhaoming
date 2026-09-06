# -*- coding: utf-8 -*-
"""
被反驳假设的细粒度上下文拆分：
长上影/巨柱/跌排 在"连续上涨N天后"的表现
用户直觉：连续上涨多天后，长上影/巨柱 → 衰竭反转
本脚本按 连续上涨天数(连阳/连涨) 拆分，看是否在某阈值后反转

列序（旧列序）：[1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [10]柱排 [13]日ZA [19]BSHA [26]次日高幅 [30]上符串
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
    s=sfs.strip(); return bool(s) and s[-1]=='A'
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr
def report(title, keys):
    print(f'\n{"="*82}')
    print(title)
    print('='*82)
    print(f'{"条件":<54} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*76)
    for k in keys:
        if k in stats:
            s=stats[k]
            print(f'{k:<54} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

files_core=0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code=fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core+=1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r=csv.reader(f); next(r)
            rows=list(r)
            for i,row in enumerate(rows):
                if len(row)<=55: continue
                hr=to_f(row[26])
                if hr is None or hr<-50 or hr>50: continue
                zpa=to_f(row[13]); bsha=to_f(row[19])
                if zpa is None or bsha is None: continue
                sfs=row[30].strip(); zp=row[10].strip()
                o=to_f(row[2]); c=to_f(row[1]); h=to_f(row[3]); gf=to_f(row[6])
                if o is None or c is None or h is None or gf is None or c<=0: continue
                upper=(h-max(o,c))/c*100
                touch=is_touch(sfs)
                # 连续上涨天数：从今日往前数，收>前收 的连续天数
                up_days=0
                j=i
                while j>0:
                    if to_f(rows[j][1]) is not None and to_f(rows[j-1][1]) is not None and to_f(rows[j][1])>to_f(rows[j-1][1]):
                        up_days+=1; j-=1
                    else: break
                # 连续触顶天数（合顶）
                hetop=0
                if touch:
                    for ch in reversed(sfs):
                        if ch=='A': hetop+=1
                        else: break

                if touch:
                    # 长上影 × 连续上涨天数
                    if upper>=3:
                        if up_days>=5: add('长上影+连涨≥5', hr)
                        elif up_days>=3: add('长上影+连涨3-4', hr)
                        elif up_days>=1: add('长上影+连涨1-2', hr)
                        else: add('长上影+未连涨', hr)
                    # 巨柱 × 连续上涨天数
                    if gf>=8:
                        if up_days>=5: add('巨柱+连涨≥5', hr)
                        elif up_days>=3: add('巨柱+连涨3-4', hr)
                        elif up_days>=1: add('巨柱+连涨1-2', hr)
                        else: add('巨柱+未连涨', hr)
                    # 长上影+巨柱 × 连续上涨天数
                    if upper>=3 and gf>=8:
                        if up_days>=5: add('长上影+巨柱+连涨≥5', hr)
                        elif up_days>=3: add('长上影+巨柱+连涨3-4', hr)
                        elif up_days>=1: add('长上影+巨柱+连涨1-2', hr)
                        else: add('长上影+巨柱+未连涨', hr)
                    # 合顶天数 × 连续上涨天数（推高顶部 vs 连涨）
                    if hetop>=3:
                        if up_days>=5: add('合顶≥3+连涨≥5', hr)
                        else: add('合顶≥3+连涨<5', hr)
                # 跌排 × 触DJA × 连续上涨天数
                if zpa is not None and 0<zpa<=2 and '跌' in zp:
                    if up_days>=3: add('触DJA+跌排+连涨≥3', hr)
                    else: add('触DJA+跌排+连涨<3', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
report('长上影 × 连续上涨天数', [
    '长上影+连涨≥5','长上影+连涨3-4','长上影+连涨1-2','长上影+未连涨',
])
report('巨柱 × 连续上涨天数', [
    '巨柱+连涨≥5','巨柱+连涨3-4','巨柱+连涨1-2','巨柱+未连涨',
])
report('长上影+巨柱 × 连续上涨天数', [
    '长上影+巨柱+连涨≥5','长上影+巨柱+连涨3-4','长上影+巨柱+连涨1-2','长上影+巨柱+未连涨',
])
report('合顶≥3 × 连续上涨天数', [
    '合顶≥3+连涨≥5','合顶≥3+连涨<5',
])
report('触DJA+跌排 × 连续上涨天数', [
    '触DJA+跌排+连涨≥3','触DJA+跌排+连涨<3',
])
