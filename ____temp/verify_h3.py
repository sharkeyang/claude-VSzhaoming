# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_dir_class(zhu):
    if zhu.startswith('升'):
        return '升排'
    if zhu.startswith('跌'):
        if '吞' in zhu:
            return '跌吞'
        return '跌排'
    if zhu.startswith('(升)'):
        return '(升)人'
    if zhu.startswith('(跌)'):
        return '(跌)人'
    if zhu.startswith('(人)'):
        return '(人)人'
    return '其他'

# 假设3: 甲+等3, 按柱排分组, 验证:
#  (a) 次日冲高P(>=3%)
#  (b) 次日下破DJA(次日日ZA<0)
#  (c) 次日是否结束DJA丘(次日护型不再是甲)
# 跨行: 记录当前行(甲+等3)的柱排, 看下一行
jia_e3 = defaultdict(lambda:[0,0,0,0])  # 柱排 -> [样本, 冲高, 下破DJA, 转非甲]

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62: continue
            rows.append(row)
    # 逐行处理, 用下一行判断
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        cur_hx = row[9][0]
        deng = row[44]
        zhu = row[10]
        if cur_hx == 'a' and deng == '等3':
            grp = zhu_dir_class(zhu)
            try:
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            jia_e3[grp][0] += 1
            if next_hr_f > 3: jia_e3[grp][1] += 1
            if next_za < 0: jia_e3[grp][2] += 1
            if nxt[9][0] != 'a': jia_e3[grp][3] += 1
    n += 1

print('总文件:', n)
print('\n=== 假设3: 甲+等3 按柱排分组 (次日冲高/下破DJA/转非甲) ===')
print(f"{'柱排':<10}{'样本':>9}{'次日冲高':>10}{'P冲高':>8}{'下破DJA':>9}{'P下破':>8}{'转非甲':>8}{'P转非甲':>9}")
for grp, (tot, hit, brk, zhuan) in sorted(jia_e3.items()):
    p1 = hit/tot*100 if tot else 0
    p2 = brk/tot*100 if tot else 0
    p3 = zhuan/tot*100 if tot else 0
    print(f"{grp:<10}{tot:>9}{hit:>10}{p1:>7.2f}%{brk:>9}{p2:>7.2f}%{zhuan:>8}{p3:>8.2f}%")
