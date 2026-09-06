# -*- coding: utf-8 -*-
"""
持有过程中两个管（哼JA / JA哈）的状态监控验证
========================================
课题：持有过程中要考虑两个管（哼JA管 / JA哈管）。

DJA之上（哼JA管）：
  考虑是否在哼JA管稳定运行。警惕：DJA之上跌连、回归DJA、冲高导致管宽过大。

下破DJA（JA哈管）：
  考虑是否在JA哈管形成稳定下跌柱排通道。DJA之下三柱跌排很可能形成下跌管。
  如果出现升排、上破DJA，要看是否真正上破，是否是诱多。

列序（旧列序）：[1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [10]柱排 [13]日ZA [19]BSHA [23]脸哼JA [26]次日高幅 [30]上符串
"""
import csv, os, sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

def to_f(v):
    try: return float(v)
    except: return None
def is_die(zp): return '跌' in zp
def is_sheng(zp): return '升' in zp

stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr

def report(title, keys):
    print(f'\n{"="*84}')
    print(title)
    print('='*84)
    print(f'{"条件":<52} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*80)
    for k in keys:
        if k in stats:
            s = stats[k]
            print(f'{k:<52} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

files_core = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                zpa = to_f(row[13])
                if zpa is None: continue
                zp = row[10].strip()
                lian = to_f(row[23])  # 脸哼JA = 管宽哼JA
                # 前2日（用于判断三柱跌排）
                p1 = rows[i-1] if i>0 else None
                p2 = rows[i-2] if i>1 else None
                p1_zp = p1[10].strip() if p1 else ''
                p2_zp = p2[10].strip() if p2 else ''
                # 连续跌排天数（从今日往前数）
                die_days = 0
                j = i
                while j>=0 and is_die(rows[j][10].strip()):
                    die_days += 1; j -= 1

                # ============ DJA之上（哼JA管） ============
                if zpa > 0:
                    # 稳定运行 vs 警惕信号
                    # 警惕1：跌连（连续跌排）
                    if die_days >= 3: add('DJA上+跌连≥3(警惕)', hr)
                    elif die_days == 2: add('DJA上+跌连=2', hr)
                    elif die_days == 1: add('DJA上+跌连=1', hr)
                    else: add('DJA上+无跌连(稳定)', hr)
                    # 警惕2：回归DJA（日ZA接近0）
                    if zpa <= 2: add('DJA上+回归DJA(ZA≤2)', hr)
                    else: add('DJA上+远离DJA(ZA>2)', hr)
                    # 警惕3：管宽过大（脸哼JA大）
                    if lian is not None:
                        if lian >= 20: add('DJA上+管宽过大(≥20)', hr)
                        elif lian >= 10: add('DJA上+管宽10-20', hr)
                        elif lian >= 5: add('DJA上+管宽5-10', hr)
                        else: add('DJA上+管宽<5', hr)
                    # 稳定运行：无跌连 + 远离DJA + 管宽适中
                    if die_days==0 and zpa>2 and lian is not None and 5<=lian<20:
                        add('DJA上+稳定运行(无跌连+远离+管宽适中)', hr)

                # ============ 下破DJA（JA哈管） ============
                if zpa <= 0:
                    # 三柱跌排（形成下跌管）
                    if die_days >= 3: add('DJA下+三柱跌排(形成下跌管)', hr)
                    elif die_days == 2: add('DJA下+两柱跌排', hr)
                    elif die_days == 1: add('DJA下+单柱跌排', hr)
                    else: add('DJA下+无跌排', hr)
                    # 升排/上破DJA 是否真正上破（诱多 vs 真突破）
                    if is_sheng(zp): add('DJA下+升排(可能上破)', hr)
                    if is_sheng(zp) and die_days==0: add('DJA下+升排+无跌排(真突破?)', hr)
                    if is_sheng(zp) and die_days>=1: add('DJA下+升排+有跌排(诱多?)', hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

report('DJA之上（哼JA管）状态监控', [
    'DJA上+无跌连(稳定)','DJA上+跌连=1','DJA上+跌连=2','DJA上+跌连≥3(警惕)',
    'DJA上+远离DJA(ZA>2)','DJA上+回归DJA(ZA≤2)',
    'DJA上+管宽<5','DJA上+管宽5-10','DJA上+管宽10-20','DJA上+管宽过大(≥20)',
    'DJA上+稳定运行(无跌连+远离+管宽适中)',
])
report('下破DJA（JA哈管）状态监控', [
    'DJA下+无跌排','DJA下+单柱跌排','DJA下+两柱跌排','DJA下+三柱跌排(形成下跌管)',
    'DJA下+升排(可能上破)','DJA下+升排+无跌排(真突破?)','DJA下+升排+有跌排(诱多?)',
])
