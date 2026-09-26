# -*- coding: utf-8 -*-
"""状态机口径重新统计 §6.7.2.3 出管判定（连阴/阴阳阴 × 下一柱触顶）
升管 = 甲乙己 + 已触哼（flag累积）
列：col5=涨幅, col9=DXAB, col13=日ZA, col26=次日高幅, col30=上符串
"""
import io, sys, glob, os
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
print(f'共 {len(files)} 个文件', flush=True)
stats = defaultdict(lambda: {'n':0,'p3':0,'p5':0,'chu':0,'sum':0})
def parse(row):
    if len(row)<31: return None
    try: return {'ab':row[9],'zf':float(row[5]),'za':int(row[13]),'nh':float(row[26]),'sf':row[30]}
    except: return None
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows=[]
        for line in f:
            r=parse(line.strip().split(','))
            if r is not None: rows.append(r)
    n=len(rows)
    past5=[0.0]*n
    for j in range(n):
        m=0.0
        for k in range(max(0,j-4), j+1):
            m=max(m, rows[k]['nh'])
        past5[j]=m
    flag=False
    for j in range(n):
        r=rows[j]
        hx=r['ab'][0] if r['ab'] else ''
        if hx in ('a','b','r'):
            touch=('B' in r['sf']) or ('A' in r['sf'])
            if touch: flag=True
            if flag and j>=2:  # 在升管中
                yin = r['zf']<0
                yang = r['zf']>0
                yin_prev = rows[j-1]['zf']<0
                yang_prev = rows[j-1]['zf']>0
                yin_prev2 = rows[j-2]['zf']<0
                # 连阴：本柱阴 + 前柱阴
                if yin and yin_prev:
                    ct_next = ('A' in rows[j+1]['sf']) if j+1<n else False
                    label = '连阴_下一柱触顶' if ct_next else '连阴_下一柱未触顶'
                    st=stats[label]; st['n']+=1
                    if r['nh']>=3: st['p3']+=1
                    if past5[j]>=3: st['p5']+=1
                    st['sum']+=r['nh']
                    chu=0
                    for k in range(j+1, min(n,j+4)):
                        hk=rows[k]['ab'][0] if rows[k]['ab'] else ''
                        if hk not in ('a','b','r'): chu=1; break
                    if chu: st['chu']+=1
                # 阴阳阴：本柱阴 + 前柱阳 + 前前柱阴
                elif yin and yang_prev and yin_prev2:
                    ct_next = ('A' in rows[j+1]['sf']) if j+1<n else False
                    label = '阴阳阴_下一柱触顶' if ct_next else '阴阳阴_下一柱未触顶'
                    st=stats[label]; st['n']+=1
                    if r['nh']>=3: st['p3']+=1
                    if past5[j]>=3: st['p5']+=1
                    st['sum']+=r['nh']
                    chu=0
                    for k in range(j+1, min(n,j+4)):
                        hk=rows[k]['ab'][0] if rows[k]['ab'] else ''
                        if hk not in ('a','b','r'): chu=1; break
                    if chu: st['chu']+=1
        else:
            flag=False
print('=== §6.7.2.3 出管判定（状态机口径）===')
for label in ['连阴_下一柱触顶','连阴_下一柱未触顶','阴阳阴_下一柱触顶','阴阳阴_下一柱未触顶']:
    st=stats[label]
    if st['n']>0:
        print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 5天P3%={st["p5"]/st["n"]*100:.2f}%, 3天出管%={st["chu"]/st["n"]*100:.2f}%, 均高幅={st["sum"]/st["n"]:.2f}%')
