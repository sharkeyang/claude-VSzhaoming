# -*- coding: utf-8 -*-
"""评估筛选分类方式：先周层势型 vs 先仓日类操作（抽样300文件）
数据：谕组日 CSV（GBK），列索引见元数据_vba数据映射_日类.md
"""
import csv, glob, os, sys
from collections import defaultdict

DATA_DIR = '昭明算展/谕组日'
SAMPLE = 100  # 抽样文件数

COL_ZHOUHR = 74      # 周HR
COL_SHIXING = 84     # 周势型(金银唏嘘屎尿)
COL_DXCD = 8         # DXCD护级
COL_DXAB = 9         # DXAB护型
COL_RIZC = 17        # 日ZC
COL_RIZE = 18        # 日ZE
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
            situ = calc_situ(rize, dxcd)
            huduan = calc_huduan(dxab)
            recs.append((op, situ, dxcd, huduan, shixing, next_hr))
    print(f'有效行数: {len(recs)}', flush=True)

    def stats(cond, label):
        n = hr3 = 0
        for op, situ, dxcd, huduan, shixing, next_hr in recs:
            if cond(op, situ, dxcd, huduan, shixing):
                n += 1
                if next_hr >= 3: hr3 += 1
        if n == 0:
            print(f'{label}: n=0', flush=True); return
        print(f'{label}: n={n:,} | 下周周HR>=3% {hr3/n*100:.1f}%', flush=True)

    def shixing_jin(shixing): return shixing and len(shixing) >= 2 and shixing[1] == '金'

    print('\n===== 当前方式：先周层势型金，再仓日类护级 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='上', '金+护级上')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='忐', '金+护级忐')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='忠', '金+护级忠')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='中', '金+护级中')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='下', '金+护级下')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='忑', '金+护级忑')

    print('\n===== 当前方式：金+护级上，再按护段 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='上' and hd in ('a','b'), '金+上+护段正交(a,b)')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='上' and hd in ('r','c'), '金+上+护段过渡(r,c)')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and dxcd=='上' and hd in ('y','z'), '金+上+护段负交(y,z)')

    print('\n===== 提议方式：先仓日类操作 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: op=='多持', '多持')
    stats(lambda op,situ,dxcd,hd,sx: op=='多截', '多截')
    stats(lambda op,situ,dxcd,hd,sx: op=='空持', '空持')
    stats(lambda op,situ,dxcd,hd,sx: op=='空截', '空截')

    print('\n===== 提议方式：多持，再按护级 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd=='上', '多持+护级上')
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd=='忐', '多持+护级忐')
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd not in ('上','忐'), '多持+护级其他')

    print('\n===== 提议方式：多持+上，再按护段 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd=='上' and hd in ('a','b'), '多持+上+护段正交(a,b)')
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd=='上' and hd in ('r','c'), '多持+上+护段过渡(r,c)')
    stats(lambda op,situ,dxcd,hd,sx: op=='多持' and dxcd=='上' and hd in ('y','z'), '多持+上+护段负交(y,z)')

    print('\n===== 交叉：周层势型金 vs 仓日类多持 =====', flush=True)
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and op=='多持', '金+多持')
    stats(lambda op,situ,dxcd,hd,sx: shixing_jin(sx) and op!='多持', '金+非多持')
    stats(lambda op,situ,dxcd,hd,sx: not shixing_jin(sx) and op=='多持', '非金+多持')

if __name__ == '__main__':
    main()
