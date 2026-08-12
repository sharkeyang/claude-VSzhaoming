# -*- coding: utf-8 -*-
"""
等1与等5 各种过滤组合穷举 — 找最优≥2%提升
过滤维度：操作区域、前一柱护型、周门、BSHA5/3、连阳、柱梯
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 800
np.random.seed(42)

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    # 逐行收集数据，然后批量分析
    rows = []

    for i, f in enumerate(sampled):
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['日ZA','中符串','次日高幅','高幅','日ZC','DXCD','DXAB','柱型'])
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
        zhuxing = df['柱型'].astype(str)
        prev_dxab = dxab.shift(1)

        for idx in df.index:
            zval = za[idx]; nhv = nh[idx]; lc = last[idx]; hv = high[idx]
            zc_p = (zc[idx] > 0)
            dxcd_up = (dxcd[idx] == '上')
            dxcd_zhong = (dxcd[idx] == '中')
            dxcd_shang_tan = (dxcd[idx] in ['上','中','忐'])
            ab_type = str(dxab[idx])[1] if len(str(dxab[idx]))>1 else ''
            prev_ab = str(prev_dxab[idx])[1] if pd.notna(prev_dxab[idx]) and len(str(prev_dxab[idx]))>1 else ''
            zx = str(zhuxing[idx])

            # 只收集等1和等5
            lc_char = str(lc) if pd.notna(lc) else ''
            if pd.isna(zval) or zval == '': continue
            zval_f = float(zval)
            is_deng1 = (zval_f == 1)
            is_deng5 = (zval_f == -1)
            if not is_deng1 and not is_deng5: continue

            # 过滤条件（布尔值）
            operable = zc_p or (not zc_p and ab_type in '甲乙己')
            prev_ab_jiay = prev_ab in '甲乙'  # 甲乙
            prev_ab_yi = prev_ab == '乙'  # 仅乙
            prev_ab_jiayiji = prev_ab in '甲乙己'  # 甲乙己
            zhoumen = zc_p and dxcd_up
            zhoumen_kuan = zc_p and dxcd_shang_tan  # 宽周门
            zc_gt0 = zc_p
            zc_le0 = not zc_p
            bsha5 = pd.notna(hv) and hv > 5
            bsha3 = pd.notna(hv) and hv > 3
            bsha2 = pd.notna(hv) and hv > 2
            zhuti = '梯' in str(zx)

            # 方向（下柱ZA>0的概率）
            # 这里不计算方向，只计算冲高

            row = {
                'deng': '等1' if is_deng1 else '等5',
                'nh': nhv if pd.notna(nhv) else 0,
                'nh_valid': int(pd.notna(nhv)),
                'nh2': int(pd.notna(nhv) and nhv > 2) if pd.notna(nhv) else 0,
                'nh3': int(pd.notna(nhv) and nhv > 3) if pd.notna(nhv) else 0,
                'operable': int(operable),
                'prev_ab_jiay': int(prev_ab_jiay),
                'prev_ab_yi': int(prev_ab_yi),
                'prev_ab_jiayiji': int(prev_ab_jiayiji),
                'zhoumen': int(zhoumen),
                'zhoumen_kuan': int(zhoumen_kuan),
                'zc_gt0': int(zc_gt0),
                'zc_le0': int(zc_le0),
                'bsha5': int(bsha5),
                'bsha3': int(bsha3),
                'bsha2': int(bsha2),
                'zhuti': int(zhuti),
            }
            rows.append(row)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'数据收集完成: {len(rows):,} 行, 耗时 {time.time()-t0:.0f}s', flush=True)

    # 转为DataFrame分析
    df = pd.DataFrame(rows)

    # 定义过滤条件列表
    filters = {
        '操作区域': 'operable',
        '前一柱甲乙': 'prev_ab_jiay',
        '前一柱乙': 'prev_ab_yi',
        '前一柱甲乙己': 'prev_ab_jiayiji',
        '周门': 'zhoumen',
        '宽周门': 'zhoumen_kuan',
        'ZC>0': 'zc_gt0',
        'ZC≤0': 'zc_le0',
        'BSHA5': 'bsha5',
        'BSHA3': 'bsha3',
        'BSHA2': 'bsha2',
        '柱梯': 'zhuti',
    }

    for deng_name in ['等1', '等5']:
        sub = df[df['deng'] == deng_name]
        if len(sub) == 0: continue

        print(f'\n' + '='*90)
        print(f'【{deng_name}】过滤组合穷举 — 按≥2%排序')
        print(f'总样本: {len(sub):,}')
        print('='*90)

        # 单过滤
        results = []
        # 先加"无过滤"基准
        base_n = len(sub)
        base_nh2 = sub['nh2'].sum()
        base_nh3 = sub['nh3'].sum()
        base_sum = sub['nh'][sub['nh_valid']==1].sum()
        results.append({
            'name': '无过滤（基准）',
            'n': base_n, 'nh2_pct': base_nh2/base_n, 'nh3_pct': base_nh3/base_n,
            'avg': base_sum/base_nh2 if base_nh2 else 0
        })

        # 单过滤
        for fname, fcol in filters.items():
            m = sub[sub[fcol] == 1]
            if len(m) < 50: continue
            nh2 = m['nh2'].sum()
            nh3 = m['nh3'].sum()
            avg = m['nh'][m['nh_valid']==1].sum()/len(m)
            results.append({
                'name': fname,
                'n': len(m), 'nh2_pct': nh2/len(m), 'nh3_pct': nh3/len(m),
                'avg': avg
            })

        # 双过滤组合
        filter_items = list(filters.items())
        for i in range(len(filter_items)):
            for j in range(i+1, len(filter_items)):
                fn1, fc1 = filter_items[i]
                fn2, fc2 = filter_items[j]
                m = sub[(sub[fc1] == 1) & (sub[fc2] == 1)]
                if len(m) < 50: continue
                nh2 = m['nh2'].sum()
                nh3 = m['nh3'].sum()
                avg = m['nh'][m['nh_valid']==1].sum()/len(m)
                results.append({
                    'name': f'{fn1}+{fn2}',
                    'n': len(m), 'nh2_pct': nh2/len(m), 'nh3_pct': nh3/len(m),
                    'avg': avg
                })

        # 三过滤组合（只测常见组合）
        triple_combos = [
            ('操作区域', '前一柱甲乙', 'BSHA5'),
            ('操作区域', '前一柱乙', 'BSHA5'),
            ('操作区域', '前一柱甲乙', 'BSHA3'),
            ('操作区域', '前一柱甲乙', '周门'),
            ('操作区域', '前一柱甲乙', '柱梯'),
            ('前一柱甲乙', 'BSHA5', '周门'),
            ('前一柱甲乙', 'BSHA5', '柱梯'),
            ('前一柱乙', 'BSHA5', '周门'),
            ('操作区域', 'BSHA5', '周门'),
            ('操作区域', 'BSHA5', '柱梯'),
            ('前一柱甲乙', 'BSHA3', '周门'),
            ('BSHA5', '周门', '柱梯'),
            ('操作区域', '前一柱甲乙', 'BSHA5_周门'),
        ]
        for triple in triple_combos:
            m = sub
            ok = True
            for t in triple:
                if t in filters:
                    m = m[m[filters[t]] == 1]
                elif t == 'BSHA5_周门':
                    m = m[(m['bsha5'] == 1) & (m['zhoumen'] == 1)]
                else:
                    ok = False
            if not ok or len(m) < 50: continue
            nh2 = m['nh2'].sum()
            nh3 = m['nh3'].sum()
            avg = m['nh'][m['nh_valid']==1].sum()/len(m)
            results.append({
                'name': '+'.join(triple),
                'n': len(m), 'nh2_pct': nh2/len(m), 'nh3_pct': nh3/len(m),
                'avg': avg
            })

        # 排序输出
        results.sort(key=lambda r: r['nh2_pct'], reverse=True)
        print(f'{"排名":>3} {"过滤组合":<40} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8}')
        print('-'*80)
        for rank, r in enumerate(results, 1):
            if r['n'] < 50: continue
            print(f'{rank:>3} {r["name"]:<40} {r["n"]:>8,} {r["nh2_pct"]:>7.1%} {r["nh3_pct"]:>7.1%} {r["avg"]:>7.2f}%')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()