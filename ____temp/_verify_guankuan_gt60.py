# -*- coding: utf-8 -*-
"""验证管宽哼JA(col23) >60 的真实案例
管宽哼JA = (最近5日最高价/EMA5 - 1)*100
找 >60 的行，打印完整上下文（收/开/高/低/涨幅/高幅/BSHA/管宽哼JA/日ZA）
列映射：col1=收, col2=开, col3=高, col4=低, col5=涨幅, col6=高幅, col13=日ZA, col21=BSHA, col23=管宽哼JA
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))

# 统计管宽哼JA 值分布（更细）
dist = defaultdict(int)
cases = []  # 存 >60 的案例
total = 0
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 31: continue
            try:
                gk = row[23].strip()
                if gk == '': continue
                gkv = float(gk)
            except: continue
            total += 1
            if gkv > 60:
                dist['>60'] += 1
                if len(cases) < 15:
                    cases.append((fp, row))
            elif gkv > 50: dist['50-60'] += 1
            elif gkv > 40: dist['40-50'] += 1
            elif gkv > 30: dist['30-40'] += 1
            elif gkv > 20: dist['20-30'] += 1
            elif gkv > 10: dist['10-20'] += 1
            else: dist['0-10'] += 1

print(f'管宽哼JA 有值总行数: {total}')
print('\n=== 管宽哼JA 值分布 ===')
for k in ['>60','50-60','40-50','30-40','20-30','10-20','0-10']:
    v = dist[k]
    print(f'{k}: {v} ({v/total*100:.2f}%)')

print('\n=== 管宽哼JA >60 的真实案例（前15个）===')
for fp, row in cases:
    print(f'文件: {os.path.basename(fp)}')
    print(f'  日期={row[0]} 收={row[1]} 开={row[2]} 高={row[3]} 低={row[4]} 涨幅={row[5]} 高幅={row[6]}')
    print(f'  日ZA={row[13]} BSHA={row[21]} 管宽哼JA={row[23]} 宽哼JC={row[24]}')
    print()
