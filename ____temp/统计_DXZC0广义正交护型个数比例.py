# -*- coding: utf-8 -*-
"""
统计 DXZC>0 时，各 DXAB 广义正交护型的个数比例
====================================================
广义正交定义：己、戊(ZA>0)、甲、乙(ZA>0)、乙(ZA<0)、丙
非广义：戊(ZA<0)、丁

用户问题：甲一般只有一次机会，乙只要DXZA出现就一次机会。
统计 DXZC>0 时各护型（含乙拆 ZA>0/ZA<0）的个数占比。

磁盘CSV列序：9=DXAB, 13=日ZA, 14=日ZC
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池板块映射
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

# 计数: key -> n
cnt = defaultdict(int)
cnt_zc0 = defaultdict(int)   # 全量（不限ZC）用于对照
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                if zc is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                # 分类键：护型 + ZA符号
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                cnt_zc0[key] += 1
                if zc > 0:
                    cnt[key] += 1
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# 广义正交类型（用户定义）
广义类型 = ['己(ZA>0)', '己(ZA=0)', '己(ZA<0)',
          '戊(ZA>0)',
          '甲(ZA>0)', '甲(ZA=0)',
          '乙(ZA>0)', '乙(ZA=0)', '乙(ZA<0)',
          '丙(ZA>0)', '丙(ZA=0)', '丙(ZA<0)']
非广义类型 = ['戊(ZA<0)', '戊(ZA=0)', '丁(ZA>0)', '丁(ZA=0)', '丁(ZA<0)']

def 汇总(keys, label):
    total = sum(cnt[k] for k in keys)
    print(f'  {label}: n={total:,}')
    for k in keys:
        if k in cnt:
            print(f'    {k:<12} {cnt[k]:>10,}  {cnt[k]/total*100:>6.2f}%')

print('=' * 60)
print('DXZC>0 时各广义正交护型个数比例')
print('=' * 60)
汇总(广义类型, '广义正交合计')
print()
汇总(非广义类型, '非广义合计')

# 关键对比：甲 vs 乙(ZA>0)
print()
print('=' * 60)
print('关键对比（DXZC>0）')
print('=' * 60)
甲 = cnt['甲(ZA>0)'] + cnt['甲(ZA=0)']
乙za0 = cnt['乙(ZA>0)']
乙za0_ = cnt['乙(ZA>0)'] + cnt['乙(ZA=0)']
乙all = cnt['乙(ZA>0)'] + cnt['乙(ZA=0)'] + cnt['乙(ZA<0)']
广义总 = sum(cnt[k] for k in 广义类型)
print(f'  甲(全部):            {甲:>10,}  {甲/广义总*100:>6.2f}%')
print(f'  乙(ZA>0):            {乙za0:>10,}  {乙za0/广义总*100:>6.2f}%')
print(f'  乙(ZA>0+ZA=0):       {乙za0_:>10,}  {乙za0_/广义总*100:>6.2f}%')
print(f'  乙(全部):            {乙all:>10,}  {乙all/广义总*100:>6.2f}%')
print(f'  广义正交合计:        {广义总:>10,}')

# 全量对照（不限ZC）
print()
print('=' * 60)
print('对照：全量（不限ZC）各护型个数比例')
print('=' * 60)
tot_all = sum(cnt_zc0.values())
for k in sorted(cnt_zc0, key=lambda x: -cnt_zc0[x]):
    print(f'  {k:<12} {cnt_zc0[k]:>10,}  {cnt_zc0[k]/tot_all*100:>6.2f}%')
