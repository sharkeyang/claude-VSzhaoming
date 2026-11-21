# -*- coding: utf-8 -*-
"""评估D3节按日综改造方案：先按操作（多截/空截/空持），多持再按护级（上/忐/其他）
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
SAMPLE = 100

COL_ZHOUHR = 74
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

def calc_situ(rize, dxcd):
    if rize is None or dxcd is None: return '?'
    if rize < 0 and dxcd in ('下','忑'): return '禁'
    if dxcd in ('中','下','忑'): return '念'
    if rize > 0 and dxcd in ('上','忐'): return '沃'
    return '肋'

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
            op = calc_operation(rize, rizc, dtzd, dtcd)
            situ = calc_situ(rize, dxcd)
            huduan = dxab[0] if dxab else '?'
            recs.append((op, situ, dxcd, huduan, next_hr))
    print(f'有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = 0
        for op, situ, dxcd, huduan, next_hr in recs:
            if cond(op, situ, dxcd, huduan):
                n += 1
                if next_hr >= 3: hr3 += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | 下周周HR>=3% {hr3/n*100:.1f}%', flush=True)

    print('\n===== 方案：先按操作分类 =====', flush=True)
    stats(lambda op,situ,dxcd,hd: op=='多截', '多截')
    stats(lambda op,situ,dxcd,hd: op=='空截', '空截')
    stats(lambda op,situ,dxcd,hd: op=='空持', '空持')

    print('\n===== 多持再按护级 =====', flush=True)
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='上', '多持+上')
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='忐', '多持+忐')
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd not in ('上','忐'), '多持+其他')

    print('\n===== 多持+上 内部（原逻辑）=====', flush=True)
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='上' and hd in ('c','y','z'), '多持+上+cyz')
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='上' and hd in ('a','b'), '多持+上+ab正交')
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='上' and hd in ('r',), '多持+上+r过渡')

    print('\n===== 多持+上+ab正交 再细分（脸哼JA）=====', flush=True)
    # 脸哼JA列=23，这里用护段近似
    stats(lambda op,situ,dxcd,hd: op=='多持' and dxcd=='上' and hd in ('a','b'), '多持+上+ab正交(全)')

if __name__ == '__main__':
    main()
