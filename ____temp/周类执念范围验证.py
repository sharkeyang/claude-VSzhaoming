# -*- coding: utf-8 -*-
"""周类执念范围验证：WXZC>0 + 丙丁戊（范围外但非禁区）"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = set(k for k,v in pool.items() if v in ('Qic','Qim','Qit'))

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])
def add(key, nxt):
    s = stats[key]; s[0]+=1
    if nxt>=3: s[1]+=1
    s[2]+=nxt

def parse_hx(wxab):
    if len(wxab) > 1 and wxab[1] in '甲乙丙丁戊己': return wxab[1]
    return ''

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组周')):
    if not fname.endswith('.csv'): continue
    code = fname.replace('谕组周_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组周',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            prev = None
            for row in r:
                if len(row) <= 16: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                wxab = row[4].strip()
                zc = to_f(row[16])
                hr = to_f(row[3])
                if zc is None or hr is None: continue
                if prev is not None:
                    p_wxab, p_zc, p_hr = prev
                    if p_hr < -50 or p_hr > 50:
                        prev = (wxab, zc, hr); continue
                    hx = parse_hx(p_wxab)
                    # 基线
                    add('基线', p_hr)
                    # 宽范围（范围内护型）
                    if hx in '甲乙己' or (hx=='戊' and p_zc>0) or (hx=='乙'):
                        add('宽范围', p_hr)
                    # 禁区范围（WXZC<0 + 丙丁戊）
                    if p_zc < 0 and hx in '丙丁戊':
                        add('禁区范围', p_hr)
                    # 执念范围（WXZC>0 + 丙丁戊）
                    if p_zc > 0 and hx in '丙丁戊':
                        add('执念范围', p_hr)
                prev = (wxab, zc, hr)
    except Exception:
        pass

print(f'核心池文件: {files_core}')
print()
def show(key):
    if key in stats:
        s = stats[key]
        print(f'{key:<28} n={s[0]:>10,} 周冲高≥3%={s[1]/s[0]*100:.2f}% 平均周高幅={s[2]/s[0]:.2f}%')
    else:
        print(f'{key:<28} n=0')

print('=== 周类三范围验证 ===')
show('基线')
show('宽范围')
show('禁区范围')
show('执念范围')

# 验证合并
n_all = stats['基线'][0]
n_w = stats['宽范围'][0]
n_a = stats['禁区范围'][0]
n_z = stats['执念范围'][0]
print()
print(f'宽范围 + 禁区范围 + 执念范围 = {n_w:,} + {n_a:,} + {n_z:,} = {n_w+n_a+n_z:,}')
print(f'基线(全部) = {n_all:,}')
print(f'合并/全部 = {(n_w+n_a+n_z)/n_all*100:.2f}%')
