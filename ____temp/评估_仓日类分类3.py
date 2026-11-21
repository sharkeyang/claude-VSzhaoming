# -*- coding: utf-8 -*-
"""评估：周层势型在提议方式下的辅助价值（多持内，金 vs 非金）
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
SAMPLE = 100

COL_ZHOUHR = 74
COL_SHIXING = 84
COL_DXCD = 8
COL_RIZC = 17
COL_RIZE = 18
COL_DTZD = 69
COL_DTCD = 71

def to_float(s):
    try: return float(s)
    except: return None

def calc_operation(rize, rizc, dtzd, dtcd):
    if rize is None or rizc is None or dtzd is None or dtcd is None:
        return '?'
    if rize > 0:
        if dtzd > 0 and rizc > 0: return '多持'
        if dtzd < 0 and rizc < 0: return '多截'
        if dtcd > 0:
            return '多持' if abs(rizc) < abs(dtzd) else '多截'
        else:
            return '多持' if abs(dtzd) < abs(rizc) else '多截'
    else:
        if dtzd < 0 and rizc < 0: return '空持'
        if dtzd > 0 and rizc > 0: return '空截'
        if dtcd < 0:
            return '空截' if abs(dtzd) < abs(rizc) else '空持'
        else:
            return '空截' if abs(rizc) < abs(dtzd) else '空持'

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:SAMPLE]
    by_fid = defaultdict(list)
    for f in files:
        fid = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        with open(f, encoding='gbk') as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                if len(row) >= 135:
                    by_fid[fid].append(row)
    recs = []
    for fid, rlist in by_fid.items():
        for i, row in enumerate(rlist):
            next_hr = to_float(rlist[i+1][COL_ZHOUHR]) if i+1 < len(rlist) else None
            if next_hr is None: continue
            rize = to_float(row[COL_RIZE])
            rizc = to_float(row[COL_RIZC])
            dtzd = to_float(row[COL_DTZD])
            dtcd = to_float(row[COL_DTCD])
            dxcd = row[COL_DXCD]
            shixing = row[COL_SHIXING]
            op = calc_operation(rize, rizc, dtzd, dtcd)
            recs.append((op, dxcd, shixing, next_hr))
    print(f'有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = 0
        for op, dxcd, shixing, next_hr in recs:
            if cond(op, dxcd, shixing):
                n += 1
                if next_hr >= 3: hr3 += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | 下周周HR>=3% {hr3/n*100:.1f}%', flush=True)

    def shixing_jin(shixing): return shixing and len(shixing) >= 2 and shixing[1] == '金'

    print('\n===== 多持内：金 vs 非金（周层势型辅助价值）=====', flush=True)
    stats(lambda op,dxcd,sx: op=='多持' and shixing_jin(sx), '多持+金')
    stats(lambda op,dxcd,sx: op=='多持' and not shixing_jin(sx), '多持+非金')

    print('\n===== 多持+护级上：金 vs 非金 =====', flush=True)
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='上' and shixing_jin(sx), '多持+上+金')
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='上' and not shixing_jin(sx), '多持+上+非金')

    print('\n===== 多持+护级忐：金 vs 非金 =====', flush=True)
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='忐' and shixing_jin(sx), '多持+忐+金')
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='忐' and not shixing_jin(sx), '多持+忐+非金')

    print('\n===== 多持+上+正交：金 vs 非金 =====', flush=True)
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='上' and shixing_jin(sx), '多持+上+正交+金')
    stats(lambda op,dxcd,sx: op=='多持' and dxcd=='上' and not shixing_jin(sx), '多持+上+正交+非金')

if __name__ == '__main__':
    main()
