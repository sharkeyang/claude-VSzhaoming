# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_dir_class(zhu):
    if zhu.startswith('升'):
        if '连' in zhu: return '升连'
        if '吞' in zhu: return '升吞'
        return '升排'
    if zhu.startswith('跌'):
        if '吞' in zhu: return '跌吞'
        return '跌排'
    if zhu.startswith('(升)人'): return '(升)人'
    if zhu.startswith('(跌)人'): return '(跌)人'
    if zhu.startswith('(人)'): return '(人)人'
    return '其他'

# 跌管中(日ZA<0) 各柱排方向 后续上破DJA(转入升管)概率
# 镜面映射§2.9.2: 升管中跌排/跌吞=靠近DJA(DJA丘结束)但不进入跌管
# 跌管中阳柱/升连/升吞=靠近DJA(跌管中DJA丘结束)但不转入升管
r = defaultdict(lambda:[0,0,0,0])  # (护型,柱排) -> [样本, 次日上破, 3日上破, 次日仍跌管]

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
        # 跌管中: 日ZA<0
        if cur_za < 0:
            zc = zhu_dir_class(zhu)
            # 只看阳柱/升连/升吞/升排
            if zc in ('升连','升吞','升排'):
                nxt_za = int(rows[i+1][13])
                brk3 = 0
                for j in range(i+1, min(i+4, len(rows))):
                    if int(rows[j][13]) > 0:
                        brk3 = 1
                        break
                r[(cur_hx, zc)][0] += 1
                if nxt_za > 0: r[(cur_hx, zc)][1] += 1
                if brk3: r[(cur_hx, zc)][2] += 1
                if nxt_za < 0: r[(cur_hx, zc)][3] += 1
    n += 1

HX = {'a':'甲','b':'乙','r':'己','c':'丙','y':'戊','z':'丁'}
print('总文件:', n)
print('\n=== 跌管中(日ZA<0) 阳柱/升连/升吞 后续上破DJA(转入升管)概率 ===')
print(f"{'护型':<4}{'柱排':<6}{'样本':>9}{'次日上破':>9}{'P次日上破':>10}{'3日上破':>9}{'P3日上破':>10}{'次日仍跌管':>11}{'P次日仍跌':>10}")
for hx in ['a','b','r','c','y','z']:
    for zc in ['升连','升吞','升排']:
        tot, brk1, brk3, still = r[(hx,zc)]
        if tot == 0: continue
        print(f"{HX[hx]:<4}{zc:<6}{tot:>9}{brk1:>9}{brk1/tot*100:>9.2f}%{brk3:>9}{brk3/tot*100:>9.2f}%{still:>11}{still/tot*100:>9.2f}%")
