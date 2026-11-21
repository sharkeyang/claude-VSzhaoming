# -*- coding: utf-8 -*-
"""验证D3节按日综新分类逻辑：先按操作，多持再按护级细分，确认未知=0
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
SAMPLE = 50

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

    counts = defaultdict(int)
    total = 0
    for fid, rlist in by_fid.items():
        for row in rlist:
            rize = to_float(row[COL_RIZE])
            rizc = to_float(row[COL_RIZC])
            dtzd = to_float(row[COL_DTZD])
            dtcd = to_float(row[COL_DTCD])
            dxcd = row[COL_DXCD]
            dxab = row[COL_DXAB]
            op = calc_operation(rize, rizc, dtzd, dtcd)
            huduan = dxab[0] if dxab else '?'
            # 按新分类逻辑
            if op == '多持':
                if dxcd == '上':
                    if huduan in ('c','y','z'): counts['多持_上_cyz'] += 1
                    elif huduan in ('a','b'): counts['多持_上_ab'] += 1
                    elif huduan == 'r': counts['多持_上_r'] += 1
                    else: counts['多持_上_其他护段'] += 1
                elif dxcd == '忐': counts['多持_忐'] += 1
                else: counts['多持_其他'] += 1
            elif op == '多截': counts['多截'] += 1
            elif op == '空截': counts['空截'] += 1
            elif op == '空持': counts['空持'] += 1
            else: counts['未知'] += 1
            total += 1
    print(f'总行数: {total}', flush=True)
    print('\n===== D3节新分类逻辑各字典样本分布 =====', flush=True)
    for k in ['多持_上_cyz','多持_上_ab','多持_上_r','多持_上_其他护段','多持_忐','多持_其他','多截','空截','空持','未知']:
        print(f'{k}: {counts[k]:,} ({counts[k]/total*100:.1f}%)', flush=True)
    print(f'\n未知分类: {counts["未知"]} (应为0)', flush=True)

if __name__ == '__main__':
    main()
