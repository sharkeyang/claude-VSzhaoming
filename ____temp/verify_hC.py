# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 猜想C: 转换态(上破DJA 1-2柱, 日ZA=1或2), 结合DXZC(价格vs DJC)
# 验证: DXZA>0且DXZC>0 vs DXZA>0且DXZC<0, 后续进入升管(5日内仍站上DJA)概率
# 用日ZC[14]近似DXZB方向
rC = defaultdict(lambda:[0,0])  # (DXZC符号, 柱排) -> [样本, 5日仍升管]

# 同时验证: 上破DJA后(日ZA=1), 柱排升排 vs 跌排, 后续方向
rC_zhu = defaultdict(lambda:[0,0])

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
        cur_zc = int(row[14])
        zhu = row[10]
        # 转换态: 上破DJA 1-2柱 (日ZA=1或2)
        if cur_za in (1,2):
            # 5日内仍升管(日ZA>0)
            still = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    still = 1
                    break
            # 按DXZC符号
            if cur_zc > 0:
                grp = 'DXZC>0'
            elif cur_zc < 0:
                grp = 'DXZC<0'
            else:
                grp = 'DXZC=0'
            rC[grp][0] += 1
            if still: rC[grp][1] += 1
            # 按柱排
            zc = zhu_dir_class(zhu)
            rC_zhu[zc][0] += 1
            if still: rC_zhu[zc][1] += 1
    n += 1

print('总文件:', n)
print('\n=== 猜想C: 转换态(上破DJA 1-2柱) 按DXZC符号 5日内仍升管概率 ===')
print(f"{'DXZC':<10}{'样本':>9}{'5日仍升管':>10}{'P':>8}")
for grp in ['DXZC>0','DXZC<0','DXZC=0']:
    tot, still = rC[grp]
    if tot == 0: continue
    print(f"{grp:<10}{tot:>9}{still:>10}{still/tot*100:>7.2f}%")

print('\n=== 转换态(上破DJA 1-2柱) 按柱排 5日内仍升管概率 ===')
print(f"{'柱排':<10}{'样本':>9}{'5日仍升管':>10}{'P':>8}")
for zc, (tot, still) in sorted(rC_zhu.items(), key=lambda x:-x[1][0]):
    if tot == 0: continue
    print(f"{zc:<10}{tot:>9}{still:>10}{still/tot*100:>7.2f}%")
