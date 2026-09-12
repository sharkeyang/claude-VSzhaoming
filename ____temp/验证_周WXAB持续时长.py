# -*- coding: utf-8 -*-
"""
周级别 WXAB 正向/负向 平均持续时长 + WXCD 区分
====================================================
WXAB正向 = 护级 上/忐/忠 (ZC>0)
WXAB负向 = 护级 中/忑/下 (ZC<0)
持续时长 = 连续同方向(正向/负向)的周数

输出：
  ① WXAB 正向/负向 平均持续时长（总体）
  ② 按 WXCD 区分（金升/银升/唏待 vs 屎降/尿降/嘘待）
  ③ 各 WXCD 下 正向/负向 持续时长

周CSV列序：4=WXAB, 13=WXCD
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

def get_huji(wxab):
    """提取WXAB护级：上/忐/忠/中/忑/下"""
    m = re.search(r'[上忐忠中忑下]', wxab)
    return m.group(0) if m else None

def is_pos(huji):
    return huji in ('上', '忐', '忠')

def get_wxcd_cat(wxcd):
    """WXCD分类：金升/银升/唏待=正向，屎降/尿降/嘘待=负向"""
    if wxcd.startswith('金升') or wxcd.startswith('银升') or wxcd.startswith('唏'):
        return '正向WXCD'
    if wxcd.startswith('屎降') or wxcd.startswith('尿降') or wxcd.startswith('嘘'):
        return '负向WXCD'
    return '其他'

# 持续时长统计: key -> 时长列表
durations = defaultdict(list)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组周')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组周_sz') or fname.startswith('谕组周_sh')): continue
    code = fname.replace('谕组周_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    cur_dir = None  # '正向'/'负向'
    cur_len = 0
    cur_wxcd = None
    try:
        with open(os.path.join('昭明算展/谕组周', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 13: continue
                wxab = row[4].strip()
                wxcd = row[13].strip()
                huji = get_huji(wxab)
                if huji is None: continue
                direction = '正向' if is_pos(huji) else '负向'
                wxcd_cat = get_wxcd_cat(wxcd)
                if direction == cur_dir and wxcd_cat == cur_wxcd:
                    cur_len += 1
                else:
                    if cur_dir is not None:
                        durations[f'总体-{cur_dir}'].append(cur_len)
                        durations[f'{cur_wxcd}-{cur_dir}'].append(cur_len)
                    cur_dir = direction
                    cur_wxcd = wxcd_cat
                    cur_len = 1
            if cur_dir is not None:
                durations[f'总体-{cur_dir}'].append(cur_len)
                durations[f'{cur_wxcd}-{cur_dir}'].append(cur_len)
    except Exception:
        pass

print(f'周级别高波池文件: {files_core}')
print()

def show(label, key):
    lst = durations[key]
    if not lst: return
    n = len(lst)
    avg = sum(lst)/n
    med = sorted(lst)[n//2]
    mx = max(lst)
    mn = min(lst)
    print(f'{label:<24} 段数{n:>6,} 平均{avg:>6.2f}周 中位{med:>4}周 最长{mx:>4}周 最短{mn:>3}周')

print('=' * 70)
print('① WXAB 正向/负向 平均持续时长（总体）')
print('=' * 70)
show('正向(上/忐/忠)', '总体-正向')
show('负向(中/忑/下)', '总体-负向')

print()
print('=' * 70)
print('② 按 WXCD 区分（正向WXCD vs 负向WXCD）')
print('=' * 70)
show('正向WXCD-正向', '正向WXCD-正向')
show('正向WXCD-负向', '正向WXCD-负向')
show('负向WXCD-正向', '负向WXCD-正向')
show('负向WXCD-负向', '负向WXCD-负向')
