# -*- coding: utf-8 -*-
"""按管宽（宽哼JC col24）分类：扩管/平管/窄管，验证次日P3%
扩管=管宽大(正)，平管=管宽接近0，窄管=管宽小(负)
"""
import io, os, glob, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# col8=DXCD, col24=宽哼JC, col26=次日高幅
# 只统计升管（DXZA>0，甲乙己）样本
# 先看管宽分类的次日P3%（次日高幅≥3%）

# 分类：扩管(管宽>50)/平管(管宽-50~50)/窄管(管宽<-50)
# 先看不同管宽区间的次日P3%
bins = [(-10**9, -100, '窄管(管宽<-100)'),
        (-100, -30, '窄管(-100~-30)'),
        (-30, 0, '窄管(-30~0)'),
        (0, 30, '平管(0~30)'),
        (30, 60, '平管(30~60)'),
        (60, 100, '扩管(60~100)'),
        (100, 10**9, '扩管(管宽>100)')]

stats = defaultdict(lambda: {'n': 0, 'p3': 0, 'p5': 0, 'sum_nh': 0})

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 27:
                continue
            try:
                gk = float(row[24])  # 宽哼JC
                nh = float(row[26])  # 次日高幅
            except:
                continue
            # 找管宽区间
            for lo, hi, label in bins:
                if lo <= gk < hi:
                    st = stats[label]
                    st['n'] += 1
                    if nh >= 3:
                        st['p3'] += 1
                    if nh >= 5:
                        st['p5'] += 1
                    st['sum_nh'] += nh
                    break

print('\n=== 管宽分类的次日P3% ===')
for lo, hi, label in bins:
    st = stats[label]
    if st['n'] == 0:
        continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 次日P5%={st["p5"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')