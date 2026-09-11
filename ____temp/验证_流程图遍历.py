# -*- coding: utf-8 -*-
"""
护型操作决策流程图遍历验证：随机10个代码，检查每个柱是否都能找到操作指南
====================================================
流程图逻辑（§4.8.4.1）：
- 起点：DXZC>0 区域（DXCD=上/忐）
- 护型8选1：甲/乙ZA>0/己=可做；乙ZA<0=交叉路口；丙=持仓或退出；戊ZA>0=观察；丁/戊ZA<0=放弃
- 介入时机：DJA丘 + 日等型 + BSHA5
- 持有监控退出信号

报告：遍历随机代码，统计每个柱落入哪个分支，报告流程图覆盖不到的柱。
"""
import csv, os, sys, random
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = [k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')]

def to_f(v):
    try: return float(v)
    except: return None

# 随机选10个代码
random.seed(42)
codes = random.sample(high, 10)
print(f'随机10个代码: {codes}')
print()

# 统计每个柱的分支
branch_cnt = Counter()
uncovered = []  # 覆盖不到的柱
total_rows = 0
files_core = 0

for code in codes:
    fname = f'谕组日_{code}.csv'
    path = os.path.join('昭明算展/谕组日', fname)
    if not os.path.exists(path):
        print(f'  [缺失] {code}')
        continue
    files_core += 1
    with open(path, encoding='gbk') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) <= 14: continue
            dxcd = row[8].strip()
            dxab = row[9].strip()
            za = to_f(row[13])
            if za is None: continue
            total_rows += 1
            hx = dxab[0] if dxab else ''
            # 判断流程图分支
            if dxcd in ('上', '忐'):
                # DXZC>0 区域
                if hx == 'a' and za > 0:
                    branch_cnt['甲ZA>0-可做'] += 1
                elif hx == 'b' and za > 0:
                    branch_cnt['乙ZA>0-可做'] += 1
                elif hx == 'r' and za > 0:
                    branch_cnt['己ZA>0-可做'] += 1
                elif hx == 'b' and za < 0:
                    branch_cnt['乙ZA<0-交叉路口'] += 1
                elif hx == 'c':
                    branch_cnt['丙-持仓或退出'] += 1
                elif hx == 'y' and za > 0:
                    branch_cnt['戊ZA>0-观察'] += 1
                elif hx == 'z':
                    branch_cnt['丁-放弃'] += 1
                elif hx == 'y' and za < 0:
                    branch_cnt['戊ZA<0-放弃'] += 1
                else:
                    branch_cnt['其他-未覆盖'] += 1
                    uncovered.append((code, row[0], dxcd, dxab, za))
            elif dxcd == '忠':
                branch_cnt['DXCD=忠-未覆盖'] += 1
                uncovered.append((code, row[0], dxcd, dxab, za))
            else:
                # DXCD=中/下/忑 (DXZC<0)
                branch_cnt['DXCD中下忑-未覆盖'] += 1
                uncovered.append((code, row[0], dxcd, dxab, za))

print(f'遍历 {files_core} 个代码，共 {total_rows} 行')
print()
print('=' * 60)
print('流程图分支覆盖统计')
print('=' * 60)
for k, v in branch_cnt.most_common():
    print(f'{k:<24} {v:>8,}  {v/total_rows*100:>6.2f}%')

print()
print('=' * 60)
print('覆盖不到的柱（未找到操作指南）')
print('=' * 60)
uncovered_cnt = sum(v for k, v in branch_cnt.items() if '未覆盖' in k)
print(f'未覆盖总数: {uncovered_cnt:,} ({uncovered_cnt/total_rows*100:.2f}%)')
print()
# 按类型汇总未覆盖
uncovered_by_type = Counter(u[2] for u in uncovered)
print('未覆盖按DXCD类型:')
for k, v in uncovered_by_type.most_common():
    print(f'  {k}: {v:,} ({v/uncovered_cnt*100:.2f}%)')
print()
print('未覆盖样例（前20条）:')
for u in uncovered[:20]:
    print(f'  {u[0]} {u[1]} DXCD={u[2]} DXAB={u[3]} ZA={u[4]}')