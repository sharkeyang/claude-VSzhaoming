# -*- coding: utf-8 -*-
"""探索管宽哼JA(col23) 的正确区分方法
检查 col23 在升管/跌管时的值分布，是否有负值（窄管）
"""
import io, os, glob, sys, random
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
random.seed(42)
sample_files = random.sample(files, 100)
print(f'采样 {len(sample_files)} 个文件')

# col13=日ZA, col23=管宽哼JA(脸哼JA), col24=宽哼JC
# 检查 col23 在升管(ZA>0)/跌管(ZA<0)时的值
za_pos = []   # 升管时的 col23 值
za_neg = []   # 跌管时的 col23 值
za_pos_empty = 0
za_neg_empty = 0
za_pos_total = 0
za_neg_total = 0
col23_neg = []  # col23 负值

for fp in sample_files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for i, line in enumerate(f):
            if i >= 500: break
            row = line.strip().split(',')
            if len(row) < 25: continue
            try:
                za = int(row[13])
            except:
                continue
            v23 = row[23].strip()
            v24 = row[24].strip()
            if za > 0:
                za_pos_total += 1
                if v23 == '':
                    za_pos_empty += 1
                else:
                    try:
                        fv = float(v23)
                        za_pos.append(fv)
                        if fv < 0: col23_neg.append(fv)
                    except:
                        pass
            elif za < 0:
                za_neg_total += 1
                if v23 == '':
                    za_neg_empty += 1
                else:
                    try:
                        za_neg.append(float(v23))
                    except:
                        pass

print(f'\n=== col23(管宽哼JA) 值分布 ===')
print(f'升管(ZA>0): total={za_pos_total}, 空={za_pos_empty}({za_pos_empty/za_pos_total*100:.1f}%), 有值={len(za_pos)}')
if za_pos:
    print(f'  升管有值范围: min={min(za_pos):.1f}, max={max(za_pos):.1f}, 负值={len(col23_neg)}')
    # 分档
    c = Counter()
    for v in za_pos:
        if v > 60: c['扩管>60'] += 1
        elif v >= 0: c['平管0-60'] += 1
        else: c['窄管<0'] += 1
    total = sum(c.values())
    for k in ('扩管>60', '平管0-60', '窄管<0'):
        print(f'  {k}: {c[k]}({c[k]/total*100:.1f}%)')
print(f'跌管(ZA<0): total={za_neg_total}, 空={za_neg_empty}({za_neg_empty/za_neg_total*100:.1f}%), 有值={len(za_neg)}')
if za_neg:
    print(f'  跌管有值范围: min={min(za_neg):.1f}, max={max(za_neg):.1f}')

# 检查 col24(宽哼JC) 在升管/跌管时的值
print(f'\n=== col24(宽哼JC) 值分布 ===')
za_pos24 = []
za_neg24 = []
for fp in sample_files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for i, line in enumerate(f):
            if i >= 500: break
            row = line.strip().split(',')
            if len(row) < 25: continue
            try:
                za = int(row[13])
                v24 = float(row[24])
            except:
                continue
            if za > 0: za_pos24.append(v24)
            elif za < 0: za_neg24.append(v24)
if za_pos24:
    print(f'升管(ZA>0): n={len(za_pos24)}, min={min(za_pos24):.1f}, max={max(za_pos24):.1f}')
    c = Counter()
    for v in za_pos24:
        if v > 60: c['扩管>60'] += 1
        elif v >= 0: c['平管0-60'] += 1
        else: c['窄管<0'] += 1
    total = sum(c.values())
    for k in ('扩管>60', '平管0-60', '窄管<0'):
        print(f'  {k}: {c[k]}({c[k]/total*100:.1f}%)')
if za_neg24:
    print(f'跌管(ZA<0): n={len(za_neg24)}, min={min(za_neg24):.1f}, max={max(za_neg24):.1f}')
