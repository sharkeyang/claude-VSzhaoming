# -*- coding: utf-8 -*-
"""升管(甲乙己+DXZA>0) 等3 × 柱排 管宽分类（col22 正确列）
列映射：col10=护型, col11=柱排, col14=日ZA, col22=管宽哼JA, col27=次日高幅, col31=上符串, col43=等型
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
                deng = row[42].strip()
            except:
                continue
            if hx[:1] not in ('a','b','r'): continue  # 甲乙己
            if za <= 0: continue  # DXZA>0 升管
            try: dv = int(deng)
            except: continue
            if dv < 3: continue  # 等3 = ZA>=3
            touch = 'A' in sf
            shengpai = zp.startswith('升.')
            zpc = zhupai_class(zp)
            add('等3_基线', nh)
            if gk == '':
                add('等3_管宽空', nh)
            else:
                gkv = float(gk)
                if 0 < gkv < 5:
                    add(f'等3_窄管_{zpc}', nh)
                elif gkv >= 5:
                    if touch and shengpai:
                        add(f'等3_扩管_{zpc}', nh)
                    else:
                        add(f'等3_平管_{zpc}', nh)
                else:
                    add('等3_管宽<=0', nh)

print('\n=== 升管(甲乙己+DXZA>0) 等3 管宽分类 × 柱排 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等3'):
        report(label)