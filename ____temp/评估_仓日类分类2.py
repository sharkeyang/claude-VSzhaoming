# -*- coding: utf-8 -*-
"""补充评估：非金+多持的细分，确认提议方式在非金范围也有效
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
SAMPLE = 100

COL_ZHOUHR = 74
COL_SHIXING = 84
COL_DXCD = 8
COL_DXAB = 9
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

def calc_huduan(dxab):
    return dxab[0] if dxab else '?'

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
    print(f'抽样文件数: {len(by_fid)}', flush=True)

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
            dxab = row[COL_DXAB]
            shixing = row[COL_SHIXING]
            op = calc_operation(rize, rizc, dtzd, dtcd)
            huduan = calc_huduan(dxab)
            recs.append((op, dxcd, huduan, shixing, next_hr))
    print(f'有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = 0
        for op, dxcd, huduan, shixing, next_hr in recs:
            if cond(op, dxcd, huduan, shixing):
                n += 1
                if next_hr >= 3: hr3 += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | 下周周HR>=3% {hr3/n*100:.1f}%', flush=True)

    def shixing_jin(shixing): return shixing and len(shixing) >= 2 and shixing[1] == '金'

    print('\n===== 非金+多持 的细分 =====', flush=True)
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd=='上', '非金+多持+护级上')
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd=='忐', '非金+多持+护级忐')
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd not in ('上','忐'), '非金+多持+护级其他')

    print('\n===== 非金+多持+上，再按护段 =====', flush=True)
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd=='上' and hd in ('a','b'), '非金+多持+上+正交(a,b)')
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd=='上' and hd in ('r','c'), '非金+多持+上+过渡(r,c)')
    stats(lambda op,dxcd,hd,sx: not shixing_jin(sx) and op=='多持' and dxcd=='上' and hd in ('y','z'), '非金+多持+上+负交(y,z)')

    print('\n===== 金+多持 的细分（对比）=====', flush=True)
    stats(lambda op,dxcd,hd,sx: shixing_jin(sx) and op=='多持' and dxcd=='上', '金+多持+护级上')
    stats(lambda op,dxcd,hd,sx: shixing_jin(sx) and op=='多持' and dxcd=='忐', '金+多持+护级忐')

    print('\n===== 非金各势型 + 多持 =====', flush=True)
    for s in ['银','唏','嘘','屎','尿']:
        stats(lambda op,dxcd,hd,sx,s=s: sx and len(sx)>=2 and sx[1]==s and op=='多持', f'{s}+多持')

if __name__ == '__main__':
    main()
