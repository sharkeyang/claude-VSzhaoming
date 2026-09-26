# -*- coding: utf-8 -*-
"""窄管阈值分析：0-3 / 0-4 / 0-5 分布 + 次日P3%
升管 = DXAB甲乙己(a/b/r) + DXZA>0
列映射：col9=DXAB, col13=日ZA, col23=管宽哼JA, col26=次日高幅
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

# 统计：升管总数、各窄管阈值区间
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
    if len(row) < 27: return None
    try:
        return {'ab': row[9], 'za': int(row[13]), 'gk': row[23].strip(), 'nh': float(row[26])}
    except:
        return None

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            r = parse_row(line.strip().split(','))
            if r is None: continue
            hx = r['ab'][0] if r['ab'] else ''
            nh = r['nh']
            # 升管 = 甲乙己 + DXZA>0
            if hx in ('a','b','r') and r['za'] > 0:
                add('升管_基线', nh)
                if r['gk'] == '':
                    add('升管_管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    if 0 < gkv < 3:
                        add('窄管_0-3', nh)
                    elif 3 <= gkv < 4:
                        add('窄管_3-4', nh)
                    elif 4 <= gkv < 5:
                        add('窄管_4-5', nh)
                    elif 0 < gkv < 4:
                        add('窄管_0-4', nh)
                    elif 0 < gkv < 5:
                        add('窄管_0-5', nh)
                    elif gkv >= 5:
                        add('管宽>=5', nh)
                    else:
                        add('管宽<=0', nh)

print('\n=== 升管 窄管阈值分析（升管=甲乙己+DXZA>0）===', flush=True)
for label in ['升管_基线','管宽<=0','窄管_0-3','窄管_3-4','窄管_4-5','窄管_0-4','窄管_0-5','管宽>=5','升管_管宽空']:
    report(label)

# 计算占比
base = stats['升管_基线']['n']
print(f'\n=== 占比（占升管基线 {base}）===', flush=True)
for label in ['窄管_0-3','窄管_0-4','窄管_0-5','管宽>=5']:
    st = stats[label]
    if base>0:
        print(f'{label}: {st["n"]/base*100:.2f}%', flush=True)