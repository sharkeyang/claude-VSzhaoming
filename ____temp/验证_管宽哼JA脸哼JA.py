# -*- coding: utf-8 -*-
"""
用真正的管宽哼JA（脸哼JA[23]）重新验证管宽假设
============================================
用户确认：管宽哼JA = 脸哼JA[23] = (龟结哼/日类JA-1)*100

假设：
1. 管宽哼JA太小（同时触碰顶与DJA）→ 平移/失去上冲动力
2. 管宽哼JA≥5 → 与DSHA≥5相互印证，大部分一致
3. 少数情况管宽大但DSHA回落 → 下跌

列序（旧列序）：[1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [10]柱排 [13]日ZA [19]BSHA [23]脸哼JA(管宽哼JA) [26]次日高幅 [30]上符串
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

def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'

stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    if hr is None: return
    stats[key][0]+=1; stats[key][1]+=(1 if hr>=3 else 0); stats[key][2]+=hr

def report(title, keys):
    print(f'\n{"="*80}')
    print(title)
    print('='*80)
    print(f'{"条件":<46} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*74)
    for k in keys:
        if k in stats:
            s = stats[k]
            print(f'{k:<46} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

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
                sfs = row[30].strip()
                lian = to_f(row[23])  # 脸哼JA = 管宽哼JA
                bsha = to_f(row[19])
                gf = to_f(row[6])
                touch = is_touch(sfs)
                # 管宽哼JA 只在触哼/触顶时有值
                if lian is None: continue

                # ===== 假设1：管宽哼JA太小（同时触顶+DJA）→ 失去动力 =====
                if touch:
                    if zpa is not None and 0 < zpa <= 2:
                        # 同时触顶+触DJA（窄管）
                        if lian < 5: add('H1 触顶+触DJA+管宽<5(极窄)', hr)
                        else: add('H1 触顶+触DJA+管宽≥5', hr)
                    if zpa is not None and zpa > 2:
                        if lian < 5: add('H1 触顶+远离DJA+管宽<5', hr)
                        else: add('H1 触顶+远离DJA+管宽≥5', hr)

                # ===== 假设2：管宽哼JA≥5 vs <5 =====
                if touch:
                    if lian >= 5: add('H2 触顶+管宽哼JA≥5', hr)
                    else: add('H2 触顶+管宽哼JA<5', hr)

                # ===== 假设3：管宽大但DSHA回落 → 下跌 =====
                if touch and lian >= 5 and bsha is not None and gf is not None:
                    if gf < 3: add('H3 触顶+管宽≥5+今高幅<3(DSHA回落)', hr)
                    else: add('H3 触顶+管宽≥5+今高幅≥3(DSHA未回落)', hr)

                # ===== 管宽哼JA vs BSHA 相互印证 =====
                if touch and bsha is not None:
                    if lian >= 5 and bsha >= 5: add('H4 管宽≥5+BSHA≥5(一致)', hr)
                    if lian >= 5 and bsha < 5: add('H4 管宽≥5+BSHA<5(管宽大DSHA小)', hr)
                    if lian < 5 and bsha >= 5: add('H4 管宽<5+BSHA≥5(管宽小DSHA大)', hr)
                    if lian < 5 and bsha < 5: add('H4 管宽<5+BSHA<5(一致)', hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

report('H1 管宽哼JA太小（同时触顶+DJA）→ 失去动力？', [
    'H1 触顶+触DJA+管宽<5(极窄)','H1 触顶+触DJA+管宽≥5',
    'H1 触顶+远离DJA+管宽<5','H1 触顶+远离DJA+管宽≥5',
])
report('H2 管宽哼JA≥5 vs <5（触顶时）', [
    'H2 触顶+管宽哼JA≥5','H2 触顶+管宽哼JA<5',
])
report('H3 管宽大但DSHA回落 → 下跌？', [
    'H3 触顶+管宽≥5+今高幅<3(DSHA回落)','H3 触顶+管宽≥5+今高幅≥3(DSHA未回落)',
])
report('H4 管宽哼JA vs BSHA 相互印证', [
    'H4 管宽≥5+BSHA≥5(一致)','H4 管宽≥5+BSHA<5(管宽大DSHA小)',
    'H4 管宽<5+BSHA≥5(管宽小DSHA大)','H4 管宽<5+BSHA<5(一致)',
])
