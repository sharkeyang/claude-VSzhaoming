# -*- coding: utf-8 -*-
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

# 验证重新站上DJA后: 站稳 vs 诱多
# 重新站上(前一日跌管, 今日升管)后:
# 站稳 = 后续DTZA升到>=3(确认升管) 或 5日仍升管
# 诱多 = 后续又跌破DJA(日ZA<0)
# 按重新站上时的柱排分类, 找诱多典型模式
r = defaultdict(lambda:[0,0,0,0.0])  # (柱排) -> [样本, 站稳(5日仍升管), 诱多(5日又跌破), 5日收益和]

def zhu_class(zhu):
    if zhu.startswith('升') and '连' in zhu: return '升连'
    if zhu.startswith('升') and '吞' in zhu: return '升吞'
    if zhu.startswith('升'): return '升排'
    if zhu.startswith('跌') and '连' in zhu: return '跌连'
    if zhu.startswith('跌') and '孕' in zhu: return '跌孕'
    if zhu.startswith('跌') and '吞' in zhu: return '跌吞'
    if zhu.startswith('跌'): return '跌排'
    if zhu.startswith('(人)'): return '阴阳阴'
    if zhu.startswith('(升)人'): return '(升)人'
    if zhu.startswith('(跌)人'): return '(跌)人'
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
        hx0 = row[9][0]; za = int(row[13]); zhu = row[10]
        if hx0 not in ('a','b','r'): continue
        if za > 0 and i > 0:
            za_prev = int(rows[i-1][13])
            if za_prev < 0:
                # 重新站上点
                zc = zhu_class(zhu)
                # 5日仍升管(站稳)
                still5 = 0
                for j in range(i+1, min(i+6, len(rows))):
                    if int(rows[j][13]) > 0:
                        still5 = 1
                        break
                # 5日又跌破(诱多)
                brk5 = 0
                for j in range(i+1, min(i+6, len(rows))):
                    if int(rows[j][13]) < 0:
                        brk5 = 1
                        break
                ret5 = 0.0
                try:
                    cur = float(row[1])
                    exit5 = float(rows[min(i+5, len(rows)-1)][1])
                    ret5 = (exit5 - cur) / cur * 100
                except: pass
                r[zc][0] += 1
                if still5: r[zc][1] += 1
                if brk5: r[zc][2] += 1
                r[zc][3] += ret5
    n += 1

print('总文件:', n)
print('\n=== 重新站上DJA后 按柱排: 站稳 vs 诱多 ===')
print(f"{'柱排':<10}{'样本':>9}{'5日站稳':>9}{'P站稳':>8}{'5日诱多':>9}{'P诱多':>8}{'5日收益':>9}")
for k,(tot,still,brk,sret) in sorted(r.items(), key=lambda x:-x[1][0]):
    if tot < 1000: continue
    print(f"{k:<10}{tot:>9}{still:>9}{still/tot*100:>7.2f}%{brk:>9}{brk/tot*100:>7.2f}%{sret/tot:>8.3f}%")
