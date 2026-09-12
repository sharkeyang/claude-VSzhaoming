# -*- coding: utf-8 -*-
"""
乙(DXZA>0) 遇到 跌孕/跌吞/跌连/人排(阴阳阴) 的差异化处理
========================================================
对比甲护型的结论，验证乙(DXZA>0)是否一致。

列序（旧列序）：
  [9] DXAB护型(首字符 b=乙)
  [10] 柱排
  [13] 日ZA
  [26] 次日高幅
  [30] 上符串(末位A=触顶)

柱排分类：
  跌连 = '跌.尾连' 开头
  跌吞 = 含 '尾吞' 或 '连后吞'
  跌孕 = '跌.尾反孕' 开头
  人排(阴阳阴) = 含 '人'（阴阳交替）
  升排 = '升' 开头
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
    if '人' in s: return '人排(阴阳阴)'
    if s.startswith('升'): return '升排'
    return '其他'

def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'

# 转坏率：次日护型首字符 != 'b'（乙转成非乙）
stats_bad = defaultdict(lambda: [0,0])
stats_hr = defaultdict(lambda: [0,0,0.0])

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
                if not dxab.startswith('b'): continue
                zpa = to_f(row[13])
                if zpa is None or zpa <= 0: continue  # 只取乙(DXZA>0)
                zp = row[10].strip()
                cls = classify_zp(zp)
                if cls == '其他': continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                touch = is_touch(row[30].strip())
                next_dxab = rows[i+1][9].strip() if i+1 < len(rows) else ''
                is_bad = not next_dxab.startswith('b')
                # 转坏率
                key_bad = f'{cls}+{"触顶" if touch else "未触顶"}'
                stats_bad[key_bad][0]+=1
                stats_bad[key_bad][1]+=(1 if is_bad else 0)
                # 次日冲高率
                stats_hr[key_bad][0]+=1
                stats_hr[key_bad][1]+=(1 if hr>=3 else 0)
                stats_hr[key_bad][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*75)
print('乙(DXZA>0) 遇到 跌孕/跌吞/跌连/人排(阴阳阴) 的差异化表现')
print('='*75)
print(f'{"柱排类型":<16} {"触顶":<6} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"转坏率":>8}')
print('-'*70)
for cls in ['升排','跌吞','跌连','跌孕','人排(阴阳阴)']:
    for t in ['触顶','未触顶']:
        k = f'{cls}+{t}'
        if k in stats_bad:
            b = stats_bad[k]
            h = stats_hr[k]
            p3 = h[1]/h[0]*100 if h[0] else 0
            avg = h[2]/h[0] if h[0] else 0
            bad = b[1]/b[0]*100 if b[0] else 0
            print(f'{cls:<16} {t:<6} {b[0]:>10,} {p3:>7.2f}% {avg:>7.2f}% {bad:>7.2f}%')
