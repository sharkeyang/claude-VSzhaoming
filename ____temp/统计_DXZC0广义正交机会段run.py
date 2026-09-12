# -*- coding: utf-8 -*-
"""
统计 DXZC>0 时各 DXAB 广义正交护型的"机会段"（连续run）个数比例
====================================================
用户问题：甲一般只有一次机会，乙只要DXZA出现就一次机会。
按行计数会因持续时长不同而失真——甲持续久、乙持续短，行数多不代表机会多。

本脚本改为按"连续机会段（run）"计数：
- 定义：连续 N 天 DXZC>0 且 DXAB 护型相同，视为"一次机会"（一个run）
- 统计 DXZC>0 时各护型 run 的个数比例（这才是"机会次数"语义）

广义正交定义：己、戊(ZA>0)、甲、乙(ZA>0)、乙(ZA<0)、丙
非广义：戊(ZA<0)、丁

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

# 机会段（run）计数: key -> n
run_cnt = defaultdict(int)
# 行计数（对照）
row_cnt = defaultdict(int)
# run 长度分布（用于看"一次机会"持续多久）
run_len = defaultdict(list)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    # 当前 run 状态
    cur_key = None
    cur_len = 0
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
                if not hx:
                    # 无护型：中断当前run
                    if cur_key is not None:
                        run_cnt[cur_key] += 1
                        run_len[cur_key].append(cur_len)
                        cur_key = None; cur_len = 0
                    continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                row_cnt[key] += 1
                if zc > 0:
                    if key == cur_key:
                        cur_len += 1
                    else:
                        # 结束上一个run
                        if cur_key is not None:
                            run_cnt[cur_key] += 1
                            run_len[cur_key].append(cur_len)
                        # 开始新run
                        cur_key = key
                        cur_len = 1
                else:
                    # DXZC<=0：中断当前run
                    if cur_key is not None:
                        run_cnt[cur_key] += 1
                        run_len[cur_key].append(cur_len)
                        cur_key = None; cur_len = 0
            # 文件末尾收尾
            if cur_key is not None:
                run_cnt[cur_key] += 1
                run_len[cur_key].append(cur_len)
                cur_key = None; cur_len = 0
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

# 广义正交类型
广义类型 = ['己(ZA>0)', '戊(ZA>0)', '甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '丙(ZA<0)']
非广义类型 = ['戊(ZA<0)', '丁(ZA<0)']

def 汇总(keys, label):
    total = sum(run_cnt[k] for k in keys)
    print(f'  {label}: 机会段={total:,}')
    for k in keys:
        if k in run_cnt:
            lens = run_len[k]
            avg = sum(lens)/len(lens) if lens else 0
            med = sorted(lens)[len(lens)//2] if lens else 0
            print(f'    {k:<12} {run_cnt[k]:>10,}  {run_cnt[k]/total*100:>6.2f}%  平均{avg:.1f}天/中位{med}天')

print('=' * 70)
print('DXZC>0 时各广义正交护型"机会段"（连续run）个数比例')
print('=' * 70)
汇总(广义类型, '广义正交合计')
print()
汇总(非广义类型, '非广义合计')

# 关键对比
print()
print('=' * 70)
print('关键对比（机会段口径）')
print('=' * 70)
甲 = run_cnt['甲(ZA>0)']
乙za0 = run_cnt['乙(ZA>0)']
乙all = run_cnt['乙(ZA>0)'] + run_cnt['乙(ZA<0)']
广义总 = sum(run_cnt[k] for k in 广义类型)
print(f'  甲(ZA>0):        {甲:>10,}  {甲/广义总*100:>6.2f}%')
print(f'  乙(ZA>0):        {乙za0:>10,}  {乙za0/广义总*100:>6.2f}%')
print(f'  乙(全部):        {乙all:>10,}  {乙all/广义总*100:>6.2f}%')
print(f'  广义正交合计:    {广义总:>10,}')

# 行计数对照
print()
print('=' * 70)
print('对照：行计数口径（DXZC>0）')
print('=' * 70)
tot_row = sum(row_cnt[k] for k in 广义类型)
for k in 广义类型:
    if k in row_cnt:
        print(f'  {k:<12} {row_cnt[k]:>10,}  {row_cnt[k]/tot_row*100:>6.2f}%')
