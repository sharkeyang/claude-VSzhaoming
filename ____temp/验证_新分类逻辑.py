# -*- coding: utf-8 -*-
"""验证新分类逻辑：先按仓日类操作分类，多持再按护级/护段细分
用谕组日底层数据重新计算新格式仓日类，按新分类逻辑分类，确认各字典分布
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

def calc_situ(rize, dxcd):
    if rize is None or dxcd is None: return '?'
    if rize < 0 and dxcd in ('下','忑'): return '禁'
    if dxcd in ('中','下','忑'): return '念'
    if rize > 0 and dxcd in ('上','忐'): return '沃'
    return '肋'

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

    # 统计各分类的样本数
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
            situ = calc_situ(rize, dxcd)
            huduan = calc_huduan(dxab)
            # 新格式仓日类 = 操作+四土+护级+护段
            crl = op + situ + dxcd + huduan
            # 按新分类逻辑分类
            if op == '多持':
                if dxcd == '上':
                    if huduan in ('a','b'): counts['多持_上_正交'] += 1
                    elif huduan in ('r','c'): counts['多持_上_过渡'] += 1
                    elif huduan in ('y','z'): counts['多持_上_负交'] += 1
                    else: counts['多持_上_其他护段'] += 1
                elif dxcd == '忐': counts['多持_忐'] += 1
                else: counts['多持_其他'] += 1
            elif op == '多截': counts['多截'] += 1
            elif op == '空持': counts['空持'] += 1
            elif op == '空截': counts['空截'] += 1
            else: counts['未知'] += 1
            total += 1
    print(f'总行数: {total}', flush=True)
    print('\n===== 新分类逻辑各字典样本分布 =====', flush=True)
    for k in ['多持_上_正交','多持_上_过渡','多持_上_负交','多持_上_其他护段','多持_忐','多持_其他','多截','空持','空截','未知']:
        print(f'{k}: {counts[k]:,} ({counts[k]/total*100:.1f}%)', flush=True)

    # 验证：所有行都能被分类（未知=0）
    print(f'\n未知分类: {counts["未知"]} (应为0)', flush=True)

if __name__ == '__main__':
    main()
