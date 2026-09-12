# -*- coding: utf-8 -*-
import csv, glob
from collections import defaultdict

files = glob.glob('谕组日_*.csv')

def zhu_dir_class(zhu):
    if zhu.startswith('升'):
        return '升排'
    if zhu.startswith('跌'):
        if '吞' in zhu:
            return '跌吞'
        return '跌排'
    if zhu.startswith('(升)'):
        return '(升)人'
    if zhu.startswith('(跌)'):
        return '(跌)人'
    if zhu.startswith('(人)'):
        return '(人)人'
    return '其他'

# 收集甲+等2样本
samples = []
n=0
for fp in files:
    rows = []
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 62: continue
            rows.append(row)
    for i in range(len(rows)-1):
        row = rows[i]
        nxt = rows[i+1]
        cur_hx = row[9][0]
        prev_hx = rows[i-1][9][0] if i>0 else None
        deng = row[44]
        if cur_hx == 'a' and deng == '等2':
            try:
                dtza = int(row[13])
                next_hr_f = float(nxt[26])
                next_za = int(nxt[13])
            except:
                continue
            zhong = row[33]
            mo = zhong[-1] if zhong else '?'
            zhu_dir = zhu_dir_class(row[10])
            is_zhuan = (prev_hx == 'r')
            samples.append((dtza, mo, zhu_dir, is_zhuan, next_hr_f, next_za))
    n += 1

print('甲+等2 总样本:', len(samples))

# 坏信号候选
def moDEF(s): return s[1] in 'DEF'
def moD(s): return s[1] == 'D'
def moEF(s): return s[1] in 'EF'
def moDEF_dtza10(s): return s[1] in 'DEF' and s[0]>10
def moDEF_dtza3(s): return s[1] in 'DEF' and s[0]>3
def moDEF_die(s): return s[1] in 'DEF' and s[2] in ('跌排','跌吞')
def moD_die(s): return s[1]=='D' and s[2] in ('跌排','跌吞')
def moDEF_nozhuan(s): return s[1] in 'DEF' and not s[3]

# 好信号候选
def moC(s): return s[1] == 'C'
def moC_zhuan(s): return s[1]=='C' and s[3]
def moC_dtza3(s): return s[1]=='C' and s[0]<=3
def moC_sheng(s): return s[1]=='C' and s[2]=='升排'
def moC_zhuan_sheng(s): return s[1]=='C' and s[3] and s[2]=='升排'

print('\n=== 坏信号候选 (甲+等2) ===')
print(f"{'条件':<24}{'样本':>9}{'下破':>8}{'P下破':>8}{'冲高':>8}{'P冲高':>8}")
for name, fn in [
    ('末位DEF', moDEF), ('末位D', moD), ('末位EF', moEF),
    ('末位DEF+DTZA>10', moDEF_dtza10), ('末位DEF+DTZA>3', moDEF_dtza3),
    ('末位DEF+跌排/跌吞', moDEF_die), ('末位D+跌排/跌吞', moD_die),
    ('末位DEF+非转甲', moDEF_nozhuan),
]:
    sub = [s for s in samples if fn(s)]
    tot = len(sub)
    if tot == 0:
        print(f"{name:<24}{0:>9}"); continue
    brk = sum(1 for s in sub if s[5]<0)
    hit = sum(1 for s in sub if s[4]>3)
    print(f"{name:<24}{tot:>9}{brk:>8}{brk/tot*100:>7.2f}%{hit:>8}{hit/tot*100:>7.2f}%")

print('\n=== 好信号候选 (甲+等2) ===')
print(f"{'条件':<24}{'样本':>9}{'下破':>8}{'P下破':>8}{'冲高':>8}{'P冲高':>8}")
for name, fn in [
    ('末位C', moC), ('末位C+由己转甲', moC_zhuan), ('末位C+DTZA<=3', moC_dtza3),
    ('末位C+升排', moC_sheng), ('末位C+由己转甲+升排', moC_zhuan_sheng),
]:
    sub = [s for s in samples if fn(s)]
    tot = len(sub)
    if tot == 0:
        print(f"{name:<24}{0:>9}"); continue
    brk = sum(1 for s in sub if s[5]<0)
    hit = sum(1 for s in sub if s[4]>3)
    print(f"{name:<24}{tot:>9}{brk:>8}{brk/tot*100:>7.2f}%{hit:>8}{hit/tot*100:>7.2f}%")
