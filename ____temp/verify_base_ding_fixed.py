# -*- coding: utf-8 -*-
"""
基顶型验证 - 修正parse_ding后重新验证
用户指出：基顶型下破时很多是顶态L(离顶)，不是全部顶态G。
原parse_ding把_K/_L前缀错误解析为核心顶型Kd虎天劫/Ld虎天劫，漏掉顶态K/L的基顶型。
"""
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_ding(s):
    """修正版：正确解析顶型前缀
    前缀: _K=已下破+顶态K, _L=已下破+顶态L, _=已下破+顶态G, K=顶态K, L=顶态L, 无=顶态G
    返回(顶态, 核心顶型)
    """
    if not s:
        return None, None
    if s.startswith('_K'): return 'K', s[2:]
    if s.startswith('_L'): return 'L', s[2:]
    if s.startswith('_'): return 'G', s[1:]
    if s.startswith('K'): return 'K', s[1:]
    if s.startswith('L'): return 'L', s[1:]
    return 'G', s

BASE_DING = {'a龙', 'b龙', 'd虎天劫', 'd虎AZ劫'}

# 加载数据
files = []
for fp in glob.glob(DATA_DIR + '/*.csv'):
    frows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62:
                continue
            try:
                dtza = int(row[13])
                ds, dc = parse_ding(row[43])
                frows.append((dtza, ds, dc))
            except (ValueError, IndexError):
                continue
    files.append(frows)

total = sum(len(f) for f in files)
print(f'总行数: {total}')

def rest(frows, i, la=5):
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][0] > 0:
            return True
    return False

# 基顶型 vs 其他顶型（下破DTZA=-1/-2）
base = [0,0]
other = [0,0]
for frows in files:
    for i in range(len(frows)-1):
        dtza, ds, dc = frows[i]
        if dtza in (-1,-2):
            if dc in BASE_DING:
                base[1] += 1
                if rest(frows, i): base[0] += 1
            else:
                other[1] += 1
                if rest(frows, i): other[0] += 1

print('\n=== 基顶型 vs 其他顶型（下破DTZA=-1/-2，修正parse_ding）===')
if base[1]:
    print(f'基顶型: n={base[1]}, 5日重新站上DJA={base[0]/base[1]*100:.1f}%')
if other[1]:
    print(f'其他顶型: n={other[1]}, 5日重新站上DJA={other[0]/other[1]*100:.1f}%')

# 基顶型细分（按核心顶型）
print('\n=== 基顶型细分（按核心顶型）===')
detail = collections.defaultdict(lambda: [0,0])
for frows in files:
    for i in range(len(frows)-1):
        dtza, ds, dc = frows[i]
        if dtza in (-1,-2) and dc in BASE_DING:
            detail[dc][1] += 1
            if rest(frows, i): detail[dc][0] += 1
for k,(restn,tot) in sorted(detail.items(), key=lambda x:-x[1][1]):
    if tot:
        print(f'  {k}: n={tot}, 5日重新站上DJA={restn/tot*100:.1f}%')

# 基顶型按顶态细分
print('\n=== 基顶型按顶态细分（下破DTZA=-1/-2）===')
detail2 = collections.defaultdict(lambda: [0,0])
for frows in files:
    for i in range(len(frows)-1):
        dtza, ds, dc = frows[i]
        if dtza in (-1,-2) and dc in BASE_DING:
            detail2[ds][1] += 1
            if rest(frows, i): detail2[ds][0] += 1
for k,(restn,tot) in sorted(detail2.items(), key=lambda x:-x[1][1]):
    if tot:
        print(f'  顶态{k}: n={tot}, 5日重新站上DJA={restn/tot*100:.1f}%')
