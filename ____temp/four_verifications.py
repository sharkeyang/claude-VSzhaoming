"""四项验证：周地型/诱多/日周联动/周冲地型"""
import csv, glob, os
from collections import defaultdict, Counter

DIR = r"D:\@VSwork\VS昭明计划VBA优化\____temp\谕组"
files = sorted(glob.glob(os.path.join(DIR, "谕组_*.csv")))
print(f"数据: {len(files)} 只股票\n")

# ====== ① 周地型对下周冲高概率影响 ======
print("=" * 60)
print("① 周地型对下周冲高概率影响")
print("=" * 60)
# 柱排周格式类似 "升.尾连QQ.Q3", "人.尾连QQ.W2", "跌.尾连QQ.Q3"
# 地型是柱排的第一个字：升/跌/人/蠕/梯等
types = Counter()
冲高 = Counter()
total = 0
for f in files[:500]:
    prev = None
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            col = row.get('柱排周', '')
            hr = row.get('HR', '')
            if not col or not hr: continue
            dz = col[0] if col else '?'
            try:
                hr_val = float(hr)
            except:
                continue
            types[dz] += 1
            if hr_val >= 3:
                冲高[dz] += 1
            total += 1

print(f"\n  总行数: {total:,}")
print(f"\n  各周地型的冲高率(P>=3%):")
for dz in sorted(types, key=lambda x: types[x], reverse=True):
    if types[dz] < 100: continue
    rate = 冲高[dz] / types[dz] * 100
    bar = '#' * int(rate / 2)
    print(f"    {dz}: {rate:5.1f}% ({冲高[dz]:>6,}/{types[dz]:>6,}) {bar}")

# ====== ② 诱多形态定量胜率 ======
print("\n" + "=" * 60)
print("② 诱多形态定量胜率")
print("=" * 60)
# 诱多定义：本周柱排为"升"但下周HR<0
# 使用柱排周 + 下周HR
诱多_阳 = 0
诱多_阴 = 0
诱多_总 = 0
for f in files[:500]:
    rows_list = []
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            rows_list.append(row)
    for i in range(len(rows_list) - 1):
        col = rows_list[i].get('柱排周', '')
        if not col: continue
        if col[0] == '升':
            try:
                next_hr = float(rows_list[i+1].get('HR', 0))
            except:
                continue
            诱多_总 += 1
            if next_hr > 0:
                诱多_阳 += 1
            else:
                诱多_阴 += 1

if 诱多_总 > 0:
    print(f"\n  升排后下周HR>0: {诱多_阳} ({诱多_阳/诱多_总*100:.1f}%)")
    print(f"  升排后下周HR<=0(诱多): {诱多_阴} ({诱多_阴/诱多_总*100:.1f}%)")

# ====== ③ 日周联动叠加效果 ======
print("\n" + "=" * 60)
print("③ 日周联动叠加效果（盈提示分层）")
print("=" * 60)
# 盈提示列: 高/宽/丘等
盈分层 = defaultdict(lambda: {'总':0, '冲高3':0, '冲高5':0})
for f in files[:500]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            yt = row.get('盈提示', '')
            hr = row.get('HR', '')
            if not hr: continue
            try:
                hr_val = float(hr)
            except:
                continue
            盈分层[yt]['总'] += 1
            if hr_val >= 3: 盈分层[yt]['冲高3'] += 1
            if hr_val >= 5: 盈分层[yt]['冲高5'] += 1

print(f"\n  盈提示各等级冲高概率:")
for yt in ['高', '宽', '丘', '', '丘顶']:
    d = 盈分层[yt]
    if d['总'] < 50: continue
    r3 = d['冲高3']/d['总']*100
    r5 = d['冲高5']/d['总']*100
    label = yt if yt else '(无)'
    print(f"    盈{label}: P>=3%={r3:.1f}%  P>=5%={r5:.1f}%  (n={d['总']:,})")

# ====== ④ 周冲地型 + 盈提示叠加 ======
print("\n" + "=" * 60)
print("④ 周冲地型 + 盈提示叠加")
print("=" * 60)
叠加 = defaultdict(lambda: {'总':0, '冲高3':0})
for f in files[:500]:
    with open(f, 'r', encoding='gbk', errors='ignore') as fh:
        for row in csv.DictReader(fh):
            col = row.get('柱排周', '')
            yt = row.get('盈提示', '')
            hr = row.get('HR', '')
            if not col or not hr: continue
            dz = col[0] if col else '?'
            key = f"{dz}|{yt if yt else '无'}"
            try:
                hr_val = float(hr)
            except:
                continue
            叠加[key]['总'] += 1
            if hr_val >= 3: 叠加[key]['冲高3'] += 1

print(f"\n  地型+盈提示 冲高率(P>=3%) Top15:")
scores = [(k, v['冲高3']/v['总']*100, v['总']) for k, v in 叠加.items() if v['总'] >= 50]
scores.sort(key=lambda x: x[1], reverse=True)
for k, r, n in scores[:15]:
    print(f"    {k:12s}: {r:5.1f}% (n={n:,})")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)