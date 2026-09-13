# -*- coding: utf-8 -*-
"""
基顶型验证 - 详细检查
用户怀疑算错。检查：
1. 顶态范围（G only vs G+K vs 全部）对基顶型站上率的影响
2. 基顶型定义（a龙/b龙/d虎天劫/d虎AZ劫）
3. 下破DTZA=-1/-2 + 重新站上判定
"""
import csv, glob, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日0911'

def parse_ding(s):
    """解析顶型: 返回(顶态, 核心顶型)
    a龙 -> ('G','a龙')   _a龙 -> ('G','a龙')
    Kd虎天劫 -> ('K','d虎天劫')  Ld虎天劫 -> ('L','d虎天劫')
    """
    if not s:
        return None, None
    if s[0] in ('K', 'L'):
        return s[0], s[1:]
    if s[0] == '_':
        return 'G', s[1:]
    return 'G', s

BASE_DING = {'a龙', 'b龙', 'd虎天劫', 'd虎AZ劫'}

# 加载数据（只保留需要的列）
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
    """未来la天内是否重新站上DJA(日ZA>0)"""
    for j in range(i+1, min(i+1+la, len(frows))):
        if frows[j][0] > 0:
            return True
    return False

# 不同顶态范围
for state_filter, label in [
    (lambda s: s == 'G', '顶态G only'),
    (lambda s: s in ('G','K'), '顶态G+K'),
    (lambda s: True, '全部顶态'),
]:
    base = [0,0]  # [站上, 总数]
    other = [0,0]
    for frows in files:
        for i in range(len(frows)-1):
            dtza, ds, dc = frows[i]
            if dtza in (-1,-2) and state_filter(ds):
                if dc in BASE_DING:
                    base[1] += 1
                    if rest(frows, i): base[0] += 1
                else:
                    other[1] += 1
                    if rest(frows, i): other[0] += 1
    print(f'\n=== {label} ===')
    if base[1]:
        print(f'基顶型: n={base[1]}, 5日重新站上DJA={base[0]/base[1]*100:.1f}%')
    if other[1]:
        print(f'其他顶型: n={other[1]}, 5日重新站上DJA={other[0]/other[1]*100:.1f}%')

# 基顶型细分（顶态G+K）
print('\n=== 基顶型细分（顶态G+K）===')
detail = collections.defaultdict(lambda: [0,0])
for frows in files:
    for i in range(len(frows)-1):
        dtza, ds, dc = frows[i]
        if dtza in (-1,-2) and ds in ('G','K') and dc in BASE_DING:
            detail[dc][1] += 1
            if rest(frows, i): detail[dc][0] += 1
for k,(restn,tot) in sorted(detail.items(), key=lambda x:-x[1][1]):
    if tot:
        print(f'  {k}: n={tot}, 5日重新站上DJA={restn/tot*100:.1f}%')
