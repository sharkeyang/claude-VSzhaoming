# -*- coding: utf-8 -*-
"""
深入调查异常：长上影/巨柱/跌排 在"已冲高"上下文中的表现
用户假设：冲高后长上影/巨柱 → 衰竭；跌排压低DJA → 不利
但聚合数据显示相反。本脚本测试"已冲高"上下文是否改变结论。

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
def is_sheng(zp): return '升' in zp
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr
def report(title, keys):
    print(f'\n{"="*80}')
    print(title)
    print('='*80)
    print(f'{"条件":<52} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*74)
    for k in keys:
        if k in stats:
            s=stats[k]
            print(f'{k:<52} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

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
                # 已冲高定义：连续N日上涨 或 已远离DJA(ZA大) 或 近5日累计涨幅大
                # 用 近5日涨幅 判断是否"已冲高"
                run5 = None
                if i>=5:
                    c5 = to_f(rows[i-5][1])
                    if c5 and c5>0: run5 = (c/c5-1)*100
                # 已冲高 = 近5日涨幅≥15% 或 日ZA≥5（远离DJA）
                surged = (run5 is not None and run5>=15) or (zpa is not None and zpa>=5)
                not_surged = (run5 is not None and run5<15) or (zpa is not None and zpa<5)

                if touch:
                    # 长上影 在 已冲高 vs 未冲高
                    if surged and upper>=3: add('A2 触顶+长上影+已冲高', hr)
                    if surged and upper<3: add('A2 触顶+无长上影+已冲高', hr)
                    if not_surged and upper>=3: add('A2 触顶+长上影+未冲高', hr)
                    if not_surged and upper<3: add('A2 触顶+无长上影+未冲高', hr)
                    # 巨柱 在 已冲高 vs 未冲高
                    if surged and gf>=8: add('A5 触顶+巨柱+已冲高', hr)
                    if surged and gf<8: add('A5 触顶+非巨柱+已冲高', hr)
                    if not_surged and gf>=8: add('A5 触顶+巨柱+未冲高', hr)
                    if not_surged and gf<8: add('A5 触顶+非巨柱+未冲高', hr)
                    # 长上影+巨柱 组合（最极端衰竭信号）
                    if surged and upper>=3 and gf>=8: add('A7 触顶+长上影+巨柱+已冲高', hr)
                    if surged and upper<3 and gf<8: add('A7 触顶+无长上影+非巨柱+已冲高', hr)
                # 跌排 在 触DJA 时，已冲高 vs 未冲高
                if zpa is not None and 0<zpa<=2 and '跌' in zp:
                    if surged: add('B1 触DJA+跌排+已冲高', hr)
                    else: add('B1 触DJA+跌排+未冲高', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
report('A2 长上影 × 已冲高上下文', [
    'A2 触顶+长上影+已冲高','A2 触顶+无长上影+已冲高',
    'A2 触顶+长上影+未冲高','A2 触顶+无长上影+未冲高',
])
report('A5 巨柱 × 已冲高上下文', [
    'A5 触顶+巨柱+已冲高','A5 触顶+非巨柱+已冲高',
    'A5 触顶+巨柱+未冲高','A5 触顶+非巨柱+未冲高',
])
report('A7 长上影+巨柱 组合（最极端衰竭）', [
    'A7 触顶+长上影+巨柱+已冲高','A7 触顶+无长上影+非巨柱+已冲高',
])
report('B1 跌排 × 已冲高上下文', [
    'B1 触DJA+跌排+已冲高','B1 触DJA+跌排+未冲高',
])
