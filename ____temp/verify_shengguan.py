# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
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

# 猜想A: 升管中(日ZA>0) 出现跌排/跌连/跌吞, 后续是否下破DJA(进入跌管)
# 需要跨行: 记录当前行(升管+跌排), 看后续N日内是否下破DJA
# 简化: 看次日是否下破DJA(日ZA<0), 以及3日内是否下破
# 同时看: 跌排后是否立刻回升(次日日ZA仍>0)

# 结果: (护型, 柱排方向) -> [样本, 次日下破, 3日内下破, 次日仍升管]
r = defaultdict(lambda:[0,0,0,0])

n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r_csv = csv.reader(f)
        next(r_csv)
        for row in r_csv:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        cur_za = int(row[13])
        cur_hx = row[9][0]
        zhu = row[10]
        # 升管中: 日ZA>0
        if cur_za > 0:
            zc = zhu_dir_class(zhu)
            # 只看跌排/跌连/跌吞/升排
            if zc in ('升排','跌排','跌吞'):
                # 次日
                nxt_za = int(rows[i+1][13])
                nxt_hr = float(rows[i+1][26])
                # 3日内是否下破
                brk3 = 0
                for j in range(i+1, min(i+4, len(rows))):
                    if int(rows[j][13]) < 0:
                        brk3 = 1
                        break
                r[(cur_hx, zc)][0] += 1
                if nxt_za < 0: r[(cur_hx, zc)][1] += 1
                if brk3: r[(cur_hx, zc)][2] += 1
                if nxt_za > 0: r[(cur_hx, zc)][3] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己'}
print('总文件:', n)
print('\n=== 猜想A: 升管中(日ZA>0) 各柱排方向 后续下破DJA概率 ===')
print(f"{'护型':<4}{'柱排':<6}{'样本':>9}{'次日下破':>9}{'P次日下破':>10}{'3日内下破':>10}{'P3日下破':>10}{'次日仍升管':>11}{'P次日仍升':>10}")
for hx in ['a','b','r']:
    for zc in ['升排','跌排','跌吞']:
        tot, brk1, brk3, still = r[(hx,zc)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{zc:<6}{tot:>9}{brk1:>9}{brk1/tot*100:>9.2f}%{brk3:>10}{brk3/tot*100:>9.2f}%{still:>11}{still/tot*100:>9.2f}%")
