# -*- coding: utf-8 -*-
"""
DXAB 广义正交护型覆盖上涨区域验证（高波池）
任务1：验证 DXZC>0 的 DXAB 广义正交护型是否覆盖上涨区域
广义正交护型 = 己、戊(DXZA>0)、甲、乙(DXZA>0)、乙(DXZA<0)、戊
即：除 丁、戊(DXZA<0) 外的所有护型
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def parse_dxab(dxab):
    """解析DXAB编码，返回(护型汉字, 正交符号, DXZA)"""
    if len(dxab) < 3: return ('','','')
    hx = dxab[1]
    zj = dxab[2]
    # DXZA从DXAB编码提取（如 'a甲↗上1.I' 里的 '1'）
    # 格式：a甲↗上1.I 或 z丁↘忑-1.Y暂
    # DXZA在符号后的数字
    import re
    m = re.search(r'[↗→↘]([+-]?\d+)', dxab)
    dxza = m.group(1) if m else ''
    return (hx, zj, dxza)

def to_f(v):
    try: return float(v)
    except: return None

# 统计
stats = defaultdict(lambda: [0,0,0.0])  # key -> [n, hr3, sum_hr]
def add(key, hr):
    s = stats[key]; s[0]+=1
    if hr>=3: s[1]+=1
    s[2]+=hr

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                zc = to_f(row[14])
                za = to_f(row[13])
                hr = to_f(row[26])  # 次日高幅
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx, zj, dxza_s = parse_dxab(dxab)
                if hx == '': continue
                dxza = to_f(dxza_s)
                # 只统计 DXZC>0
                if zc <= 0: continue
                # 广义正交护型：己、戊(DXZA>0)、甲、乙(DXZA>0)、乙(DXZA<0)、戊
                # 即：除 丁、戊(DXZA<0) 外的所有
                if hx == '丁':
                    add('丁(非广义)', hr)
                elif hx == '戊' and dxza is not None and dxza < 0:
                    add('戊(DXZA<0)(非广义)', hr)
                else:
                    add('广义正交护型', hr)
                add('基线(DXZC>0)', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== DXZC>0 上涨区域覆盖验证 ===')
for key in ['广义正交护型','丁(非广义)','戊(DXZA<0)(非广义)','基线(DXZC>0)']:
    if key in stats:
        s = stats[key]
        print(f'{key:<20} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')
print()
# 覆盖占比
total = stats['基线(DXZC>0)'][0]
covered = stats['广义正交护型'][0]
print(f'广义正交护型覆盖 DXZC>0 样本占比: {covered/total*100:.2f}%')
print(f'未覆盖(丁+戊DXZA<0)占比: {(total-covered)/total*100:.2f}%')