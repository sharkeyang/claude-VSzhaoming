# -*- coding: utf-8 -*-
"""
赛马不可靠策略放宽条件测试：等8/等6/等5
逐步放宽 BSHA阈值/连阳/周门，看样本量是否充足且≥2%是否达标
"""
import numpy as np, pandas as pd, os, glob, time, warnings, math
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800
np.random.seed(42)

def classify_8(za, last):
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); lc = str(last) if pd.notna(last) else ''
    ab = lc in 'AB'; cdef = lc in 'CDEF'
    abcd = lc in 'ABCD'; ef = lc in 'EF'
    if za > 0:
        if za == 1: return '等1'
        elif za >= 2 and ab: return '等3'
        elif za >= 2 and cdef and za <= 3: return '等2'
        elif za > 3 and cdef: return '等4'
    elif za < 0:
        if za == -1: return '等5'
        elif za >= -3 and za <= -2 and abcd: return '等6'
        elif za <= -2 and ef: return '等7'
        elif za < -3 and abcd: return '等8'
    return 'NA'

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    rows = []
    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','高幅','日ZC','DXCD','DXAB'])
        except: continue
        if len(df) < 100: continue
        za = df['日ZA'].astype(float)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        high = df['高幅'].astype(float)
        zc = df['日ZC'].astype(float)
        dxab = df['DXAB'].astype(str)
        dxcd = df['DXCD'].astype(str)

        for idx in df.index:
            zval = za[idx]; nhv = nh[idx]; lc = last[idx]; hv = high[idx]
            zc_p = (zc[idx] > 0)
            dxcd_up = (dxcd[idx] == '上')
            ab_type = str(dxab[idx])[1] if len(str(dxab[idx]))>1 else ''
            operable = zc_p or (not zc_p and ab_type in '甲乙己')

            c8 = classify_8(zval, lc)
            if c8 not in ['等5','等6','等8']: continue

            rows.append({
                'deng': c8, 'nh': nhv if pd.notna(nhv) else 0, 'nhv': int(pd.notna(nhv)),
                'nh2': int(pd.notna(nhv) and nhv>2),
                'nh3': int(pd.notna(nhv) and nhv>3),
                'bsha5': int(pd.notna(hv) and hv>5),
                'bsha4': int(pd.notna(hv) and hv>4),
                'bsha3': int(pd.notna(hv) and hv>3),
                'bsha2': int(pd.notna(hv) and hv>2),
                'zhoumen': int(zc_p and dxcd_up),
                'operable': int(operable),
            })
        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'数据收集完成: {len(rows):,} 行, 耗时 {time.time()-t0:.0f}s', flush=True)
    df = pd.DataFrame(rows)

    def ci(n, p):
        se = math.sqrt(p*(1-p)/n) if n>0 else 0
        return (p-1.96*se, p+1.96*se)

    for deng in ['等5','等6','等8']:
        sub = df[df['deng']==deng]
        if len(sub)==0: continue
        print('\n' + '='*90)
        print(f'【{deng}】放宽条件测试 — 从最严到最宽')
        print(f'总样本: {len(sub):,}')
        print('='*90)
        print(f'{"条件":<38} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"95%置信区间":<18} {"判断"}')
        print('-'*95)

        # 条件组合：从严到宽
        combos = [
            (f'{deng}+BSHA5+连阳+周门', 'bsha5', 'zhoumen'),
            (f'{deng}+BSHA5+周门', 'bsha5', 'zhoumen'),
            (f'{deng}+BSHA5+连阳', 'bsha5', None),
            (f'{deng}+BSHA5', 'bsha5', None),
            (f'{deng}+BSHA4+周门', 'bsha4', 'zhoumen'),
            (f'{deng}+BSHA4', 'bsha4', None),
            (f'{deng}+BSHA3+周门', 'bsha3', 'zhoumen'),
            (f'{deng}+BSHA3', 'bsha3', None),
            (f'{deng}+BSHA2+周门', 'bsha2', 'zhoumen'),
            (f'{deng}+BSHA2', 'bsha2', None),
            (f'{deng}+操作区域', 'operable', None),
        ]
        seen = set()
        for name, c1, c2 in combos:
            m = sub[sub[c1]==1]
            if c2: m = m[m[c2]==1]
            if len(m) < 30: continue
            n = len(m)
            n2 = m['nh2'].sum()/n
            n3 = m['nh3'].sum()/n
            lo, hi = ci(n, n2)
            if n < 100:
                judge = '样本小'
            elif n < 1000:
                judge = '参考'
            elif n < 10000:
                judge = '可用'
            else:
                judge = '稳定'
            key = (c1, c2)
            if key in seen: continue
            seen.add(key)
            print(f'{name:<38} {n:>8,} {n2:>7.1%} {n3:>7.1%} [{lo:>5.1%}~{hi:>5.1%}] {judge}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()