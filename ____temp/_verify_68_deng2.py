# -*- coding: utf-8 -*-
"""验证2修正：等2 正交初期回落DJA反弹
正交初期 = DXAB 刚转正（前一日 DXAB<=0 或 前一日日ZA<0）
回落DJA = 当日日ZA=2（站上DJA第2柱）
看：正交初期回落DJA 的次日P3%，以及继续触顶形成垒升（触顶）的增强
列映射：col9=DXAB, col13=日ZA, col23=管宽哼JA, col26=次日高幅, col30=上符串
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'p3':0,'sum_nh':0})
def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1
    st['sum_nh']+=nh
def report(label):
    st = stats[label]
    if st['n']==0: return
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%', flush=True)

def parse_row(row):
    if len(row) < 31: return None
    try:
        return {'ab': row[9], 'za': int(row[13]), 'gk': row[23].strip(),
                'nh': float(row[26]), 'sf': row[30]}
    except:
        return None

for fp in files:
    rows = []
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            r = parse_row(line.strip().split(','))
            if r is not None: rows.append(r)
    for i, cur in enumerate(rows):
        if i == 0: continue
        prev = rows[i-1]
        hx = cur['ab'][0] if cur['ab'] else ''
        touch = 'A' in cur['sf']
        nh = cur['nh']
        # 等2 = 日ZA=2
        if cur['za'] == 2 and hx in ('a','b','r'):
            add('等2_基线', nh)
            if touch: add('等2_触顶', nh)
            else: add('等2_未触顶', nh)
            # 正交初期 = 前一日日ZA<0（刚从跌管转正）或 前一日日ZA<=0
            if prev['za'] <= 0:
                add('等2_正交初期(前日ZA<=0)', nh)
                if touch: add('等2_正交初期_触顶', nh)
            # 更严格：前一日日ZA<0（刚上穿）
            if prev['za'] < 0:
                add('等2_正交初期(前日ZA<0)', nh)
                if touch: add('等2_正交初期(前日ZA<0)_触顶', nh)
            # 管宽哼JA 分类（正交初期）
            if prev['za'] <= 0:
                if cur['gk'] == '': gk_class = '空'
                else:
                    gkv = float(cur['gk'])
                    if gkv > 60: gk_class = '扩管>60'
                    elif gkv >= 0: gk_class = '平管0-60'
                    else: gk_class = '窄管<0'
                add(f'等2_正交初期_{gk_class}', nh)

print('\n=== 等2 正交初期回落DJA反弹 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等2'):
        report(label)
