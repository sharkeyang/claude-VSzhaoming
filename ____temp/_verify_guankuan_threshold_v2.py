# -*- coding: utf-8 -*-
"""窄管阈值分析（用正确列 col21=脸哼JA=管宽哼JA）
升管 = DXAB甲乙己(a/b/r) + DXZA>0
列映射（VBA导出代码权威，勿信表头）：
col9=DXAB护型, col13=日ZA, col21=脸哼JA(管宽哼JA), col26=次日高幅, col30=上符串(触顶A), col10=柱排
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

stats = defaultdict(lambda: {'n':0,'p3':0,'sum':0})
def add(label, nh):
    st=stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1
    st['sum']+=nh
def report(label):
    st=stats[label]
    if st['n']==0: return
    print(f'{label}: n={st["n"]}, 占比={st["n"]/stats["升管_基线"]["n"]*100:.2f}%, P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum"]/st["n"]:.2f}%', flush=True)

def parse_row(row):
    if len(row) < 31: return None
    try:
        return {'ab': row[9], 'zp': row[10], 'za': int(row[13]), 'gk': row[21].strip(),
                'nh': float(row[26]), 'sf': row[30]}
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
            if hx in ('a','b','r') and r['za'] > 0:  # 升管 = 甲乙己 + DXZA>0
                add('升管_基线', nh)
                if r['gk'] == '':
                    add('管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    touch = 'A' in r['sf']
                    shengpai = r['zp'].startswith('升.')
                    if 0 < gkv < 3:
                        add('窄管_0-3', nh)
                    elif 3 <= gkv < 4:
                        add('窄管_3-4', nh)
                    elif 4 <= gkv < 5:
                        add('窄管_4-5', nh)
                    elif gkv >= 5:
                        if touch and shengpai:
                            add('扩管', nh)
                        else:
                            add('平管', nh)
                    else:
                        add('管宽<=0', nh)

print('\n=== 升管 管宽分类（col21=脸哼JA 正确列）===', flush=True)
for label in ['升管_基线','管宽<=0','窄管_0-3','窄管_3-4','窄管_4-5','扩管','平管','管宽空']:
    report(label)

# 累计窄管
base = stats['升管_基线']['n']
for a,b,name in [(0,3,'0-3'),(0,4,'0-4'),(0,5,'0-5')]:
    n=0; p3=0; s=0
    for lbl in ['窄管_0-3','窄管_3-4','窄管_4-5']:
        lo,hi = {'窄管_0-3':(0,3),'窄管_3-4':(3,4),'窄管_4-5':(4,5)}[lbl]
        if lo>=a and hi<=b:
            n+=stats[lbl]['n']; p3+=stats[lbl]['p3']; s+=stats[lbl]['sum']
    if n>0:
        print(f'累计窄管{a}-{b}: n={n}, 占比={n/base*100:.2f}%, P3%={p3/n*100:.2f}%, 均高幅={s/n:.2f}%', flush=True)