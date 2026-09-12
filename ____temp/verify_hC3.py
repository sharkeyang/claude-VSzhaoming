# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 护级→DXZB符号映射（VBA定义 神谕.bas:4818-4835）
# 上/中/忐 -> DXZB>0 (JZ>JB)
# 下/忠/忑 -> DXZB<0 (JZ<JB)
# 护型字符串位3 = 护级

# 猜想C: 转换态(上破DJA 1-2柱, 日ZA=1或2), 用护级判定DXZB
rC = defaultdict(lambda:[0,0])  # (DXZB符号) -> [样本, 5日仍升管]
# 同时验证护级分布
huji = defaultdict(int)

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
        hx = row[9]
        # 护级 = 位3 (方向符号后)
        # 格式: a甲↗上1.I -> 位0=a,位1=甲,位2=↗,位3=上
        if len(hx) < 4: continue
        huji_char = hx[3]
        huji[huji_char] += 1
        if huji_char in ('上','中','忐'):
            dxzb = 'DXZB>0'
        elif huji_char in ('下','忠','忑'):
            dxzb = 'DXZB<0'
        else:
            continue
        # 转换态: 上破DJA 1-2柱 (日ZA=1或2)
        if cur_za in (1,2):
            still = 0
            for j in range(i+1, min(i+6, len(rows))):
                if int(rows[j][13]) > 0:
                    still = 1
                    break
            rC[dxzb][0] += 1
            if still: rC[dxzb][1] += 1
    n += 1

print('总文件:', n)
print('\n护级分布:', dict(huji))
print('\n=== 猜想C: 转换态(上破DJA 1-2柱) 用护级判定DXZB 5日内仍升管概率 ===')
print(f"{'DXZB':<10}{'样本':>9}{'5日仍升管':>10}{'P':>8}")
for grp in ['DXZB>0','DXZB<0']:
    tot, still = rC[grp]
    if tot == 0: continue
    print(f"{grp:<10}{tot:>9}{still:>10}{still/tot*100:>7.2f}%")
