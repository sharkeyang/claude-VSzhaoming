# -*- coding: utf-8 -*-
"""等3 管宽分类（用户纠正版）× 柱排 细分
窄管 = 0 < 管宽哼JA < 5
管宽≥5：推高顶(触顶+升排)=扩管，否则=平管
列映射：col9=DXAB, col10=柱排, col13=日ZA, col23=管宽哼JA, col26=次日高幅, col30=上符串(触顶A)
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

def zhupai_class(zp):
    if zp.startswith('升.'):
        if '尾连' in zp: return '升连'
        elif '尾吞' in zp: return '升吞'
        elif '尾反孕' in zp: return '升孕'
        else: return '升排其他'
    elif zp.startswith('跌.'):
        if '尾连' in zp: return '跌连'
        elif '尾吞' in zp: return '跌吞'
        elif '尾反孕' in zp: return '跌孕'
        else: return '跌排其他'
    elif zp.startswith('('):
        return '人排'
    else:
        return '其他'

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
        return {'ab': row[9], 'zp': row[10], 'za': int(row[13]), 'gk': row[23].strip(),
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
            touch = 'A' in r['sf']
            shengpai = r['zp'].startswith('升.')
            tuigaoding = touch and shengpai
            zpc = zhupai_class(r['zp'])
            if r['za'] >= 3 and hx in ('a','b','r'):
                add('等3_基线', nh)
                if r['gk'] == '':
                    add('等3_管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    if 0 < gkv < 5:
                        add(f'等3_窄管_{zpc}', nh)
                    elif gkv >= 5:
                        if tuigaoding:
                            add(f'等3_扩管_{zpc}', nh)
                        else:
                            add(f'等3_平管_{zpc}', nh)
                    else:
                        add('等3_管宽<=0', nh)

print('\n=== 等3 管宽分类 × 柱排（推高顶=触顶+升排）===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等3'):
        report(label)