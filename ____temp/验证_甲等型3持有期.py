# -*- coding: utf-8 -*-
"""
验证：DXZC>0 + 甲 + 等型3 持有期收益（持有到护型转坏或ZC转负）
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# 持有期收益：从入场（甲+ZC>0+等型3）持有到退出（次日非甲 或 ZC<=0）
# 收益 = 累计涨幅（用每日涨幅[5]累加）
stats = defaultdict(lambda: [0,0,0.0,0])  # 等型 -> [n, 盈利count, sum_ret, sum_days]

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            i = 0
            while i < len(rows):
                row = rows[i]
                if len(row) <= 44: i+=1; continue
                if not row[9].strip().startswith('a'): i+=1; continue
                zc = to_f(row[14])
                if zc is None or zc <= 0: i+=1; continue
                dx = row[44].strip()
                if dx != '等3': i+=1; continue
                # 入场，持有到退出
                ret = 0.0
                days = 0
                j = i
                while j < len(rows):
                    r2 = rows[j]
                    if len(r2) <= 14: break
                    # 检查退出条件（从第2天开始）
                    if j > i:
                        if not r2[9].strip().startswith('a'): break  # 护型转坏
                        zc2 = to_f(r2[14])
                        if zc2 is None or zc2 <= 0: break  # ZC转负
                    # 累加当日涨幅
                    zf = to_f(r2[5])
                    if zf is not None:
                        ret += zf
                    days += 1
                    j += 1
                s = stats[dx]
                s[0]+=1
                s[1]+=(1 if ret>0 else 0)
                s[2]+=ret
                s[3]+=days
                i = j  # 跳到退出位置
    except Exception: pass

print('DXZC>0 + 甲 + 等型3 持有期收益（持有到护型转坏或ZC转负）')
print(f'{"等型":<8} {"n":>10} {"胜率":>8} {"均收益":>8} {"均持有天数":>8}')
for k in sorted(stats.keys()):
    s = stats[k]
    if s[0] < 100: continue
    print(f'{k:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {s[3]/s[0]:>7.1f}天')
