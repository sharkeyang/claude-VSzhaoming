# -*- coding: utf-8 -*-
"""统计三柱组合分布，看跌吞+升孕+跌吞等是否真的为0"""
import csv, io, os
from collections import Counter
COL_ZC=14; COL_ZP=10; COL_GF=6
DIE=0x4e0b; SHENG=0x5347; REN=0x4eba; LIAN=0x8dcc
TUN=0x541e; YUN=0x5b55; FAN=0x53cd; LIAN2=0x8fde
def cls(zp):
    if zp.startswith('('): head=zp[1:2]; body=zp[3:]
    else: head=zp[0:1]; body=zp[1:]
    codes=[ord(c) for c in body]
    if TUN in codes: tail='吞'
    elif YUN in codes: tail='孕'
    elif LIAN2 in codes: tail='连'
    elif FAN in codes: tail='反'
    else: tail='其他'
    hc=ord(head)
    if hc==DIE: h='跌'
    elif hc==SHENG: h='升'
    elif hc==REN: h='人'
    elif hc==LIAN: h='连'
    else: h='其他'
    return h,tail
files=[f for f in os.listdir('昭明算展/谕组日') if f.endswith('.csv')]
comb=Counter()
for fi,fname in enumerate(files):
    try:
        with io.open(os.path.join('昭明算展/谕组日',fname),'r',encoding='gbk') as f:
            r=csv.reader(f); next(r)
            rows=[]
            for row in r:
                if len(row)<=COL_GF: continue
                try: zc=float(row[COL_ZC])
                except: continue
                rows.append((zc,row[COL_ZP],row[COL_GF]))
            for i in range(len(rows)-3):
                if rows[i][0]<=0: continue
                h0,t0=cls(rows[i][1]); h1,t1=cls(rows[i+1][1]); h2,t2=cls(rows[i+2][1])
                comb[f'{h0}{t0}+{h1}{t1}+{h2}{t2}']+=1
    except: pass
    if (fi+1)%2000==0: print(f'  处理{fi+1}')
for k in ['跌吞+升孕+跌吞','跌孕+升孕+跌吞','跌孕+升吞+跌孕']:
    print(f'{k}: {comb.get(k,0)}')
print('最常见组合:')
for k,v in comb.most_common(10):
    print(f'  {k}: {v}')