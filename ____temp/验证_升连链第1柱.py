# -*- coding: utf-8 -*-
"""
验证：升连链第1柱（启动柱）介入持有到链末的收益，是否显著高于后续柱。
只统计链长>=2 的升连链（第1柱后有升连），对齐文档口径。
"""
import csv, glob, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组周"
COL_并符串 = 51
COL_周涨 = 1

def 识别升连链(并符串):
    if not 并符串:
        return 0
    当前 = 并符串[-1]
    if 当前 != 'Q':
        return 0
    n = 0
    for ch in reversed(并符串):
        if ch == 'Q':
            n += 1
        else:
            break
    return n

def main():
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    from collections import defaultdict
    介入收益 = defaultdict(list)
    介入单周 = defaultdict(list)
    链长分布 = defaultdict(int)

    for f in files:
        with open(f, encoding='gbk', errors='replace') as fh:
            r = csv.reader(fh)
            header = next(r)
            rows = []
            for row in r:
                if len(row) <= COL_并符串:
                    continue
                try:
                    周涨 = float(row[COL_周涨])
                except:
                    周涨 = 0.0
                rows.append((row[0], 周涨, row[COL_并符串].strip()))

        n = len(rows)
        i = 0
        while i < n:
            位置 = 识别升连链(rows[i][2])
            if 位置 == 0:
                i += 1
                continue
            start = i
            while start - 1 >= 0 and 识别升连链(rows[start-1][2]) > 0:
                start -= 1
            end = i
            while end + 1 < n and 识别升连链(rows[end+1][2]) > 0:
                end += 1
            整链长 = end - start + 1
            if 整链长 < 2:
                i = end + 1
                continue  # 只统计链长>=2
            链长分布[整链长] += 1
            for k in range(start, end+1):
                柱位置 = k - start + 1
                累计 = 1.0
                for m in range(k, end+1):
                    累计 *= (1 + rows[m][1] / 100.0)
                累计收益 = (累计 - 1) * 100
                介入收益[柱位置].append(累计收益)
                介入单周[柱位置].append(rows[k][1])
            i = end + 1

    def 统计(lst):
        if not lst:
            return "n=0"
        lst.sort()
        n = len(lst)
        mean = sum(lst)/n
        med = lst[n//2]
        pos = sum(1 for x in lst if x > 0)/n*100
        return f"n={n} 均={mean:.2f}% 中位={med:.2f}% 正收益={pos:.1f}%"

    print("=== 只统计链长>=2 的升连链 ===")
    print("\n=== 介入第N柱持有到链末的累计收益 ===")
    for 柱 in sorted(介入收益):
        if 柱 <= 8:
            print(f"  第{柱}柱: {统计(介入收益[柱])}")

    print("\n=== 介入第N柱的单周收益 ===")
    for 柱 in sorted(介入单周):
        if 柱 <= 8:
            print(f"  第{柱}柱: {统计(介入单周[柱])}")

if __name__ == "__main__":
    main()