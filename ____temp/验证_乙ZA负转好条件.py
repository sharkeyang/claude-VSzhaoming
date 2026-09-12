# -*- coding: utf-8 -*-
"""
乙(DXZA<0) 转乙(DXZA>0) 的条件分析
转好 = 次日护型首字符'b' 且 日ZA>0
维度：日ZA具体值/柱型/柱排/触顶/管宽/BSHA
"""
import csv, os, sys
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

def classify_zx(zx):
    s = zx.strip()
    if s.startswith('.'):
        return {'9':'线下','5':'根','4':'枝','0':'梯','1':'栏','2':'栅','3':'杂'}.get(s[1])
    return None

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def is_touch(sfs):
    s=sfs.strip(); return bool(s) and s[-1]=='A'

stats = defaultdict(lambda: [0,0])  # key -> [n, 转好count]
def add(key, good):
    stats[key][0]+=1
    stats[key][1]+=(1 if good else 0)

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                if not row[9].strip().startswith('b'): continue
                zpa = to_f(row[13])
                if zpa is None or zpa > 0: continue
                if i+1 >= len(rows): continue
                nht = rows[i+1][9].strip()[:1]
                nzpa = to_f(rows[i+1][13])
                good = (nht=='b' and nzpa is not None and nzpa>0)
                # 日ZA具体值
                add(f'ZA={int(zpa)}', good)
                # 柱型
                zx = classify_zx(row[27])
                if zx: add(f'柱型={zx}', good)
                # 柱排
                zp = classify_zp(row[10])
                if zp!='其他': add(f'柱排={zp}', good)
                # 触顶
                touch = is_touch(row[30].strip())
                add(f'触顶={"是" if touch else "否"}', good)
                # 管宽
                lian = to_f(row[21])
                if lian is not None:
                    if lian<5: add('管宽<5', good)
                    elif lian<10: add('管宽5-10', good)
                    else: add('管宽≥10', good)
                # BSHA
                bsha = to_f(row[19])
                if bsha is not None:
                    if bsha<3: add('BSHA<3', good)
                    elif bsha<8: add('BSHA3-8', good)
                    else: add('BSHA≥8', good)
    except Exception: pass

print('乙(DXZA<0) 转乙(DXZA>0) 概率（转好率）')
print(f'{"条件":<16} {"n":>10} {"转好率":>8}')
print('-'*40)
for k in sorted(stats.keys()):
    s = stats[k]
    if s[0] < 1000: continue
    print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')
