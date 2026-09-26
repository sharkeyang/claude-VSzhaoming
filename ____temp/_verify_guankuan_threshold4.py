# -*- coding: utf-8 -*-
"""管宽阈值 5→4 全量重验（用户决定 2026-09-21）
新定义：窄管 = 0 < 管宽哼JA < 4；管宽≥4 看推高顶(触顶+升排)=扩管，否则=平管
列映射（VBA导出代码权威）：col9=DXAB, col10=柱排, col13=日ZA, col21=脸哼JA(管宽哼JA), col26=次日高幅, col30=上符串(触顶A), col42=BT连阳(等型)
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

def parse_row(row):
    if len(row) < 43: return None
    try:
        return {'ab': row[9], 'zp': row[10], 'za': int(row[13]), 'gk': row[21].strip(),
                'nh': float(row[26]), 'sf': row[30], 'deng': row[42].strip()}
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
            # 等型
            try: dv = int(r['deng'])
            except: dv = None
            if dv is None: deng='等其他'
            elif dv==1: deng='等1'
            elif dv==2: deng='等2'
            elif dv>=3: deng='等3'
            elif dv==-1: deng='等5'
            elif dv==-2: deng='等6'
            elif dv<=-3: deng='等7'
            else: deng='等其他'
            if hx in ('a','b','r') and r['za'] > 0:  # 升管
                add('升管_基线', nh)
                if r['gk'] == '':
                    add('管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    touch = 'A' in r['sf']
                    shengpai = r['zp'].startswith('升.')
                    zpc = zhupai_class(r['zp'])
                    if 0 < gkv < 4:
                        add('窄管', nh)
                        add(f'窄管_{deng}', nh)
                        add(f'窄管_{zpc}', nh)
                    elif gkv >= 4:
                        if touch and shengpai:
                            add('扩管', nh)
                            add(f'扩管_{deng}', nh)
                            add(f'扩管_{zpc}', nh)
                        else:
                            add('平管', nh)
                            add(f'平管_{deng}', nh)
                            add(f'平管_{zpc}', nh)
                    else:
                        add('管宽<=0', nh)

print('\n=== 升管 管宽分类（阈值4）===', flush=True)
for label in ['升管_基线','管宽<=0','窄管','扩管','平管','管宽空']:
    report(label)

print('\n=== 升管 管宽分类 × 等型 ===', flush=True)
for label in sorted(stats.keys()):
    if '_等' in label:
        report(label)

print('\n=== 升管 管宽分类 × 柱排 ===', flush=True)
for label in sorted(stats.keys()):
    if ('_升' in label or '_跌' in label or '_人' in label) and '_等' not in label:
        report(label)