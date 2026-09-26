# -*- coding: utf-8 -*-
"""状态机口径重新统计 §6.7.2.4 出管边界优化（DJB宽松边界）
升管 = 甲乙己 + 已触哼（flag累积）
入管点 = flag 从 False 变 True（触哼入升管）
出管A(旧)：变非甲乙己 或 DXZA<0
出管B(新)：变丙丁戊(DXZB<0)
列：col9=DXAB, col13=日ZA, col30=上符串
"""
import io, sys, glob, os
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
print(f'共 {len(files)} 个文件', flush=True)
stats = defaultdict(lambda: {'n':0,'daysA':0,'daysB':0})
def parse(row):
    if len(row)<31: return None
    try: return {'ab':row[9],'za':int(row[13]),'sf':row[30]}
    except: return None
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows=[]
        for line in f:
            r=parse(line.strip().split(','))
            if r is not None: rows.append(r)
    n=len(rows)
    flag=False
    for j in range(n):
        r=rows[j]
        hx=r['ab'][0] if r['ab'] else ''
        if hx in ('a','b','r'):
            touch=('B' in r['sf']) or ('A' in r['sf'])
            if touch and not flag:  # 触哼入升管（flag从False变True）
                flag=True
                st=stats['入管后']
                st['n']+=1
                # 到出管A：变非甲乙己 或 DXZA<0
                daysA=None
                for k in range(1,15):
                    if j+k>=n: break
                    hk=rows[j+k]['ab'][0] if rows[j+k]['ab'] else ''
                    if hk not in ('a','b','r') or rows[j+k]['za']<0:
                        daysA=k; break
                # 到出管B：变丙丁戊(DXZB<0)
                daysB=None
                for k in range(1,15):
                    if j+k>=n: break
                    hk=rows[j+k]['ab'][0] if rows[j+k]['ab'] else ''
                    if hk not in ('a','b','r'):
                        daysB=k; break
                st['daysA']+=daysA if daysA else 15
                st['daysB']+=daysB if daysB else 15
        else:
            flag=False
st=stats['入管后']
print(f'=== §6.7.2.4 出管边界优化（状态机口径）===')
print(f'入管样本: {st["n"]}')
print(f'到出管A(旧,变非甲乙己或DXZA<0)平均天数: {st["daysA"]/st["n"]:.2f}')
print(f'到出管B(新,变丙丁戊/DXZB<0)平均天数: {st["daysB"]/st["n"]:.2f}')
print(f'出管B比出管A多容忍天数: {st["daysB"]/st["n"]-st["daysA"]/st["n"]:.2f}')
