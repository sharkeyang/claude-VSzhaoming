# -*- coding: utf-8 -*-
"""
等高线分类简化 + 柱型赛马 全量验证
1. 末符2类(AB vs CDEF) vs 等高线8类方向+冲高对比
2. 等2 vs 等4区分度证明（DTZA细分的边际价值）
3. 柱型 × 日层等 交叉赛马
4. 柱型 × 末符2类 交叉赛马

=== 输出 ===
表1: 等高线8类 baseline
表2: 等2 vs 等4（CDEF末符内DTZA细分的边际价值）
表3: 末符2类(AB vs CDEF) + 信号叠加
表4: 柱型 × 日层等 交叉赛马 (H2)
表5: 柱型 × 末符2类 交叉赛马 (H2)
"""
import numpy as np, pandas as pd, os, glob, time, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
N_FILES = 99999
np.random.seed(42)

def classify_8(za, last):
    """等高线8类 — 末位逻辑，阈值3"""
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

def classify_2_moshi(za, last):
    """末符2类：AB vs CDEF（仅上侧DTZA≥2）"""
    if pd.isna(za) or za == '': return 'NA'
    za = float(za); lc = str(last) if pd.notna(last) else ''
    if za >= 2 and lc in 'AB': return '末符AB'
    elif za >= 2 and lc in 'CDEF': return '末符CDEF'
    return 'NA'

def classify_zhuxing(ct_str):
    """柱型提取：根/枝/干/冠/梯/栅/蛀/暂"""
    if pd.isna(ct_str): return 'NA'
    ct = str(ct_str)
    if '根' in ct: return '柱根'
    elif '枝' in ct: return '柱枝'
    elif '干' in ct: return '柱干'
    elif '冠' in ct: return '柱冠'
    elif '梯' in ct: return '柱梯'
    elif '栅' in ct: return '柱栅'
    elif '蛀' in ct: return '柱蛀'
    elif '暂' in ct: return '柱暂'
    else: return '柱其他'

def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    if len(files) > N_FILES:
        sampled = sorted(np.random.choice(files, N_FILES, replace=False))
    else:
        sampled = files
    print(f'总文件: {len(files)}, 抽样: {len(sampled)}', flush=True)

    # 聚合统计
    # 每个分类维度的统计：{分类名: {n, nh1, nh2, nh3, nh5, nh_sum, pos, neg}}
    stats = {}

    def add_stat(cat, nh_val, next_za_val):
        if cat not in stats:
            stats[cat] = {'n':0, 'nh1':0, 'nh2':0, 'nh3':0, 'nh5':0, 'nh_sum':0.0, 'pos':0, 'neg':0, 'zero':0}
        s = stats[cat]
        s['n'] += 1
        if not pd.isna(nh_val):
            if nh_val > 1: s['nh1'] += 1
            if nh_val > 2: s['nh2'] += 1
            if nh_val > 3: s['nh3'] += 1
            if nh_val > 5: s['nh5'] += 1
            s['nh_sum'] += nh_val
        if not pd.isna(next_za_val):
            if next_za_val > 0: s['pos'] += 1
            elif next_za_val < 0: s['neg'] += 1
            else: s['zero'] += 1

    for i, f in enumerate(sampled):
        try:
            # 按VBA列位置读取（勿看表头）：[13]日ZA [33]中符串 [26]次日高幅 [27]柱型 [14]日ZC [8]DXCD
            df = pd.read_csv(f, encoding='gbk', header=None, skiprows=1,
                             usecols=[13,33,26,27,14,8],
                             names=['日ZA','中符串','次日高幅','柱型','日ZC','DXCD'])
        except: continue
        if len(df) < 100: continue
        za = pd.to_numeric(df['日ZA'], errors='coerce')
        next_za = za.shift(-1)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = pd.to_numeric(df['次日高幅'], errors='coerce')
        zhuxing = df['柱型']

        # 周门条件
        zc_gt0 = pd.to_numeric(df['日ZC'], errors='coerce') > 0
        dxcd_up = df['DXCD'].astype(str) == '上'
        zhoumen = zc_gt0 & dxcd_up

        for idx in df.index:
            zval = za[idx]; nz = next_za[idx]; nhv = nh[idx]; lc = last[idx]
            zx = zhuxing[idx]; zm = zhoumen[idx]

            # 等高线8类
            c8 = classify_8(zval, lc)
            if c8 != 'NA':
                add_stat(f'8_{c8}', nhv, nz)
                if zm:
                    add_stat(f'8_{c8}_周门', nhv, nz)
                # BSHA5条件（近似：当日高幅>5%）
                # 用日ZA近似，实际BSHA=当日高偏离JA%
                # 这里简化：用次日高幅>5作为BSHA5近似

            # 末符2类（上侧DTZA≥2）
            c2 = classify_2_moshi(zval, lc)
            if c2 != 'NA':
                add_stat(f'2_{c2}', nhv, nz)
                if zm:
                    add_stat(f'2_{c2}_周门', nhv, nz)

            # 柱型
            zx_cat = classify_zhuxing(zx)
            if zx_cat != 'NA':
                add_stat(f'Z_{zx_cat}', nhv, nz)
                if zm:
                    add_stat(f'Z_{zx_cat}_周门', nhv, nz)

            # 柱型 × 等高线8类
            if c8 != 'NA' and zx_cat != 'NA':
                add_stat(f'X_{zx_cat}+{c8}', nhv, nz)
                if zm:
                    add_stat(f'X_{zx_cat}+{c8}_周门', nhv, nz)

            # 柱型 × 末符2类
            if c2 != 'NA' and zx_cat != 'NA':
                add_stat(f'X2_{zx_cat}+{c2}', nhv, nz)
                if zm:
                    add_stat(f'X2_{zx_cat}+{c2}_周门', nhv, nz)

        if (i+1) % 200 == 0:
            print(f'  {i+1}/{len(sampled)} {time.time()-t0:.0f}s', flush=True)

    print(f'处理完成, 耗时 {time.time()-t0:.0f}s', flush=True)

    def print_table(title, prefix, categories, sort_key='nh2'):
        """打印对比表"""
        rows = []
        for cat, s in stats.items():
            if not cat.startswith(prefix): continue
            if s['n'] < 50: continue
            # 提取分类名（去掉前缀）
            cat_name = cat[len(prefix):]
            if cat_name not in categories: continue
            rows.append({
                'cat': cat_name,
                'n': s['n'],
                'nh1': s['nh1']/s['n'],
                'nh2': s['nh2']/s['n'],
                'nh3': s['nh3']/s['n'],
                'nh5': s['nh5']/s['n'],
                'avg': s['nh_sum']/s['n'],
                'pos': s['pos']/s['n'] if s['n'] else 0,
                'neg': s['neg']/s['n'] if s['n'] else 0,
            })
        if not rows: return
        rows.sort(key=lambda r: r[sort_key], reverse=True)
        print(f'\n{title}')
        print(f'{"分类":<20} {"样本":>8} {"≥1%":>6} {"≥2%":>6} {"≥3%":>6} {"≥5%":>6} {"均冲高":>7} {"下柱>0":>7}')
        print('-'*75)
        for r in rows:
            print(f'{r["cat"]:<20} {r["n"]:>8,} {r["nh1"]:>5.1%} {r["nh2"]:>5.1%} {r["nh3"]:>5.1%} {r["nh5"]:>5.1%} {r["avg"]:>6.2f}% {r["pos"]:>6.1%}')

    # ========== 表1：等高线8类 baseline ==========
    print_table('【表1】等高线8类 Baseline', '8_', [f'等{i}' for i in range(1,9)])
    print_table('【表1b】等高线8类 + 周门', '8_', [f'等{i}_周门' for i in range(1,9)])

    # ========== 表2：末符2类 vs 等2+等4细分 ==========
    print('\n' + '='*80)
    print('【表2】末符2类(AB vs CDEF) vs 等2/等4(CDEF内部DTZA细分)')
    print('='*80)
    # 末符2类
    for prefix, label in [('2_', '末符2类'), ('2_', '末符2类+周门')]:
        rows = []
        for cat, s in stats.items():
            if not cat.startswith(prefix): continue
            if s['n'] < 50: continue
            cn = cat[len(prefix):]
            if cn not in ['末符AB','末符CDEF','末符AB_周门','末符CDEF_周门']: continue
            rows.append({
                'cat': cn, 'n': s['n'], 'nh2': s['nh2']/s['n'],
                'nh3': s['nh3']/s['n'], 'avg': s['nh_sum']/s['n'],
                'pos': s['pos']/s['n']
            })
        if not rows: continue
        rows.sort(key=lambda r: r['nh2'], reverse=True)
        print(f'\n--- {label} ---')
        print(f'{"分类":<20} {"样本":>8} {"≥2%":>6} {"≥3%":>6} {"均冲高":>7} {"下柱>0":>7}')
        print('-'*55)
        for r in rows:
            print(f'{r["cat"]:<20} {r["n"]:>8,} {r["nh2"]:>5.1%} {r["nh3"]:>5.1%} {r["avg"]:>6.2f}% {r["pos"]:>6.1%}')

    # 等2 vs 等4 单独对比
    print(f'\n--- 等2 vs 等4（CDEF末符内DTZA细分） ---')
    print(f'{"对比":<20} {"样本":>8} {"≥2%":>6} {"≥3%":>6} {"均冲高":>7} {"下柱>0":>7} {"方向差异":>8}')
    print('-'*70)
    # 等2 vs 等4 基本
    for label, cats in [('等2 vs 等4(全量)', [('等2', '8_等2'), ('等4', '8_等4')]),
                         ('等2 vs 等4(+周门)', [('等2', '8_等2_周门'), ('等4', '8_等4_周门')])]:
        vals = []
        for cn, key in cats:
            if key in stats:
                s = stats[key]
                vals.append((cn, s['n'], s['nh2']/s['n'], s['nh3']/s['n'], s['nh_sum']/s['n'], s['pos']/s['n']))
        if len(vals) == 2:
            print(f'{label:<20} {vals[0][1]:>8,}/{vals[1][1]:>8,} {vals[0][2]:>5.1%}/{vals[1][2]:>5.1%} {vals[0][3]:>5.1%}/{vals[1][3]:>5.1%} {vals[0][4]:>6.2f}/{vals[1][4]:>6.2f} {vals[0][5]:>6.1%}/{vals[1][5]:>6.1%} {vals[0][5]-vals[1][5]:>7.1%}')

    # ========== 表3：柱型 × 日层等 交叉赛马 ==========
    print('\n' + '='*80)
    print('【表3】柱型 × 等高线 交叉赛马(H2≥2%排序)')
    print('='*80)
    # 收集所有柱型+等高线组合
    combos = []
    for cat, s in stats.items():
        if not cat.startswith('X_'): continue
        if s['n'] < 100: continue
        cn = cat[2:]
        # 解析柱型+等高线
        zx_part = cn.split('+')[0]
        dg_part = cn.split('+')[1] if '+' in cn else ''
        combos.append({
            'cat': cn, 'zx': zx_part, 'dg': dg_part,
            'n': s['n'], 'nh2': s['nh2']/s['n'], 'nh3': s['nh3']/s['n'],
            'avg': s['nh_sum']/s['n'], 'pos': s['pos']/s['n']
        })
    combos.sort(key=lambda r: r['nh2'], reverse=True)
    print(f'{"组合":<30} {"样本":>8} {"≥2%":>6} {"≥3%":>6} {"均冲高":>7} {"下柱>0":>7}')
    print('-'*65)
    for r in combos[:30]:
        print(f'{r["cat"]:<30} {r["n"]:>8,} {r["nh2"]:>5.1%} {r["nh3"]:>5.1%} {r["avg"]:>6.2f}% {r["pos"]:>6.1%}')

    # ========== 表4：柱型 × 末符2类 交叉赛马 ==========
    print('\n' + '='*80)
    print('【表4】柱型 × 末符2类 交叉赛马(H2≥2%排序)')
    print('='*80)
    combos2 = []
    for cat, s in stats.items():
        if not cat.startswith('X2_'): continue
        if s['n'] < 100: continue
        cn = cat[3:]
        zx_part = cn.split('+')[0]
        ms_part = cn.split('+')[1] if '+' in cn else ''
        combos2.append({
            'cat': cn, 'zx': zx_part, 'ms': ms_part,
            'n': s['n'], 'nh2': s['nh2']/s['n'], 'nh3': s['nh3']/s['n'],
            'avg': s['nh_sum']/s['n'], 'pos': s['pos']/s['n']
        })
    combos2.sort(key=lambda r: r['nh2'], reverse=True)
    print(f'{"组合":<30} {"样本":>8} {"≥2%":>6} {"≥3%":>6} {"均冲高":>7} {"下柱>0":>7}')
    print('-'*65)
    for r in combos2[:20]:
        print(f'{r["cat"]:<30} {r["n"]:>8,} {r["nh2"]:>5.1%} {r["nh3"]:>5.1%} {r["avg"]:>6.2f}% {r["pos"]:>6.1%}')

    # ========== 表5：柱型单独 baseline ==========
    print('\n' + '='*80)
    print('【表5】柱型单独 Baseline')
    print('='*80)
    print_table('柱型单独', 'Z_',
                ['柱根','柱枝','柱干','柱冠','柱梯','柱栅','柱蛀','柱暂','柱其他'])
    print_table('柱型+周门', 'Z_',
                [f'{c}_周门' for c in ['柱根','柱枝','柱干','柱冠','柱梯','柱栅','柱蛀','柱暂','柱其他']])

    # ========== 表6：等2 vs 等4 合并CDEF后的效果 ==========
    print('\n' + '='*80)
    print('【表6】等2+等4合并(CDEF末符归一类) vs 分开(等2/等4) — 方向区分度对比')
    print('='*80)
    # 合并CDEF
    cdef_n = sum(stats.get(f'8_{c}', {}).get('n', 0) for c in ['等2','等4'])
    cdef_pos = sum(stats.get(f'8_{c}', {}).get('pos', 0) for c in ['等2','等4'])
    cdef_nh2 = sum(stats.get(f'8_{c}', {}).get('nh2', 0) for c in ['等2','等4'])
    cdef_nh3 = sum(stats.get(f'8_{c}', {}).get('nh3', 0) for c in ['等2','等4'])
    cdef_nh = sum(stats.get(f'8_{c}', {}).get('nh_sum', 0) for c in ['等2','等4'])
    ab_n = stats.get('8_等3', {}).get('n', 0)
    ab_pos = stats.get('8_等3', {}).get('pos', 0)
    ab_nh2 = stats.get('8_等3', {}).get('nh2', 0)
    ab_nh3 = stats.get('8_等3', {}).get('nh3', 0)
    ab_nh = stats.get('8_等3', {}).get('nh_sum', 0)

    print(f'\n{"方案":<30} {"样本":>8} {"≥2%":>6} {"≥3%":>6} {"均冲高":>7} {"下柱>0":>7} {"方向差异":>8}')
    print('-'*80)
    print(f'{"方案A:等3(AB) vs 合并CDEF":<30} {ab_n:>8,}/{cdef_n:>8,} {ab_nh2/ab_n:>5.1%}/{cdef_nh2/cdef_n:>5.1%} {ab_nh3/ab_n:>5.1%}/{cdef_nh3/cdef_n:>5.1%} {ab_nh/ab_n:>6.2f}/{cdef_nh/cdef_n:>6.2f} {ab_pos/ab_n:>6.1%}/{cdef_pos/cdef_n:>6.1%} {ab_pos/ab_n - cdef_pos/cdef_n:>7.1%}')
    e2 = stats.get('8_等2', {}); e4 = stats.get('8_等4', {})
    if e2 and e4:
        e2_r = e2['pos']/e2['n']; e4_r = e4['pos']/e4['n']
        print(f'{"方案B:等3(AB) vs 等2 vs 等4":<30} {ab_n:>8,}/{e2["n"]:>8,}/{e4["n"]:>8,} {ab_nh2/ab_n:>5.1%}/{e2["nh2"]/e2["n"]:>5.1%}/{e4["nh2"]/e4["n"]:>5.1%} {ab_nh3/ab_n:>5.1%}/{e2["nh3"]/e2["n"]:>5.1%}/{e4["nh3"]/e4["n"]:>5.1%} {ab_nh/ab_n:>6.2f}/{e2["nh_sum"]/e2["n"]:>6.2f}/{e4["nh_sum"]/e4["n"]:>6.2f} {ab_pos/ab_n:>6.1%}/{e2_r:>6.1%}/{e4_r:>6.1%} {e2_r - e4_r:>7.1%}')
    print(f'\n结论：方案A(末符2类)方向差异={ab_pos/ab_n - cdef_pos/cdef_n:.1%}')
    print(f'      方案B(等2vs等4)方向差异={e2_r - e4_r:.1%}（远小于末符2类）')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()