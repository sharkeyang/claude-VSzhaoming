# -*- coding: utf-8 -*-
"""分析 0<WXAB<=3 (AB周=1,2,3) 叠加其他条件后的下周冲高(HR>=3%)概率
谕组周CSV: 主期[0] 周涨[1] PR[2] HR[3] WXAB[4] 波型[5] 柱排周[6] WXCD[13] ZA周[14] AB周[21] ZC周[16]
下周冲高 = 同一股票下一行的 HR >= 3
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')
print(f'股票数: {len(files)}')

# 四态映射：WXAB护型首字母
def sitai(wxab):
    if not wxab: return ''
    c = wxab[0]
    if c in 'ab': return '龙'
    if c == 'c': return '雀'
    if c in 'zy': return '虎'
    if c == 'r': return '武'
    return ''

def huxing(wxab):
    if not wxab: return ''
    c = wxab[0]
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(c, '')

# 统计结构: 条件 -> [冲高次数, 总次数]
stats = defaultdict(lambda: [0, 0])

for f in files:
    with open(f, encoding='gbk') as fh:
        reader = csv.reader(fh)
        next(reader)
        prev = None  # (ab, wxab, box, zhupai, wxcd, za, zc)
        for row in reader:
            if len(row) < 22:
                prev = None
                continue
            try:
                ab = int(row[21])
                hr = float(row[3])
            except:
                prev = None
                continue
            if prev is not None:
                p_ab, p_wxab, p_box, p_zhupai, p_wxcd, p_za, p_zc = prev
                # 只统计 0<WXAB<=3 (AB周=1,2,3)
                if 1 <= p_ab <= 3:
                    hit = 1 if hr >= 3 else 0
                    st = sitai(p_wxab)
                    hx = huxing(p_wxab)
                    # 基础
                    stats['[基线] 0<WXAB<=3'][1] += 1
                    stats['[基线] 0<WXAB<=3'][0] += hit
                    # 四态
                    if st:
                        stats[f'四态={st}'][1] += 1
                        stats[f'四态={st}'][0] += hit
                    # 护型
                    if hx:
                        stats[f'护型={hx}'][1] += 1
                        stats[f'护型={hx}'][0] += hit
                    # 柱排
                    if p_zhupai:
                        z = p_zhupai[0]
                        stats[f'柱排={z}'][1] += 1
                        stats[f'柱排={z}'][0] += hit
                    # WXCD
                    if p_wxcd:
                        stats[f'WXCD={p_wxcd}'][1] += 1
                        stats[f'WXCD={p_wxcd}'][0] += hit
                    # ZA正负
                    if p_za is not None:
                        stats[f'ZA{"正" if p_za>0 else "负"}'][1] += 1
                        stats[f'ZA{"正" if p_za>0 else "负"}'][0] += hit
                    # ZC正负
                    if p_zc is not None:
                        stats[f'ZC{"正" if p_zc>0 else "负"}'][1] += 1
                        stats[f'ZC{"正" if p_zc>0 else "负"}'][0] += hit
                    # 四态×柱排
                    if st and p_zhupai:
                        z = p_zhupai[0]
                        stats[f'{st}×柱排{z}'][1] += 1
                        stats[f'{st}×柱排{z}'][0] += hit
                    # 四态×WXCD
                    if st and p_wxcd:
                        stats[f'{st}×WXCD{p_wxcd}'][1] += 1
                        stats[f'{st}×WXCD{p_wxcd}'][0] += hit
            # 更新prev
            try:
                prev = (ab, row[4], row[5], row[6], row[13], float(row[14]) if row[14] else None, float(row[16]) if row[16] else None)
            except:
                prev = None

# 输出，按概率排序，样本>=1000
print()
print(f'{"条件":<20}{"样本":>8}{"下周HR≥3%":>10}{"概率":>8}')
results = []
for k, (hit, total) in stats.items():
    if total >= 1000:
        results.append((k, hit, total, hit/total*100))
results.sort(key=lambda x: -x[3])
for k, hit, total, pct in results:
    print(f'{k:<20}{total:>8}{hit:>10}{pct:>7.1f}%')