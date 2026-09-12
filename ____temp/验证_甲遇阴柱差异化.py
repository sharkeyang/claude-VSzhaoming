# -*- coding: utf-8 -*-
"""
验证：甲护型遇到跌孕/跌吞/跌连 的差异化处理
============================================
用户问题：根据5.6，甲遇到阴柱应该怎么处理？区分跌孕、跌吞、跌连。

列序（旧列序，权威来源 csv-column-mapping-vba）：
  [9] DXAB护型(首字符 a=甲 b=乙 c=丙 z=丁 y=戊 r=己)
  [10] 柱排
  [13] 日ZA [14] 日ZC
  [26] 次日高幅

柱排编码分类：
  跌连 = 柱排以 '跌.尾连' 开头（连续阴柱）
  跌吞 = 柱排含 '尾吞' 或 '连后吞'（阴柱吞没前阳）
  跌孕 = 柱排以 '跌.尾反孕' 开头（阴柱后止跌）
  升排 = 柱排以 '升' 开头（对照）

验证维度：
  1. 次日冲高率 P(≥3%) 和 均高幅
  2. 转坏率（次日护型首字符 != 'a'）
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池
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
    """柱排分类：跌连/跌吞/跌孕/升排/其他"""
    s = zp.strip()
    if s.startswith('跌.尾连'):
        return '跌连'
    if '尾吞' in s or '连后吞' in s:
        return '跌吞'
    if s.startswith('跌.尾反孕'):
        return '跌孕'
    if s.startswith('升'):
        return '升排'
    return '其他'

# 统计容器
# 次日冲高率
stats_hr = defaultdict(lambda: [0,0,0.0])  # key -> [n, P3count, sum_hr]
# 转坏率
stats_bad = defaultdict(lambda: [0,0])  # key -> [n, 转坏count]

def add_hr(key, hr):
    if hr is None: return
    stats_hr[key][0]+=1
    stats_hr[key][1]+=(1 if hr>=3 else 0)
    stats_hr[key][2]+=hr

def add_bad(key, is_bad):
    stats_bad[key][0]+=1
    stats_bad[key][1]+=(1 if is_bad else 0)

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
                if len(row) <= 26: continue
                dxab = row[9].strip()
                if not dxab.startswith('a'): continue  # 只取甲
                zp = row[10].strip()
                cls = classify_zp(zp)
                if cls == '其他': continue  # 只关注跌连/跌吞/跌孕/升排
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                # 次日护型（转坏判定）
                next_dxab = rows[i+1][9].strip() if i+1 < len(rows) else ''
                is_bad = not next_dxab.startswith('a')  # 次日不再是甲 = 转坏
                add_hr(cls, hr)
                add_bad(cls, is_bad)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('甲护型遇到 跌孕/跌吞/跌连/升排 的差异化表现')
print('='*70)
print(f'{"柱排类型":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"转坏率":>8}')
print('-'*60)
for cls in ['升排','跌孕','跌吞','跌连']:
    if cls in stats_hr:
        s = stats_hr[cls]
        b = stats_bad[cls]
        p3 = s[1]/s[0]*100 if s[0] else 0
        avg = s[2]/s[0] if s[0] else 0
        bad = b[1]/b[0]*100 if b[0] else 0
        print(f'{cls:<12} {s[0]:>10,} {p3:>7.2f}% {avg:>7.2f}% {bad:>7.2f}%')
