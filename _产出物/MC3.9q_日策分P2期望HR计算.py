#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9q_日策分P2期望HR计算.py
=====================
从日CSV还原日策分P2策略，计算每个策略的实际下日HR均值。
更新 vba表日策分P2.txt 的期望HR字段。

日CSV列（实际）：
  10:柱排, 13:日ZA, 19:BSHA, 28:层界, 33:中符串, 42:BT连阳, 6:高幅(HR)

等高线分类（等值）：
  日ZA=1 → 等1
  日ZA≥2 + 末位AB → 等3
  日ZA≥2 + 末位CDEF → 等2
  日ZA=-1 → 等5
  日ZA≤-2 + 末位EF → 等7
  日ZA≤-2 + 末位ABCD → 等6

条件评分：
  BSHA>5 → 偏5
  BSHA>3 → 偏3
  BT连阳>0 → 连门
  层界首字=主 → 层主
  柱排首字=升 → 升排
  柱排首字=跌 → 跌排

用法：
    python _产出物/MC3.9q_日策分P2期望HR计算.py
"""

import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物/_工具'
MIN_SAMPLE = 100

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0: print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
        try:
            # 列索引：6=高幅(HR), 10=柱排, 13=日ZA, 19=BSHA, 28=层界, 33=中符串, 42=BT连阳
            df = pd.read_csv(f, encoding='gbk', usecols=[6,10,13,19,28,33,42])
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except Exception as e:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    wk.columns = ['HR','柱排','日ZA','BSHA','层界','中符串','BT连阳','fid']
    wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下日HR'])
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def classify(za, mid):
    """等高线分类"""
    if pd.isna(za): return ''
    za = float(za)
    mid = str(mid) if pd.notna(mid) else ''
    last = mid[-1] if mid else ''
    if za == 1: return '等1'
    elif za >= 2 and last in 'AB': return '等3'
    elif za >= 2 and last in 'CDEF': return '等2'
    elif za == -1: return '等5'
    elif za <= -2 and last in 'EF': return '等7'
    elif za <= -2 and last in 'ABCD': return '等6'
    return ''

def strategy_name(eq, bsha, lianyang, cengzhu, zhuopai):
    """还原策略名"""
    bsha5 = bsha > 5
    bsha3 = bsha > 3
    lianyang2 = lianyang > 0
    cengzhu2 = str(cengzhu).startswith('主') if pd.notna(cengzhu) else False
    zhuopai = str(zhuopai) if pd.notna(zhuopai) else ''
    shengpai = zhuopai.startswith('升')
    diepai = zhuopai.startswith('跌')

    if eq == '等3':
        if bsha5 and lianyang2: return '等3.偏5连门'
        elif bsha5: return '等3.偏5'
        elif bsha3 and lianyang2: return '等3.偏3连门'
        elif lianyang2: return '等3.连'
        elif cengzhu2: return '等3.层主'
        elif diepai: return '等3.跌排'
    elif eq == '等1':
        if bsha5 and lianyang2: return '等1.偏5连门'
        elif bsha5: return '等1.偏5'
        elif cengzhu2: return '等1.层主'
    elif eq == '等2':
        if bsha5 and lianyang2: return '等2.偏5连门'
        elif bsha5: return '等2.偏5'
        elif bsha3 and lianyang2: return '等2.偏3连门'
        elif bsha3: return '等2.偏3'
        elif lianyang2: return '等2.连'
        elif cengzhu2 and shengpai: return '等2.层主升'
        elif shengpai: return '等2.升'
        elif diepai: return '等2.跌排'
    elif eq == '等5':
        if bsha5: return '等5.偏5'
        elif bsha3: return '等5.偏3'
    elif eq == '等6':
        if bsha5: return '等6.偏5'
        elif bsha3: return '等6.偏3'
    elif eq == '等7':
        if bsha5: return '等7.偏5'
        elif bsha3: return '等7.偏3'
    return ''

print('=' * 80)
print('MC3.9q 日策分P2期望HR计算')
print('=' * 80)
print()
wk = load_all()

# 还原策略
wk['等高线'] = wk.apply(lambda r: classify(r['日ZA'], r['中符串']), axis=1)
wk['策略'] = wk.apply(lambda r: strategy_name(r['等高线'], r['BSHA'], r['BT连阳'], r['层界'], r['柱排']), axis=1)

# 统计每个策略的下日HR均值
print('\n[1] 各策略下日HR均值')
print('=' * 60)
results = []
for name, g in wk.groupby('策略'):
    if name == '' or len(g) < MIN_SAMPLE: continue
    avg = g['下日HR'].mean()
    n = len(g)
    results.append((name, avg, n))
    print(f'{name}: n={n:>8,}  下日HR均值={avg:.2f}%')

# 排序
results.sort(key=lambda x: -x[1])
print('\n[2] 按下日HR均值排序')
print('=' * 60)
for name, avg, n in results:
    print(f'{name}: 下日HR均值={avg:.2f}%')

# 生成查表文件
print('\n[3] 生成查表文件')
print('=' * 60)

def 等级(score):
    if score > 60: return 'A'
    if score >= 50: return 'B'
    if score >= 40: return 'C'
    if score >= 30: return 'D'
    return 'E'

# 原始策分（硬编码）
scores = {
    '等3.偏5连门': 58, '等3.偏5': 54, '等3.偏3连门': 53, '等3.连': 49,
    '等3.层主': 44, '等3.跌排': 37,
    '等1.偏5连门': 61, '等1.偏5': 56, '等1.层主': 44,
    '等2.偏5连门': 58, '等2.偏5': 57, '等2.偏3连门': 53, '等2.偏3': 51,
    '等2.连': 48, '等2.层主升': 45, '等2.升': 40, '等2.跌排': 39,
    '等5.偏5': 61, '等5.偏3': 53,
    '等6.偏5': 52, '等6.偏3': 49,
    '等7.偏5': 54, '等7.偏3': 51,
}

# 期望HR用实际下日HR均值取整
hr_map = {name: avg for name, avg, n in results}

lines = ['策略名\t编码']
for name, score in scores.items():
    avg = hr_map.get(name, 0)
    exp_hr = int(round(avg)) if avg > 0 else 0
    if exp_hr > 9: exp_hr = 9
    grade = 等级(score)
    code = f'{exp_hr}{grade}{score}'
    lines.append(f'{name}\t{code}')
    print(f'{name}: 期望HR={exp_hr} (实际均值={avg:.2f}%)  编码={code}')

outpath = os.path.join(OUTDIR, 'vba表日策分P2.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'\n已生成: {outpath}')