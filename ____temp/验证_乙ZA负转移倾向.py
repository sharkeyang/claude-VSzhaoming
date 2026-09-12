# -*- coding: utf-8 -*-
"""
乙(DXZA<0) 结合柱型大类的转移倾向分析
乙(DXZA<0) = 护型首字符'b' 且 日ZA[13]<=0
转移方向：维持乙(ZA<0)/转乙(ZA>0)/转丙/转丁/转戊己
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
        d = s[1]
        return {'9':'线下','5':'根','4':'枝','0':'梯','1':'栏','2':'栅','3':'杂'}.get(d)
    return None

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

# 转移方向：柱型大类 -> 方向 -> count
stats = defaultdict(lambda: defaultdict(int))
total = defaultdict(int)

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
                if len(row) <= 30: continue
                if not row[9].strip().startswith('b'): continue
                zpa = to_f(row[13])
                if zpa is None or zpa > 0: continue  # 只取乙(DXZA<0)
                zx = classify_zx(row[27])
                if zx is None: continue
                # 次日转移方向
                if i+1 < len(rows):
                    nht = rows[i+1][9].strip()[:1]
                    nzpa = to_f(rows[i+1][13])
                    if nht == 'b':
                        if nzpa is not None and nzpa > 0:
                            direction = '转乙(ZA>0)'
                        else:
                            direction = '维持乙(ZA<0)'
                    elif nht == 'c':
                        direction = '转丙'
                    elif nht == 'z':
                        direction = '转丁'
                    elif nht in ('y','r'):
                        direction = '转戊己'
                    else:
                        direction = '其他'
                else:
                    continue
                stats[zx][direction] += 1
                total[zx] += 1
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*80)
print('乙(DXZA<0) 结合柱型大类的转移倾向')
print('='*80)
dirs = ['维持乙(ZA<0)','转乙(ZA>0)','转丙','转丁','转戊己']
print(f'{"柱型":<8} {"n":>10}', end='')
for d in dirs:
    print(f' {d:>12}', end='')
print()
print('-'*80)
for zx in ['线下','根','枝','梯','栏','栅','杂']:
    if zx in total:
        n = total[zx]
        print(f'{zx:<8} {n:>10,}', end='')
        for d in dirs:
            c = stats[zx].get(d, 0)
            print(f' {c/n*100:>11.1f}%', end='')
        print()
