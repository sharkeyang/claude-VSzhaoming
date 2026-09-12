# -*- coding: utf-8 -*-
"""
甲护型遇到 跌孕/跌吞/跌连 的上下文拆分
========================================
核心发现：跌孕(35.69%)和跌连(37.69%)转坏率远高于跌吞(22.29%)，反直觉。
本脚本按上下文拆分，理解什么条件下转坏率最高。

列序（旧列序）：
  [9] DXAB护型(首字符 a=甲)
  [10] 柱排
  [13] 日ZA [14] 日ZC
  [21] 脸哼JA(管宽哼JA)
  [26] 次日高幅
  [30] 上符串(末位A=触顶)
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

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if s.startswith('升'): return '升排'
    return '其他'

def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'

stats = defaultdict(lambda: [0,0])  # key -> [n, 转坏count]
def add(key, is_bad):
    stats[key][0]+=1
    stats[key][1]+=(1 if is_bad else 0)

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
                dxab = row[9].strip()
                if not dxab.startswith('a'): continue
                zp = row[10].strip()
                cls = classify_zp(zp)
                if cls not in ('跌孕','跌吞','跌连'): continue
                zpa = to_f(row[13])
                if zpa is None: continue
                lian = to_f(row[21])  # 脸哼JA = 管宽哼JA
                sfs = row[30].strip()
                touch = is_touch(sfs)
                next_dxab = rows[i+1][9].strip() if i+1 < len(rows) else ''
                is_bad = not next_dxab.startswith('a')

                # 触顶 vs 未触顶
                if touch: add(f'{cls}+触顶', is_bad)
                else: add(f'{cls}+未触顶', is_bad)
                # 日ZA 分层
                if zpa <= 2: add(f'{cls}+贴近DJA(ZA≤2)', is_bad)
                elif zpa <= 5: add(f'{cls}+中距(ZA3-5)', is_bad)
                else: add(f'{cls}+远离DJA(ZA>5)', is_bad)
                # 管宽 分层
                if lian is not None:
                    if lian < 5: add(f'{cls}+管宽<5', is_bad)
                    elif lian < 10: add(f'{cls}+管宽5-10', is_bad)
                    else: add(f'{cls}+管宽≥10', is_bad)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('甲护型 跌孕/跌吞/跌连 转坏率 上下文拆分')
print('='*70)
print(f'{"条件":<28} {"n":>10} {"转坏率":>8}')
print('-'*50)

# 按类别分组输出
for cls in ['跌孕','跌吞','跌连']:
    print(f'\n【{cls}】')
    keys = [f'{cls}+触顶', f'{cls}+未触顶',
            f'{cls}+贴近DJA(ZA≤2)', f'{cls}+中距(ZA3-5)', f'{cls}+远离DJA(ZA>5)',
            f'{cls}+管宽<5', f'{cls}+管宽5-10', f'{cls}+管宽≥10']
    for k in keys:
        if k in stats:
            s = stats[k]
            bad = s[1]/s[0]*100 if s[0] else 0
            print(f'{k:<28} {s[0]:>10,} {bad:>7.2f}%')
