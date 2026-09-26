# -*- coding: utf-8 -*-
"""理解管宽（宽哼JC col22）分布，为扩管/平管/窄管分类做准备"""
import io, os, glob, sys
from collections import Counter
import statistics

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 抽样读取，理解管宽（col22）分布
# col8=DXCD, col22=宽哼JC, col28=次日高幅
samples = []
for fp in files[:100]:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 29:
                continue
            try:
                gk = float(row[24])  # 宽哼JC (col24)
                nh = float(row[26])  # 次日高幅 (col26, 表头stale)
            except:
                continue
            samples.append((gk, nh))

print(f'抽样样本: {len(samples)}')
gks = [s[0] for s in samples]
print(f'管宽(宽哼JC)分布: 最少 {min(gks):.2f}, 最多 {max(gks):.2f}, 平均 {statistics.mean(gks):.2f}, 中位 {statistics.median(gks):.2f}')
# 分位数
gks_sorted = sorted(gks)
n = len(gks_sorted)
for p in (10, 25, 50, 75, 90):
    idx = int(n * p / 100)
    print(f'  {p}分位: {gks_sorted[idx]:.2f}')

# 管宽为0或负的比例
zero = sum(1 for g in gks if g <= 0)
print(f'管宽<=0: {zero} ({zero/len(gks)*100:.1f}%)')