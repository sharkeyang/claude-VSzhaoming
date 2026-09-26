# -*- coding: utf-8 -*-
"""跌管(丙丁戊+DXZA<0) 各护型 管宽分类（col22 正确列）
列映射：col10=护型, col11=柱排, col14=日ZA, col22=管宽哼JA, col27=次日高幅, col31=上符串
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
import random
LIMIT = int(os.environ.get('FILE_LIMIT', '0'))
if LIMIT:
    random.seed(1)
    files = random.sample(files, LIMIT)
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

for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            row = line.strip().split(',')
            if len(row) < 44: continue
            try:
                hx = row[9].strip()
                zp = row[10]
                za = float(row[13])
                gk = row[21].strip()
                nh = float(row[26])
                sf = row[30]
            except:
                continue
            if hx[:1] not in ('c','z','y'): continue  # 丙丁戊
            if za >= 0: continue  # DXZA<0 跌管
            touch = 'A' in sf
            shengpai = zp.startswith('升.')
            h = hx[:1]
            add(f'跌管_{h}_基线', nh)
            if gk == '':
                add(f'跌管_{h}_管宽空', nh)
            else:
                gkv = float(gk)
                if 0 < gkv < 5:
                    add(f'跌管_{h}_窄管', nh)
                elif gkv >= 5:
                    if touch and shengpai:
                        add(f'跌管_{h}_扩管', nh)
                    else:
                        add(f'跌管_{h}_平管', nh)
                else:
                    add(f'跌管_{h}_管宽<=0', nh)

print('\n=== 跌管(丙丁戊+DXZA<0) 各护型 管宽分类 ===', flush=True)
for label in sorted(stats.keys()):
    report(label)