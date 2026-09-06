# -*- coding: utf-8 -*-
"""
被反驳直觉的细粒度上下文拆分：管宽过大 / 三柱跌排
========================================
用户直觉：冲高导致管宽过大要警惕；三柱跌排形成下跌管。
但聚合数据显示相反（管宽越大越好、三柱跌排反而略高）。
本脚本按上下文拆分，看是否在某条件下直觉成立。

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
                lian = to_f(row[23])
                o = to_f(row[2]); c = to_f(row[1]); h = to_f(row[3])
                if o is None or c is None or h is None or c<=0: continue
                upper = (h - max(o,c))/c*100  # 上影
                # 连续上涨天数
                up_days = 0
                j = i
                while j>0:
                    if to_f(rows[j][1]) is not None and to_f(rows[j-1][1]) is not None and to_f(rows[j][1])>to_f(rows[j-1][1]):
                        up_days+=1; j-=1
                    else: break
                # 连续下跌天数
                down_days = 0
                j = i
                while j>0:
                    if to_f(rows[j][1]) is not None and to_f(rows[j-1][1]) is not None and to_f(rows[j][1])<to_f(rows[j-1][1]):
                        down_days+=1; j-=1
                    else: break
                # 连续跌排天数
                die_days = 0
                j = i
                while j>=0 and is_die(rows[j][10].strip()):
                    die_days += 1; j -= 1

                # ============ 管宽过大（≥20）上下文拆分 ============
                if lian is not None and lian >= 20 and zpa > 0:
                    # 连续上涨天数
                    if up_days>=5: add('管宽≥20+连涨≥5', hr)
                    elif up_days>=3: add('管宽≥20+连涨3-4', hr)
                    elif up_days>=1: add('管宽≥20+连涨1-2', hr)
                    else: add('管宽≥20+未连涨', hr)
                    # 长上影
                    if upper>=3: add('管宽≥20+长上影(≥3%)', hr)
                    else: add('管宽≥20+无长上影(<3%)', hr)
                    # 柱排
                    if is_sheng(zp): add('管宽≥20+升排', hr)
                    elif is_die(zp): add('管宽≥20+跌排', hr)
                    else: add('管宽≥20+非升非跌', hr)
                    # 长上影+跌排（冲高回落）
                    if upper>=3 and is_die(zp): add('管宽≥20+长上影+跌排(冲高回落)', hr)
                    else: add('管宽≥20+非(长上影+跌排)', hr)

                # ============ 三柱跌排上下文拆分 ============
                if zpa <= 0 and die_days >= 3:
                    # 连续下跌天数
                    if down_days>=5: add('三柱跌排+连跌≥5', hr)
                    elif down_days>=3: add('三柱跌排+连跌3-4', hr)
                    else: add('三柱跌排+连跌<3', hr)
                    # 是否触底（日ZA接近最低，即ZA很负）
                    if zpa <= -5: add('三柱跌排+深跌(ZA≤-5)', hr)
                    else: add('三柱跌排+浅跌(ZA>-5)', hr)
                    # 止跌信号（今日小阳/十字星）
                    is_stop = (c > o) and (h-c)/c*100 < 1  # 小阳柱
                    if is_stop: add('三柱跌排+今日小阳(止跌)', hr)
                    else: add('三柱跌排+今日非小阳', hr)
                    # 升排（反转）
                    if is_sheng(zp): add('三柱跌排+升排(反转?)', hr)
                    else: add('三柱跌排+非升排', hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

report('管宽过大（≥20）上下文拆分', [
    '管宽≥20+连涨≥5','管宽≥20+连涨3-4','管宽≥20+连涨1-2','管宽≥20+未连涨',
    '管宽≥20+长上影(≥3%)','管宽≥20+无长上影(<3%)',
    '管宽≥20+升排','管宽≥20+跌排','管宽≥20+非升非跌',
    '管宽≥20+长上影+跌排(冲高回落)','管宽≥20+非(长上影+跌排)',
])
report('三柱跌排上下文拆分', [
    '三柱跌排+连跌≥5','三柱跌排+连跌3-4','三柱跌排+连跌<3',
    '三柱跌排+深跌(ZA≤-5)','三柱跌排+浅跌(ZA>-5)',
    '三柱跌排+今日小阳(止跌)','三柱跌排+今日非小阳',
    '三柱跌排+升排(反转?)','三柱跌排+非升排',
])