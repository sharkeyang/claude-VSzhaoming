# -*- coding: utf-8 -*-
"""
镜面映射：WXZB<0 持续期内最终转负概率（用户新定义，高效版）
定义：从当前 WXZC>0 且 WXZB<0 起点，逐周跟踪，只要 WXZB 仍<0 就继续；
一旦 WXZB>0 停止（不计转负）；一旦 WXZC<0 记为转负。
用 next-occurrence 数组，每个起点 O(1)。
"""
import glob, pandas as pd, io, sys, numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for i,f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2:
            df['fid']=i
            dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
wk['WXZB'] = pd.to_numeric(wk['ZB周'], errors='coerce')
wk['WXAB'] = pd.to_numeric(wk['AB周'], errors='coerce')
wk['WXZA'] = pd.to_numeric(wk['ZA周'], errors='coerce')
print(f'总样本: {len(wk):,}')
print()

def 持续转负(wk, 起点条件):
    """统计起点在WXZB持续<0期间内最终转负的比例"""
    转负 = 0
    未转负 = 0
    for fid, df in wk.groupby('fid', sort=False):
        zc = df['WXZC'].values
        zb = df['WXZB'].values
        n = len(df)
        # next occurrence：i之后第一个zc<0 / zb>0
        next_neg = np.full(n, -1)
        next_pos = np.full(n, -1)
        last_neg = -1
        last_pos = -1
        for i in range(n-1, -1, -1):
            next_neg[i] = last_neg
            next_pos[i] = last_pos
            if zc[i] < 0:
                last_neg = i
            if zb[i] > 0:
                last_pos = i
        starts = np.where(起点条件(df))[0]
        for i in starts:
            nn = next_neg[i]
            np_ = next_pos[i]
            if nn == -1:
                未转负 += 1
            elif np_ == -1:
                转负 += 1
            else:
                if nn < np_:
                    转负 += 1
                else:
                    未转负 += 1
    return 转负, 未转负

def 持续转正(wk, 起点条件):
    """统计起点在WXZB持续>0期间内最终转正的比例（镜像）"""
    转正 = 0
    未转正 = 0
    for fid, df in wk.groupby('fid', sort=False):
        zc = df['WXZC'].values
        zb = df['WXZB'].values
        n = len(df)
        next_pos = np.full(n, -1)
        next_neg = np.full(n, -1)
        last_pos = -1
        last_neg = -1
        for i in range(n-1, -1, -1):
            next_pos[i] = last_pos
            next_neg[i] = last_neg
            if zc[i] > 0:
                last_pos = i
            if zb[i] < 0:
                last_neg = i
        starts = np.where(起点条件(df))[0]
        for i in starts:
            np_ = next_pos[i]
            nn = next_neg[i]
            if np_ == -1:
                未转正 += 1
            elif nn == -1:
                转正 += 1
            else:
                if np_ < nn:
                    转正 += 1
                else:
                    未转正 += 1
    return 转正, 未转正

def 报告(name, 起点条件, 方向):
    if 方向 == '负':
        转, 未 = 持续转负(wk, 起点条件)
    else:
        转, 未 = 持续转正(wk, 起点条件)
    total = 转 + 未
    if total < 100:
        print(f'  {name}: n={total} 样本不足')
        return
    print(f'  {name}: n={total:,}  持续期内最终转{方向}率={转/total*100:.1f}%')
    print()

print('='*90)
print('猜想2：WXZC>0 + WXZB<0 前提下，WXAB<0 是否提高持续期内最终转负率？')
print('='*90)
报告('WXZC>0+WXZB<0+WXAB<0', lambda df: (df['WXZC']>0)&(df['WXZB']<0)&(df['WXAB']<0), '负')
报告('WXZC>0+WXZB<0+WXAB>0', lambda df: (df['WXZC']>0)&(df['WXZB']<0)&(df['WXAB']>0), '负')
报告('WXZC>0+WXZB<0(全)', lambda df: (df['WXZC']>0)&(df['WXZB']<0), '负')
print()

print('='*90)
print('对照：WXZC>0 + WXZA<0 前提下，WXAB<0 是否提高持续期内最终转负率？')
print('='*90)
报告('WXZC>0+WXZA<0+WXAB<0', lambda df: (df['WXZC']>0)&(df['WXZA']<0)&(df['WXAB']<0), '负')
报告('WXZC>0+WXZA<0+WXAB>0', lambda df: (df['WXZC']>0)&(df['WXZA']<0)&(df['WXAB']>0), '负')
print()

print('='*90)
print('猜想1镜像：WXZC<0 + WXZB>0 前提下，WXAB>0 是否提高持续期内最终转正率？')
print('='*90)
报告('WXZC<0+WXZB>0+WXAB>0', lambda df: (df['WXZC']<0)&(df['WXZB']>0)&(df['WXAB']>0), '正')
报告('WXZC<0+WXZB>0+WXAB<0', lambda df: (df['WXZC']<0)&(df['WXZB']>0)&(df['WXAB']<0), '正')
报告('WXZC<0+WXZB>0(全)', lambda df: (df['WXZC']<0)&(df['WXZB']>0), '正')
