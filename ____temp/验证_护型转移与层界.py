# -*- coding: utf-8 -*-
"""
验证用户猜想核心数据：
1. 各护型次日转移概率（甲/乙/己/戊(ZA>0)/丙/乙(ZA<0)/丁/戊(ZA<0)）
2. 己转甲+己概率、戊(ZA>0)转甲+己概率
3. 各护型层界状态细分（初/再AB/再AC/主ZA劫/再ZB劫）

磁盘CSV列序：9=DXAB, 13=日ZA, 14=日ZC, 26=次日高幅, 28=日层界
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

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    """解析DXAB，返回(护型, ZA符号)"""
    if not dxab or len(dxab)<1: return ('','')
    hx = 护型映射.get(dxab[0],'')
    return hx

def parse_lj(lj):
    """解析日层界，返回层类(初/再B/再C/再D/主/储/破)"""
    if not lj: return ''
    if lj.startswith('储'): return '储'
    if lj.startswith('破'): return '破'
    if lj.startswith('主'): return '主'  # 主ZA劫
    if lj.startswith('初'): return '初'  # 层A
    if lj.startswith('再'):
        # 再B/再C/再D
        if len(lj)>=3:
            return '再'+lj[2]  # 再B/再C/再D
        return '再'
    if lj.startswith('_主'): return '_主'
    if lj.startswith('_初'): return '_初'
    if lj.startswith('_再'):
        if len(lj)>=4:
            return '_再'+lj[3]
        return '_再'
    return lj[:2]

# 转移统计: (当前护型, 当前ZA符号) -> {次日护型: n}
trans = defaultdict(lambda: defaultdict(int))
# 层界统计: (当前护型, 层类) -> [n, hr3]
lj_stats = defaultdict(lambda: [0,0])

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
                if len(row) <= 28: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                hr = to_f(row[26])
                lj = row[28].strip()
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = parse_hx(dxab)
                if not hx: continue
                za_key = 'ZA>0' if za>0 else ('ZA=0' if za==0 else 'ZA<0')
                # 次日护型
                nxt_hx = ''
                if i+1 < len(rows):
                    nrow = rows[i+1]
                    if len(nrow) > 9:
                        nxt_hx = parse_hx(nrow[9].strip())
                # 转移统计
                key = (hx, za_key)
                trans[key][nxt_hx] += 1
                # 层界统计
                lj_key = parse_lj(lj)
                if lj_key:
                    lj_stats[(hx, lj_key)][0]+=1
                    lj_stats[(hx, lj_key)][1]+= (1 if hr>=3 else 0)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*70)
print('各护型次日转移概率')
print('='*70)
for hx in ['甲','乙','己','戊','丙','丁']:
    for za_key in ['ZA>0','ZA<0']:
        key = (hx, za_key)
        if key not in trans: continue
        total = sum(trans[key].values())
        if total < 1000: continue
        # 转甲/转己/转坏
        to_jia = trans[key].get('甲',0)/total*100
        to_ji = trans[key].get('己',0)/total*100
        to_yi_pos = trans[key].get('乙',0)/total*100
        print(f'{hx}({za_key}): n={total:,} 转甲={to_jia:.1f}% 转己={to_ji:.1f}% 转乙={to_yi_pos:.1f}% 维持={trans[key].get(hx,0)/total*100:.1f}%')

print()
print('='*70)
print('各护型层界状态细分（次日冲高率）')
print('='*70)
for hx in ['甲','乙','己','戊']:
    print(f'--- {hx} ---')
    for lj_key in ['初','再B','再C','再D','主','储','破','_初','_再B','_主']:
        key = (hx, lj_key)
        if key in lj_stats:
            s = lj_stats[key]
            if s[0] >= 500:
                print(f'  {lj_key}: n={s[0]:,} P(≥3%)={s[1]/s[0]*100:.2f}%')
