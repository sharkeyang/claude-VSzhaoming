# -*- coding: utf-8 -*-
"""按扩管/平管/窄管分类验证（管宽=宽哼JC col24）
扩管=管宽>60，平管=管宽0~60，窄管=管宽<0
统计次日P3%、5天P3%（次日高幅col26）
"""
import io, os, glob, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 分类
def classify(gk):
    if gk > 60:
        return '扩管(管宽>60)'
    elif gk >= 0:
        return '平管(管宽0~60)'
    else:
        return '窄管(管宽<0)'

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
            label = classify(gk)
            st = stats[label]
            st['n'] += 1
            if nh >= 3:
                st['p3'] += 1
            if nh >= 5:
                st['p5'] += 1
            st['sum_nh'] += nh

print('\n=== 扩管/平管/窄管 分类验证 ===')
for label in ('扩管(管宽>60)', '平管(管宽0~60)', '窄管(管宽<0)'):
    st = stats[label]
    if st['n'] == 0:
        continue
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 次日P5%={st["p5"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%')