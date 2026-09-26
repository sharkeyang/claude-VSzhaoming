# -*- coding: utf-8 -*-
"""跌管（丙丁戊）管宽分类（用户纠正版）验证
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
            # 跌管 = 丙丁戊
            if hx in ('c','d','y'):
                add('跌管_丙丁戊_基线', nh)
                if r['gk'] == '':
                    add(f'跌管_{hx}_管宽空', nh)
                else:
                    gkv = float(r['gk'])
                    if 0 < gkv < 5:
                        add(f'跌管_{hx}_窄管(0-5)', nh)
                    elif gkv >= 5:
                        if tuigaoding:
                            add(f'跌管_{hx}_扩管(>=5+推高顶)', nh)
                        else:
                            add(f'跌管_{hx}_平管(>=5+非推高顶)', nh)
                    else:
                        add(f'跌管_{hx}_管宽<=0', nh)

print('\n=== 跌管（丙丁戊）管宽分类（用户纠正版）===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('跌管'):
        report(label)