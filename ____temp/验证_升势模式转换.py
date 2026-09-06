# -*- coding: utf-8 -*-
"""
升势运行模式转换关系分析（C6 6.6.4.5 补充）
========================================
模式A：单向连续触顶（合顶≥3）
模式B：阶梯上升（前日触DJA→今日触顶）

分析：
1. 模式A/B的持续时长分布
2. 模式A→B、B→A 的转换概率
3. 转换后的次日冲高率
4. 模式A/B 与 非升势（普通触顶）的对比

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
def is_touch(sfs):
    s = sfs.strip()
    return bool(s) and s[-1]=='A'

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

# 模式持续时长统计: (mode, duration) -> count
duration = defaultdict(int)
# 模式转换: (from_mode, to_mode) -> count
transition = defaultdict(int)
# 模式序列（每只股票）
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
            # 先计算每行的模式
            modes = []  # 每行: 'A'/'B'/'N'(非升势)
            for i,row in enumerate(rows):
                if len(row) <= 30:
                    modes.append('N'); continue
                zpa = to_f(row[13])
                if zpa is None:
                    modes.append('N'); continue
                sfs = row[30].strip()
                touch = is_touch(sfs)
                hetop = 0
                if touch:
                    for ch in reversed(sfs):
                        if ch=='A': hetop+=1
                        else: break
                prev = rows[i-1] if i>0 else None
                prev_za = to_f(prev[13]) if prev else None
                modeA = touch and hetop>=3
                modeB = touch and prev_za is not None and 0 < prev_za <= 2
                if modeA: modes.append('A')
                elif modeB: modes.append('B')
                else: modes.append('N')
            # 统计持续时长（连续相同模式）
            i = 0
            while i < len(modes):
                m = modes[i]
                if m in ('A','B'):
                    j = i
                    while j < len(modes) and modes[j]==m:
                        j += 1
                    duration[(m, j-i)] += 1
                    i = j
                else:
                    i += 1
            # 统计转换（A/B 之间的转换）
            for i in range(1, len(modes)):
                if modes[i-1] in ('A','B') and modes[i] in ('A','B') and modes[i-1]!=modes[i]:
                    transition[(modes[i-1], modes[i])] += 1
            # 转换后的次日冲高率
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                if i==0: continue
                prev_mode = modes[i-1]; cur_mode = modes[i]
                if prev_mode in ('A','B') and cur_mode in ('A','B') and prev_mode!=cur_mode:
                    add(f'{prev_mode}→{cur_mode} 转换后次日冲高', hr)
                # 模式A/B 持续中（非转换）的次日冲高
                if prev_mode==cur_mode and cur_mode in ('A','B'):
                    add(f'{cur_mode} 持续中次日冲高', hr)
    except Exception:
        pass
    files_core += 1

print(f'高波池文件: {files_core}')

# 持续时长分布
print('\n' + '='*84)
print('模式持续时长分布')
print('='*84)
print(f'{"模式":<6} {"持续1天":>10} {"持续2天":>10} {"持续3天":>10} {"持续4天":>10} {"持续5天+":>10}')
print('-'*60)
for m in ['A','B']:
    d1 = duration[(m,1)]; d2 = duration[(m,2)]; d3 = duration[(m,3)]
    d4 = duration[(m,4)]; d5p = sum(duration[(m,k)] for k in range(5,20))
    total = d1+d2+d3+d4+d5p
    if total==0: continue
    print(f'{m:<6} {d1/total*100:>9.1f}% {d2/total*100:>9.1f}% {d3/total*100:>9.1f}% {d4/total*100:>9.1f}% {d5p/total*100:>9.1f}%')

# 转换概率
print('\n' + '='*84)
print('模式转换概率')
print('='*84)
for fm in ['A','B']:
    total = sum(transition[(fm,tm)] for tm in ['A','B'])
    if total==0: continue
    for tm in ['A','B']:
        if fm==tm: continue
        cnt = transition[(fm,tm)]
        print(f'{fm}→{tm}: {cnt} ({cnt/total*100:.1f}%)')

report('模式转换后的次日冲高率', [
    'A→B 转换后次日冲高','B→A 转换后次日冲高',
    'A 持续中次日冲高','B 持续中次日冲高',
])
