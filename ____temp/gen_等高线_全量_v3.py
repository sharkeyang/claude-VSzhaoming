# -*- coding: utf-8 -*-
"""
等高线全量验证 v2 — 阈值4→3（与柱型对齐）
分类逻辑：VBA末位（DTZA + 中符串末位）
等2: DTZA=2~3+CDEF, 等4: DTZA>3+CDEF, 等6: DTZA=-3~-2+ABCD, 等8: DTZA<-3+ABCD
增量聚合，内存友好
"""
import pandas as pd, numpy as np, os, glob, time, random, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
OUT_MD  = r'D:\@VSwork\VS昭明计划VBA优化\____temp\等高线_全量_v3.md'

USE_COLS = ['日ZA','中符串','涨幅','高幅','次日高幅','日ZC','日ZE','DXCD','DXEF','DXAB','顶型','波型','上符串','柱型','柱排','层界']
CATS = ['等1','等2','等3','等4','等5','等6','等7','等8']

def classify_vect(za, mid):
    last = mid.astype(str).str[-1]
    dg = pd.Series(None, index=za.index, dtype='object')
    dg[za == 1] = '等1'
    m = (za > 0)
    dg[m & (za > 3)  & last.isin(['C','D','E','F'])] = '等4'
    dg[m & (za >= 2) & (za <= 3) & last.isin(['C','D','E','F'])] = '等2'
    dg[m & (za >= 2) & last.isin(['A','B'])]          = '等3'
    dg[za == -1] = '等5'
    n = (za < 0) & (za != -1)
    dg[n & (za < -3)  & last.isin(['A','B','C','D'])] = '等8'
    dg[n & (za >= -3) & (za <= -2) & last.isin(['A','B','C','D'])] = '等6'
    dg[n & (za <= -2) & last.isin(['E','F'])]          = '等7'
    return dg

def main():
    t0 = time.time(); random.seed(42)
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}')

    valid = []
    for f in files:
        try:
            with open(f, 'rb') as fh:
                fh.readline(); n = sum(1 for _ in fh)
                if n >= 200: valid.append(f)
        except: pass
    print(f'合格(>=200行): {len(valid)}')

    class Agg:
        def __init__(self):
            self.stats = {c: {
                'n':0, 'nh_sum':0.0, 'nh0':0,'nh1':0,'nh3':0,'nh5':0,
                'ze_n':0,'ze3':0,'ze5':0,'noze_n':0,'noze5':0,
                'open_n':0,'open_ze':0,'closed_n':0,'closed_ze':0,
                'hold7':[0,0,0], 'hold20':[0,0,0], 'hold7_5':0,'hold7_10':0,'hold20_5':0,'hold20_10':0,
                'pr_n':0,'up_n':0,'up_sum':0.0,'down_n':0,'down_sum':0.0,
                'wave':{},
                'nextza_pos':0,'nextza_neg':0,'nextza_zero':0,'nextza_n':0,
                'top':{'龙':[0,0],'非龙':[0,0]},  # [n, ze>0]
                'top_open':{'龙':[0,0],'非龙':[0,0]},  # 门开下
                'top_closed':{'龙':[0,0],'非龙':[0,0]},  # 门关下
                'hx':{h:[0,0] for h in '甲乙丙丁戊己'},  # 护型 [n, nh>3]
                'hx_open':{h:[0,0] for h in '甲乙丙丁戊己'}  # 护型+门开
            } for c in CATS}
    agg = Agg()

    for i, f in enumerate(valid):
        try:
            df = pd.read_csv(f, encoding='gbk', usecols=USE_COLS)
        except: continue
        if len(df) < 200: continue
        df['等高线'] = classify_vect(df['日ZA'].astype(float), df['中符串']).fillna('NA')
        df['next_pr'] = df['涨幅'].shift(-1)
        df['next_za'] = df['日ZA'].shift(-1)
        rev = df['涨幅'].iloc[::-1]
        df['fwd7'] = rev.rolling(7).sum().iloc[::-1]
        df['fwd20'] = rev.rolling(20).sum().iloc[::-1]
        for c in CATS:
            sub = df[df['等高线']==c]
            if len(sub)==0: continue
            s = agg.stats[c]
            nh = sub['次日高幅']
            s['n'] += len(nh); s['nh_sum'] += float(nh.sum())
            s['nh0'] += int((nh>0).sum()); s['nh1'] += int((nh>1).sum())
            s['nh3'] += int((nh>3).sum()); s['nh5'] += int((nh>5).sum())
            ze = sub[sub['日ZE']>0]; noze = sub[sub['日ZE']<=0]
            s['ze_n'] += len(ze); s['ze3'] += int((ze['次日高幅']>3).sum()); s['ze5'] += int((ze['次日高幅']>5).sum())
            s['noze_n'] += len(noze); s['noze5'] += int((noze['次日高幅']>5).sum())
            op = sub[(sub['日ZC']>0) & (sub['DXCD'].astype(str)=='上')]
            s['open_n'] += len(op); s['open_ze'] += int((op['日ZE']>0).sum())
            cl = sub[~((sub['日ZC']>0) & (sub['DXCD'].astype(str)=='上'))]
            s['closed_n'] += len(cl); s['closed_ze'] += int((cl['日ZE']>0).sum())
            # 顶型（龙 vs 非龙）— 向量化
            top_is_long = sub['顶型'].astype(str).str.contains('龙', na=False)
            top_ze = sub['日ZE'] > 0
            s['top']['龙'][0] += int(top_is_long.sum())
            s['top']['龙'][1] += int((top_is_long & top_ze).sum())
            s['top']['非龙'][0] += int((~top_is_long).sum())
            s['top']['非龙'][1] += int(((~top_is_long) & top_ze).sum())
            # 门约束下的顶型
            is_open = (sub['日ZC'] > 0) & (sub['DXCD'].astype(str) == '上')
            open_long = top_is_long & is_open
            open_non = (~top_is_long) & is_open
            closed_long = top_is_long & ~is_open
            closed_non = (~top_is_long) & ~is_open
            s['top_open']['龙'][0] += int(open_long.sum())
            s['top_open']['龙'][1] += int((open_long & top_ze).sum())
            s['top_open']['非龙'][0] += int(open_non.sum())
            s['top_open']['非龙'][1] += int((open_non & top_ze).sum())
            s['top_closed']['龙'][0] += int(closed_long.sum())
            s['top_closed']['龙'][1] += int((closed_long & top_ze).sum())
            s['top_closed']['非龙'][0] += int(closed_non.sum())
            s['top_closed']['非龙'][1] += int((closed_non & top_ze).sum())
            # 护型（甲乙丙丁戊己）
            sub['护型'] = sub['DXAB'].astype(str).str[1]
            for h in '甲乙丙丁戊己':
                hm = (sub['护型']==h)
                s['hx'][h][0] += int(hm.sum())
                s['hx'][h][1] += int((hm & (sub['次日高幅']>3)).sum())
                is_open = (sub['日ZC']>0) & (sub['DXCD'].astype(str)=='上')
                hx_open = hm & is_open
                s['hx_open'][h][0] += int(hx_open.sum())
                s['hx_open'][h][1] += int((hx_open & (sub['次日高幅']>3)).sum())
            h7 = sub['fwd7'].dropna()
            if len(h7)>0: s['hold7'][0] += len(h7); s['hold7_5'] += int((h7>5).sum()); s['hold7_10'] += int((h7>10).sum())
            h20 = sub['fwd20'].dropna()
            if len(h20)>0: s['hold20'][0] += len(h20); s['hold20_5'] += int((h20>5).sum()); s['hold20_10'] += int((h20>10).sum())
            npr = sub['next_pr'].dropna()
            up = npr[npr>0]; down = npr[npr<0]
            s['pr_n'] += len(npr); s['up_n'] += len(up); s['up_sum'] += float(up.sum())
            s['down_n'] += len(down); s['down_sum'] += float(down.sum())
            for w in sub['波型'].astype(str).unique():
                s['wave'][w] = s['wave'].get(w, 0) + int((sub['波型'].astype(str)==w).sum())
            next_za = sub['next_za'].dropna()
            if len(next_za)>0:
                s['nextza_n'] += len(next_za)
                s['nextza_pos'] += int((next_za>0).sum())
                s['nextza_neg'] += int((next_za<0).sum())
                s['nextza_zero'] += int((next_za==0).sum())
        if (i+1)%1000==0: print(f'  {i+1}/{len(valid)} {time.time()-t0:.0f}s')
    print(f'完成: {len(valid)}文件, 耗时{time.time()-t0:.0f}s')

    n_all = sum(agg.stats[c]['n'] for c in CATS)
    L = []
    L.append('# 等高线全量验证 v3（阈值4→3，与柱型对齐）')
    L.append(f'**样本**: {n_all:,} 行, 耗时 {time.time()-t0:.0f}s')
    L.append('')
    L.append('## 一、分类分布')
    L.append('| 分类 | 样本 | 占比 |')
    L.append('|:----|-----:|-----:|')
    for c in CATS:
        L.append(f'| {c} | {agg.stats[c]["n"]:,} | {agg.stats[c]["n"]/n_all:.1%} |')
    L.append('')
    L.append('## 二、下日冲高概率')
    L.append('| 分类 | 样本 | 占比 | 平均冲高 | ≥0% | ≥1% | ≥3% | ≥5% |')
    L.append('|:----|-----:|:---:|:-------:|:---:|:---:|:---:|:---:|')
    for c in CATS:
        s = agg.stats[c]
        if s['n']==0: continue
        L.append(f'| {c} | {s["n"]:,} | {s["n"]/n_all:.1%} | {s["nh_sum"]/s["n"]:.2f}% | {s["nh0"]/s["n"]:.1%} | {s["nh1"]/s["n"]:.1%} | {s["nh3"]/s["n"]:.1%} | {s["nh5"]/s["n"]:.1%} |')
    L.append('')
    L.append('## 三、等高线 × 日ZE')
    L.append('| 分类 | ZE>0样本 | 冲≥3% | 冲≥5% | ZE≤0冲≥5% |')
    L.append('|:----|--------:|:----:|:----:|:--------:|')
    for c in CATS:
        s = agg.stats[c]
        if s['ze_n']==0: continue
        L.append(f'| {c} | {s["ze_n"]:,} | {s["ze3"]/s["ze_n"]:.1%} | {s["ze5"]/s["ze_n"]:.1%} | {s["noze5"]/max(1,s["noze_n"]):.1%} |')
    L.append('')
    L.append('## 四、门验证（ZC>0 ∩ DXCD=上 →ZE>0）')
    L.append('| 分类 | 门开n | 门开→ZE>0 | 门关n | 门关→ZE>0 |')
    L.append('|:----|------:|:--------:|------:|:--------:|')
    for c in CATS:
        s = agg.stats[c]
        if s['open_n']==0 and s['closed_n']==0: continue
        ov = '-' if s['open_n']==0 else f'{s["open_ze"]/s["open_n"]:.1%}'
        cv = '-' if s['closed_n']==0 else f'{s["closed_ze"]/s["closed_n"]:.1%}'
        L.append(f'| {c} | {s["open_n"]:,} | {ov} | {s["closed_n"]:,} | {cv} |')
    L.append('')
    L.append('## 五、等高线 × 顶型（→ZE>0）')
    L.append('| 分类 | 龙n | 龙→ZE>0 | 非龙n | 非龙→ZE>0 | 差距 |')
    L.append('|:----|----:|:------:|----:|:--------:|:----:|')
    for c in CATS:
        s = agg.stats[c]
        rn, rz = s['top']['龙']; fn, fz = s['top']['非龙']
        if rn+fn==0: continue
        L.append(f'| {c} | {rn:,} | {rz/rn:.1%} | {fn:,} | {fz/fn:.1%} | {rz/rn-fz/fn:.1%} |')
    L.append('')
    L.append('## 六、等高线 × 顶型 × 门（门开下→ZE>0）')
    L.append('| 分类 | 龙n(开) | 龙→ZE>0(开) | 非龙n(开) | 非龙→ZE>0(开) | 差距(开) |')
    L.append('|:----|--------:|:----------:|--------:|:----------:|:--------:|')
    for c in CATS:
        s = agg.stats[c]
        rn, rz = s['top_open']['龙']; fn, fz = s['top_open']['非龙']
        if rn+fn==0: continue
        L.append(f'| {c} | {rn:,} | {rz/rn:.1%} | {fn:,} | {fz/fn:.1%} | {rz/rn-fz/fn:.1%} |')
    L.append('')
    L.append('## 七、等高线 × 顶型 × 门（门关下→ZE>0）')
    L.append('| 分类 | 龙n(关) | 龙→ZE>0(关) | 非龙n(关) | 非龙→ZE>0(关) | 差距(关) |')
    L.append('|:----|--------:|:----------:|--------:|:----------:|:--------:|')
    for c in CATS:
        s = agg.stats[c]
        rn, rz = s['top_closed']['龙']; fn, fz = s['top_closed']['非龙']
        if rn+fn==0: continue
        L.append(f'| {c} | {rn:,} | {rz/rn:.1%} | {fn:,} | {fz/fn:.1%} | {rz/rn-fz/fn:.1%} |')
    L.append('')
    L.append('## 八、等高线 × 护型（DXAB）下日冲高≥3%')
    L.append('| 分类 | 样本 | 甲 | 乙 | 丙 | 丁 | 戊 | 己 |')
    L.append('|:----|-----:|:--:|:--:|:--:|:--:|:--:|:--:|')
    HXS = '甲乙丙丁戊己'
    for c in CATS:
        s = agg.stats[c]
        tot = sum(s['hx'][h][0] for h in HXS)
        if tot==0: continue
        row = f'| {c} | {tot:,} | '
        for h in HXS:
            n, h3 = s['hx'][h]
            row += f'{h3/max(1,n):.1%} | ' if n>=50 else '- | '
        L.append(row)
    L.append('')
    L.append('## 九、等高线 × 护型 × 门（门开下日冲高≥3%）')
    L.append('| 分类 | 门开n | 甲 | 乙 | 丙 | 丁 | 戊 | 己 |')
    L.append('|:----|-----:|:--:|:--:|:--:|:--:|:--:|:--:|')
    for c in CATS:
        s = agg.stats[c]
        tot = sum(s['hx_open'][h][0] for h in HXS)
        if tot==0: continue
        row = f'| {c} | {tot:,} | '
        for h in HXS:
            n, h3 = s['hx_open'][h]
            row += f'{h3/max(1,n):.1%} | ' if n>=20 else '- | '
        L.append(row)
    L.append('')
    L.append('## 十、持有期')
    L.append('| 分类 | 持7天≥5% | 持7天≥10% | 持20天≥5% | 持20天≥10% |')
    L.append('|:----|:--------:|:---------:|:---------:|:----------:|')
    for c in CATS:
        s = agg.stats[c]
        if s['n']==0: continue
        L.append(f'| {c} | {s["hold7_5"]/max(1,s["hold7"][0]):.1%} | {s["hold7_10"]/max(1,s["hold7"][0]):.1%} | {s["hold20_5"]/max(1,s["hold20"][0]):.1%} | {s["hold20_10"]/max(1,s["hold20"][0]):.1%} |')
    L.append('')
    L.append('## 十一、涨跌结构（下一柱涨幅）')
    L.append('| 分类 | 样本 | 下一柱涨天数比 | 下一柱涨均幅 | 下一柱跌均幅 | 幅度比 | 期望收益/天 |')
    L.append('|:----|-----:|:----------:|:---------:|:---------:|:-----:|:--------:|')
    for c in CATS:
        s = agg.stats[c]
        if s['pr_n']==0: continue
        ur = s['up_n']/s['pr_n']; um = s['up_sum']/s['up_n'] if s['up_n'] else 0
        dm = abs(s['down_sum']/s['down_n']) if s['down_n'] else 0
        amp = um/dm if dm else 0
        L.append(f'| {c} | {s["pr_n"]:,} | {ur:.1%} | {um:.2f}% | {dm:.2f}% | {amp:.2f} | {ur*um-(1-ur)*dm:.3f}% |')
    L.append('')
    L.append('## 十二、下一柱DTZA方向（回归确认）')
    L.append('| 分类 | 样本 | 下一柱DTZA>0(继续走) | 下一柱DTZA=0(回归) | 下一柱DTZA<0(反转) |')
    L.append('|:----|-----:|:-------------------:|:-----------------:|:-----------------:|')
    for c in CATS:
        s = agg.stats[c]
        if s['nextza_n']==0: continue
        L.append(f'| {c} | {s["nextza_n"]:,} | {s["nextza_pos"]/s["nextza_n"]:.1%} | {s["nextza_zero"]/s["nextza_n"]:.1%} | {s["nextza_neg"]/s["nextza_n"]:.1%} |')
    L.append('')
    with open(OUT_MD, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))
    print(f'输出: {OUT_MD}')

if __name__=='__main__': main()