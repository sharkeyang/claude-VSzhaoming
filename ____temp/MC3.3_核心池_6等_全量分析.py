# -*- coding: utf-8 -*-
"""
MC3.3 核心池+6等 全量分析（向量化版）
Phase 1: 数据源统一为核心池全量 (5113只)
产出: §4.1 决策表 / §4.3 柱型交叉 / §5.6 操作区域限定+护型 / §5.6.6 触顶 / §5.6.7 BSHA提前介入
"""
import numpy as np, pandas as pd, os, glob, time, json, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
MAPPING_FILE = r'D:\@VSwork\VS昭明计划VBA优化\_产出物\MP1_花册分类映射.json'
CORE_BOARDS = {'中证500', '中证小盘', '中证非'}
USECOLS = ['日ZA','中符串','次日高幅','高幅','日ZC','DXCD','DXAB',
           '柱型','上符串','BSHA','BT连阳','BT鼎','柱排','层界']

def classify_6_vec(za_ser, last_ser):
    """向量化6等分类"""
    c6 = pd.Series('NA', index=za_ser.index, dtype='object')
    ab = last_ser.isin(['A','B']); cdef = last_ser.isin(['C','D','E','F'])
    abcd = last_ser.isin(['A','B','C','D']); ef = last_ser.isin(['E','F'])
    za_pos = za_ser > 0; za_neg = za_ser < 0
    za1 = za_ser == 1; za_neg1 = za_ser == -1
    za_ge2 = za_ser >= 2; za_le_neg2 = za_ser <= -2
    c6.loc[za_pos & za1] = '等1'
    c6.loc[za_pos & za_ge2 & ab] = '等3'
    c6.loc[za_pos & za_ge2 & cdef] = '等2'  # 原等2+等4
    c6.loc[za_neg & za_neg1] = '等5'
    c6.loc[za_neg & za_le_neg2 & abcd] = '等6'  # 原等6+等8
    c6.loc[za_neg & za_le_neg2 & ef] = '等7'
    return c6

def main():
    t0 = time.time()

    # 加载花册映射
    with open(MAPPING_FILE, encoding='utf-8') as f:
        huace = json.load(f)
    core_codes = set(k for k, v in huace.items() if v in CORE_BOARDS)
    print(f'核心池代码数: {len(core_codes)}', flush=True)

    all_files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(all_files)}', flush=True)

    core_files = []
    for f in all_files:
        name = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if name in core_codes:
            core_files.append(f)
    print(f'核心池文件: {len(core_files)}', flush=True)

    # ===== 增量聚合 =====
    from collections import defaultdict
    stats = defaultdict(lambda: {'n':0, 'nh1':0, 'nh2':0, 'nh3':0, 'nh5':0, 'nh_sum':0.0, 'pos':0, 'neg':0})
    chu_stats = defaultdict(lambda: {'n':0, 'nh2':0, 'nh3':0, 'nh_sum':0.0})
    bsha5_prev = []

    def merge_stats(keys_nhv, keys_zc=None):
        """批量合并统计: keys_nhv = [(key, nhv_series), ...]; keys_zc = [(key, zc_series), ...]"""
        for key_arr, nhv_arr in keys_nhv:
            for key, nhv in zip(key_arr, nhv_arr):
                s = stats[key]
                s['n'] += 1
                if not pd.isna(nhv):
                    if nhv > 1: s['nh1'] += 1
                    if nhv > 2: s['nh2'] += 1
                    if nhv > 3: s['nh3'] += 1
                    if nhv > 5: s['nh5'] += 1
                    s['nh_sum'] += nhv
        if keys_zc:
            for key_arr, zc_arr in keys_zc:
                if pd.api.types.is_list_like(zc_arr):
                    for key, zc in zip(key_arr, zc_arr):
                        if not pd.isna(zc):
                            if zc > 0: stats[key]['pos'] += 1
                            elif zc < 0: stats[key]['neg'] += 1

    def merge_chu(key_arr, nhv_arr):
        for key, nhv in zip(key_arr, nhv_arr):
            s = chu_stats[key]
            s['n'] += 1
            if not pd.isna(nhv):
                if nhv > 2: s['nh2'] += 1
                if nhv > 3: s['nh3'] += 1
                s['nh_sum'] += nhv

    # ===== 逐文件处理（向量化） =====
    for fi, f in enumerate(core_files):
        try:
            df = pd.read_csv(f, encoding='gbk', low_memory=False, usecols=USECOLS)
        except:
            continue
        if len(df) < 100: continue

        za = df['日ZA'].astype(float)
        mid = df['中符串'].astype(str)
        last = mid.str[-1]
        nh = df['次日高幅'].astype(float)
        high = df['高幅'].astype(float)
        zc = df['日ZC'].astype(float)
        dxab = df['DXAB'].astype(str)
        dxcd = df['DXCD'].astype(str)
        bsha = df['BSHA'].astype(float)
        btly = df['BT连阳'].astype(float)
        btd = df['BT鼎'].astype(float)
        sf = df['上符串'].astype(str)
        zhuxing = df['柱型'].astype(str)
        lay = df['层界'].astype(str).fillna('')
        zhupai = df['柱排'].astype(str).fillna('')

        # 6等分类
        c6 = classify_6_vec(za, last)
        valid = c6 != 'NA'
        if not valid.any(): continue

        # 移位列
        prev_dxab = dxab.shift(1).fillna('')
        prev_bsha = bsha.shift(1)

        # 条件向量
        bsha5 = bsha > 5; bsha4 = bsha > 4; bsha3 = bsha > 3; bsha2 = bsha > 2
        has_ly = btly > 0
        zc_gt0 = zc > 0
        dxcd_up = dxcd == '上'
        zhoumen = zc_gt0 & dxcd_up
        ab_type = dxab.str[1].fillna('')
        ab_ok = ab_type.isin(['甲','乙','己'])
        operable = zc_gt0 | (~zc_gt0 & ab_ok)
        prev_ab = prev_dxab.str[1].fillna('')
        prev_ab_ok = prev_ab.isin(['甲','乙'])
        prev_ab_ok6 = prev_ab.isin(['甲','乙','己'])
        is_chu = sf.str.contains('v', na=False)
        has_bt_ding = btd > 0
        has_cengzhu = lay.str.startswith('主')
        has_die = zhupai.str.contains('跌', na=False)
        has_lian_die = btly < 0  # 连跌（BT连阳<0）
        has_sheng = zhupai.str.contains('升', na=False) & ~zhupai.str.contains('跌', na=False)
        is_zhuti = zhuxing.str.contains('梯', na=False)
        is_zhuzha = zhuxing.str.contains('栅', na=False)
        is_zhuzhi = zhuxing.str.contains('枝', na=False)
        is_zhugen = zhuxing.str.contains('根', na=False)
        is_other_zx = ~(zhuxing.str.contains('梯', na=False) |
                        zhuxing.str.contains('栅', na=False) |
                        zhuxing.str.contains('枝', na=False) |
                        zhuxing.str.contains('根', na=False))

        idx = valid & nh.notna()
        if not idx.any(): continue

        # 对齐到有效行
        def masked(series):
            return series[idx].values

        c6_v = masked(c6)
        nh_v = nh[idx].values
        zc_v = zc[idx].values

        # 布尔掩码
        bs5 = bsha5[idx].values; bs4 = bsha4[idx].values; bs3 = bsha3[idx].values; bs2 = bsha2[idx].values
        ly = has_ly[idx].values
        zm = zhoumen[idx].values
        ok = operable[idx].values
        pa = prev_ab_ok[idx].values; pa6 = prev_ab_ok6[idx].values
        chu = is_chu[idx].values
        btd = has_bt_ding[idx].values
        cz = has_cengzhu[idx].values
        die = has_die[idx].values; ldie = has_lian_die[idx].values
        sheng = has_sheng[idx].values
        zt = is_zhuti[idx].values; zz = is_zhuzha[idx].values; zzhi = is_zhuzhi[idx].values
        zg = is_zhugen[idx].values; zx_other = is_other_zx[idx].values
        ab_v = ab_type[idx].values
        prev_ab_v = prev_ab[idx].values

        # 按6等分组
        for cls in ['等1','等2','等3','等5','等6','等7']:
            cl = c6_v == cls
            if not cl.any(): continue
            cl_nh = nh_v[cl]; cl_zc = zc_v[cl]; cl_bs5 = bs5[cl]; cl_bs4 = bs4[cl]; cl_bs3 = bs3[cl]
            cl_ly = ly[cl]; cl_zm = zm[cl]; cl_ok = ok[cl]; cl_chu = chu[cl]; cl_btd = btd[cl]
            cl_cz = cz[cl]; cl_die = die[cl]; cl_ldie = ldie[cl]; cl_sheng = sheng[cl]
            cl_zt = zt[cl]; cl_pa = pa[cl]; cl_pa6 = pa6[cl]; cl_bs2 = bs2[cl]
            cl_ab = ab_v[cl]; cl_prev_ab = prev_ab_v[cl]

            def add(k, nh_sub, zc_sub):
                stats[k]['n'] += len(nh_sub)
                stats[k]['nh1'] += int((nh_sub > 1).sum())
                stats[k]['nh2'] += int((nh_sub > 2).sum())
                stats[k]['nh3'] += int((nh_sub > 3).sum())
                stats[k]['nh5'] += int((nh_sub > 5).sum())
                stats[k]['nh_sum'] += float(nh_sub.sum())
                stats[k]['pos'] += int((zc_sub > 0).sum())
                stats[k]['neg'] += int((zc_sub < 0).sum())

            # 基准
            add(f'基准_{cls}', cl_nh, cl_zc)

            # §4.1 决策表条件
            add(f'{cls}_BSHA5_连阳_周门', cl_nh[cl_bs5 & cl_ly & cl_zm], cl_zc[cl_bs5 & cl_ly & cl_zm])
            add(f'{cls}_BSHA5', cl_nh[cl_bs5], cl_zc[cl_bs5])
            add(f'{cls}_BSHA3_连阳', cl_nh[cl_bs3 & cl_ly], cl_zc[cl_bs3 & cl_ly])
            add(f'{cls}_BSHA3', cl_nh[cl_bs3], cl_zc[cl_bs3])
            add(f'{cls}_连阳', cl_nh[cl_ly], cl_zc[cl_ly])
            add(f'{cls}_BT鼎', cl_nh[cl_btd], cl_zc[cl_btd])
            add(f'{cls}_层主', cl_nh[cl_cz], cl_zc[cl_cz])
            add(f'{cls}_升排', cl_nh[cl_sheng], cl_zc[cl_sheng])
            add(f'{cls}_层主_升排', cl_nh[cl_cz & cl_sheng], cl_zc[cl_cz & cl_sheng])
            # 负面
            add(f'{cls}_跌排', cl_nh[cl_die], cl_zc[cl_die])
            add(f'{cls}_连跌', cl_nh[cl_ldie], cl_zc[cl_ldie])
            # 无信号
            no_sig = ~(cl_bs5 | cl_bs3 | cl_ly | cl_btd)
            add(f'{cls}_无信号', cl_nh[no_sig], cl_zc[no_sig])

            # §5.6.1 操作区域限定
            add(f'op_{cls}_全量', cl_nh, cl_zc)
            add(f'op_{cls}_可操作', cl_nh[cl_ok], cl_zc[cl_ok])
            add(f'op_{cls}_ZC>0', cl_nh[cl_zm | (~cl_zm & cl_ok)], cl_zc[cl_zm | (~cl_zm & cl_ok)])
            add(f'op_{cls}_ZC≤0', cl_nh[~cl_zm & ~cl_ok], cl_zc[~cl_zm & ~cl_ok])

            # §5.6.2 等1前一柱护型
            if cls == '等1':
                for ab in '甲乙丙丁戊己':
                    idx_ab = cl_prev_ab == ab
                    if idx_ab.any():
                        add(f'prev_等1_{ab}', cl_nh[idx_ab], cl_zc[idx_ab])
                        add(f'prev_等1_{ab}_可操作', cl_nh[idx_ab & cl_ok], cl_zc[idx_ab & cl_ok])

            # §5.6.3 等2/等5/等6前一柱护型
            if cls in ['等2','等5','等6']:
                for ab in '甲乙丙丁戊己':
                    idx_ab = cl_prev_ab == ab
                    if idx_ab.any():
                        add(f'prev_{cls}_{ab}', cl_nh[idx_ab], cl_zc[idx_ab])
                add(f'prev_{cls}_甲乙己', cl_nh[cl_pa6], cl_zc[cl_pa6])
                add(f'prev_{cls}_丙丁戊', cl_nh[~cl_pa6 & np.isin(cl_prev_ab, ['丙','丁','戊'])], cl_zc[~cl_pa6 & np.isin(cl_prev_ab, ['丙','丁','戊'])])

            # §5.6.5 赛马组合增强
            if cls == '等1':
                add(f'race_等1_BSHA5', cl_nh[cl_bs5], cl_zc[cl_bs5])
                add(f'race_等1_BSHA5_可操作', cl_nh[cl_bs5 & cl_ok], cl_zc[cl_bs5 & cl_ok])
                add(f'race_等1_BSHA5_前甲乙', cl_nh[cl_bs5 & cl_pa], cl_zc[cl_bs5 & cl_pa])
                add(f'race_等1_BSHA5_可操作_前甲乙', cl_nh[cl_bs5 & cl_ok & cl_pa], cl_zc[cl_bs5 & cl_ok & cl_pa])
                add(f'race_等1_BSHA5_周门', cl_nh[cl_bs5 & cl_zm], cl_zc[cl_bs5 & cl_zm])
                add(f'race_等1_BSHA5_周门_前甲乙', cl_nh[cl_bs5 & cl_zm & cl_pa], cl_zc[cl_bs5 & cl_zm & cl_pa])
            else:
                if cls in ['等2','等3','等5','等6','等7']:
                    add(f'race_{cls}_BSHA5', cl_nh[cl_bs5], cl_zc[cl_bs5])
                    add(f'race_{cls}_BSHA5_可操作', cl_nh[cl_bs5 & cl_ok], cl_zc[cl_bs5 & cl_ok])
                    add(f'race_{cls}_BSHA5_前甲乙', cl_nh[cl_bs5 & cl_pa], cl_zc[cl_bs5 & cl_pa])
                    add(f'race_{cls}_BSHA5_周门', cl_nh[cl_bs5 & cl_zm], cl_zc[cl_bs5 & cl_zm])
                    add(f'race_{cls}_BSHA5_周门_前甲乙', cl_nh[cl_bs5 & cl_zm & cl_pa], cl_zc[cl_bs5 & cl_zm & cl_pa])
                if cls in ['等5','等6']:
                    add(f'race_{cls}_BSHA4_周门', cl_nh[cl_bs4 & cl_zm], cl_zc[cl_bs4 & cl_zm])

            # §5.6.6 触顶
            if cls in ['等1','等2','等3','等6']:
                c_chu = cl_chu; c_nchu = ~cl_chu
                # 触顶 vs 不触顶
                for k_chu, m_chu in [(f'{cls}_触顶', c_chu), (f'{cls}_不触顶', c_nchu)]:
                    if m_chu.any():
                        s = chu_stats[k_chu]; sub = cl_nh[m_chu]
                        s['n'] += len(sub)
                        s['nh2'] += int((sub > 2).sum())
                        s['nh3'] += int((sub > 3).sum())
                        s['nh_sum'] += float(sub.sum())
                # 触顶+BSHA5
                for k_chu, m_chu in [(f'{cls}_触顶_BSHA5', c_chu & cl_bs5), (f'{cls}_不触顶_BSHA5', c_nchu & cl_bs5)]:
                    if m_chu.any():
                        s = chu_stats[k_chu]; sub = cl_nh[m_chu]
                        s['n'] += len(sub)
                        s['nh2'] += int((sub > 2).sum())
                        s['nh3'] += int((sub > 3).sum())
                        s['nh_sum'] += float(sub.sum())
                # 触顶+BSHA4
                if cls == '等6':
                    for k_chu, m_chu in [(f'{cls}_触顶_BSHA4', c_chu & cl_bs4), (f'{cls}_不触顶_BSHA4', c_nchu & cl_bs4)]:
                        if m_chu.any():
                            s = chu_stats[k_chu]; sub = cl_nh[m_chu]
                            s['n'] += len(sub)
                            s['nh2'] += int((sub > 2).sum())
                            s['nh3'] += int((sub > 3).sum())
                            s['nh_sum'] += float(sub.sum())

            # §5.6.7 BSHA提前介入
            if cls in ['等1','等2','等3','等6']:
                pass  # 后面单独处理

        # ===== §4.3 柱型维度（全局分类） =====
        # 柱型类别
        zx_map = {'柱梯': zt, '柱栅': zz, '柱枝': zzhi, '柱根': zg, '柱其他': zx_other}
        for zx_label, zx_mask in zx_map.items():
            if not zx_mask.any(): continue
            add(f'柱型_{zx_label}', nh_v[zx_mask], zc_v[zx_mask])
            add(f'柱型_{zx_label}_周门', nh_v[zx_mask & zm], zc_v[zx_mask & zm])
            for cls in ['等1','等2','等3','等5','等6','等7']:
                cl = (c6_v == cls) & zx_mask
                if cl.any():
                    add(f'柱型_{zx_label}_{cls}', nh_v[cl], zc_v[cl])
                    add(f'柱型_{zx_label}_{cls}_周门', nh_v[cl & zm], zc_v[cl & zm])

        # ===== §5.6.7 BSHA提前介入（全局） =====
        all_bsha_keys = [(f'{cls}_BSHA2', bs2, cls) for cls in ['等1','等2','等3','等6']]
        all_bsha_keys += [(f'{cls}_BSHA3', bs3, cls) for cls in ['等1','等2','等3','等6']]
        all_bsha_keys += [(f'{cls}_BSHA4', bs4, cls) for cls in ['等1','等2','等3','等6']]
        all_bsha_keys += [(f'{cls}_BSHA5', bs5, cls) for cls in ['等1','等2','等3','等6']]
        # 在 chu_stats 中累积 BSHA thresh
        for key, bsha_mask, cls in all_bsha_keys:
            m = bsha_mask & (c6_v == cls)
            if m.any():
                s = chu_stats[key]; sub = nh_v[m]
                s['n'] += len(sub)
                s['nh2'] += int((sub > 2).sum())
                s['nh3'] += int((sub > 3).sum())
                s['nh_sum'] += float(sub.sum())

        # BSHA5前一天分布
        bsha5_rows = bsha5 & (c6 != 'NA')
        if bsha5_rows.any():
            pv = prev_bsha[bsha5_rows].values
            bsha5_prev.extend(pv[pd.notna(pv)].tolist())

        if (fi+1) % 500 == 0:
            print(f'  [{fi+1}/{len(core_files)}] {time.time()-t0:.0f}s', flush=True)

    print(f'\n核心池全量处理完成 {len(core_files)} 文件, 耗时 {time.time()-t0:.0f}s', flush=True)

    # ===== 输出辅助 =====
    def pct(s):
        n2 = s['nh2']/s['n'] if s['n'] else 0
        n3 = s['nh3']/s['n'] if s['n'] else 0
        n1 = s['nh1']/s['n'] if s['n'] else 0
        avg = s['nh_sum']/s['n'] if s['n'] else 0
        dr = s['pos']/s['n'] if s['n'] else 0
        return s['n'], n1, n2, n3, avg, dr

    def show_row(label, s, detail=True):
        n, n1, n2, n3, avg, dr = pct(s)
        if detail:
            print(f'{label:<30} {n:>8,} {n1:>7.1%} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}% {dr:>7.1%}')
        else:
            print(f'{label:<30} {n:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}%')

    # ========================================================================
    # §4.1 决策表
    # ========================================================================
    print('\n' + '='*100)
    print('§4.1 决策表（核心池5113只，6等 — 等2=原等2+等4合并，等6=原等6+等8合并）')
    print('='*100)
    print(f'基准比较:')
    print(f'{"等类":<6} {"样本":>8} {"≥1%":>7} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
    for c in ['等1','等2','等3','等5','等6','等7']:
        k = f'基准_{c}'
        if k in stats: show_row(c, stats[k])

    for c in ['等1','等2','等3','等5','等6','等7']:
        k_base = f'基准_{c}'
        if k_base not in stats: continue
        print(f'\n--- {c} ---')
        print(f'{"条件":<30} {"样本":>8} {"≥1%":>7} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
        print('-'*85)
        show_row(f'{c} 基准', stats[k_base])
        for cond in ['BSHA5_连阳_周门','BSHA5','BSHA3_连阳','BSHA3','连阳','BT鼎','层主','升排','层主_升排']:
            k = f'{c}_{cond}'
            if k in stats: show_row(f'  {cond}', stats[k])
        for cond in ['跌排','连跌','无信号']:
            k = f'{c}_{cond}'
            if k in stats: show_row(f'  {cond}', stats[k])

    # ========================================================================
    # §4.3 柱型维度
    # ========================================================================
    print('\n' + '='*100)
    print('§4.3 柱型维度 — Baseline')
    print('='*100)
    print(f'{"柱型":<16} {"样本":>8} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
    print('-'*60)
    for zx_label in ['柱梯','柱栅','柱枝','柱根','柱其他']:
        k = f'柱型_{zx_label}'
        if k in stats: show_row(zx_label, stats[k], False)

    print(f'\n{"柱型+周门":<16}')
    for zx_label in ['柱梯','柱栅','柱枝','柱根','柱其他']:
        k = f'柱型_{zx_label}_周门'
        if k in stats: show_row(zx_label, stats[k], False)

    print('\n--- 柱型 × 等高线 交叉赛马（H2排序 top 25） ---')
    print(f'{"排名":<4} {"组合":<35} {"样本":>8} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
    print('-'*85)
    race_items = []
    for zx_label in ['柱梯','柱栅','柱枝','柱根','柱其他']:
        for cls in ['等1','等2','等3','等5','等6','等7']:
            for suffix, label_suffix in [('', ''), ('_周门', '+周门')]:
                k = f'柱型_{zx_label}_{cls}{suffix}'
                if k in stats:
                    s = stats[k]
                    n2 = s['nh2']/s['n'] if s['n'] else 0
                    race_items.append((n2, f'{zx_label}+{cls}{label_suffix}', s))
    race_items.sort(key=lambda x: -x[0])
    for rank, (n2, label, s) in enumerate(race_items[:25], 1):
        n, _, _, n3, avg, dr = pct(s)
        print(f'{rank:<4} {label:<35} {n:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}% {dr:>7.1%}')

    # ========================================================================
    # §5.6.1 操作区域限定
    # ========================================================================
    print('\n' + '='*100)
    print('§5.6.1 操作区域限定（核心池5113只）')
    print('='*100)
    print(f'{"等高线":<8} {"全量样本":>8} {"全量≥2%":>8} {"可操作样本":>10} {"可操作≥2%":>10} {"提升":>6}')
    print('-'*55)
    for c in ['等1','等2','等3','等5','等6','等7']:
        k_all = f'op_{c}_全量'
        k_ok = f'op_{c}_可操作'
        if k_all in stats:
            s_all = stats[k_all]
            n2_all = s_all['nh2']/s_all['n']
            if k_ok in stats:
                s_ok = stats[k_ok]
                n2_ok = s_ok['nh2']/s_ok['n']
                boost = (n2_ok - n2_all) * 100
                print(f'{c:<8} {s_all["n"]:>8,} {n2_all:>7.1%} {s_ok["n"]:>10,} {n2_ok:>9.1%} {boost:>+5.1f}pp')

    # ========================================================================
    # §5.6.2/§5.6.3 前一柱护型
    # ========================================================================
    print('\n' + '='*100)
    print('§5.6.2 等1 前一柱护型')
    print('='*100)
    print(f'{"前一柱护型":<12} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8} {"下柱>0":>8}')
    print('-'*55)
    for ab in '甲乙丙丁戊己':
        k = f'prev_等1_{ab}'
        if k in stats: show_row(ab, stats[k])

    print('\n§5.6.3 等2/等5/等6 前一柱护型')
    for c in ['等2','等5','等6']:
        print(f'\n--- {c} ---')
        print(f'{"前一柱护型":<12} {"样本":>8} {"≥2%":>8} {"≥3%":>8} {"均冲高":>8} {"下柱>0":>8}')
        for ab in '甲乙丙丁戊己':
            k = f'prev_{c}_{ab}'
            if k in stats: show_row(ab, stats[k])
        k_ok = f'prev_{c}_甲乙己'
        k_bad = f'prev_{c}_丙丁戊'
        if k_ok in stats: show_row('甲乙己(优)', stats[k_ok])
        if k_bad in stats: show_row('丙丁戊(弱)', stats[k_bad])

    # ========================================================================
    # §5.6.5 赛马组合增强
    # ========================================================================
    print('\n' + '='*100)
    print('§5.6.5 赛马组合增强（核心池5113只）')
    print('='*100)

    # 等1 赛马排名
    print('\n等1 赛马排名（H2排序）:')
    print(f'{"组合":<45} {"样本":>8} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7}')
    print('-'*80)
    race1_items = [(stats[k]['nh2']/stats[k]['n'], k.replace('race_等1_',''), stats[k])
                   for k in stats if k.startswith('race_等1_')]
    race1_items.sort(key=lambda x: -x[0])
    for n2, label, s in race1_items:
        n, _, _, n3, avg, _ = pct(s)
        print(f'等1+{label:<35} {n:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}%')

    for cls in ['等2','等3','等5','等6','等7']:
        r_items = [(stats[k]['nh2']/stats[k]['n'], k.replace(f'race_{cls}_',''), stats[k])
                   for k in stats if k.startswith(f'race_{cls}_') and stats[k]['n'] >= 100]
        if r_items:
            r_items.sort(key=lambda x: -x[0])
            print(f'\n{cls} BSHA5赛马:')
            print(f'{"组合":<45} {"样本":>8} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7}')
            print('-'*80)
            for n2, label, s in r_items:
                n, _, _, n3, avg, _ = pct(s)
                print(f'{cls}+{label:<35} {n:>8,} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}%')

    # ========================================================================
    # §5.6.6 触顶条件
    # ========================================================================
    print('\n' + '='*100)
    print('§5.6.6 触顶条件（核心池5113只）')
    print('='*100)
    print(f'{"等高线":<6} {"触顶≥2%":>9} {"不触顶≥2%":>11} {"差异":>6} {"触顶样本":>9}')
    for c in ['等1','等2','等3','等6']:
        k1 = f'{c}_触顶'; k2 = f'{c}_不触顶'
        if k1 in chu_stats and k2 in chu_stats:
            n21 = chu_stats[k1]['nh2']/chu_stats[k1]['n']*100
            n22 = chu_stats[k2]['nh2']/chu_stats[k2]['n']*100
            print(f'{c:<6} {n21:>8.1f}% {n22:>10.1f}% {n21-n22:>+5.1f}pp {chu_stats[k1]["n"]:>9,}')

    print(f'\n--- 触顶+BSHA5 ---')
    print(f'{"等高线":<6} {"触顶+BSHA5≥2%":>14} {"不触顶+BSHA5≥2%":>16} {"差异":>6} {"触顶样本":>9}')
    for c in ['等1','等2','等3','等6']:
        k1 = f'{c}_触顶_BSHA5'; k2 = f'{c}_不触顶_BSHA5'
        if k1 in chu_stats and k2 in chu_stats:
            n21 = chu_stats[k1]['nh2']/chu_stats[k1]['n']*100
            n22 = chu_stats[k2]['nh2']/chu_stats[k2]['n']*100
            print(f'{c:<6} {n21:>13.1f}% {n22:>15.1f}% {n21-n22:>+5.1f}pp {chu_stats[k1]["n"]:>9,}')

    print(f'\n--- 触顶+BSHA4（等6专属）---')
    for c in ['等6']:
        k1 = f'{c}_触顶_BSHA4'; k2 = f'{c}_不触顶_BSHA4'
        if k1 in chu_stats and k2 in chu_stats:
            n21 = chu_stats[k1]['nh2']/chu_stats[k1]['n']*100
            n22 = chu_stats[k2]['nh2']/chu_stats[k2]['n']*100
            print(f'{c:<6} {n21:>13.1f}% {n22:>15.1f}% {n21-n22:>+5.1f}pp {chu_stats[k1]["n"]:>9,}')

    # ========================================================================
    # §5.6.7 BSHA提前介入
    # ========================================================================
    print('\n' + '='*100)
    print('§5.6.7 BSHA提前介入（核心池5113只，6等）')
    print('='*100)
    print(f'{"等高线":<6} {"BSHA2":>8} {"BSHA3":>8} {"BSHA4":>8} {"BSHA5":>8} {"BSHA5-2":>10}')
    for c in ['等1','等2','等3','等6']:
        vals = []
        for th in [2,3,4,5]:
            k = f'{c}_BSHA{th}'
            if k in chu_stats:
                vals.append(chu_stats[k]['nh2']/chu_stats[k]['n'])
            else:
                vals.append(None)
        if vals[0] and vals[3]:
            diff = (vals[3] - vals[0])*100
            v_str = ' '.join(f'{v*100:>7.1f}%' if v else '  N/A  ' for v in vals)
            print(f'{c:<6} {v_str} {diff:>+7.1f}pp')
        else:
            v_str = ' '.join(f'{v*100:>7.1f}%' if v else '  N/A  ' for v in vals)
            print(f'{c:<6} {v_str}')

    # BSHA5前一天分布
    print('\n--- BSHA5前一天BSHA分布 ---')
    arr = np.array(bsha5_prev)
    print(f'BSHA5总样本: {len(arr):,}')
    print(f'前一天BSHA均值: {arr.mean():.2f}%')
    print(f'前一天BSHA中位数: {np.median(arr):.2f}%')
    print(f'分布:')
    print(f'  ≥5(连续两天): {(arr>=5).mean():.1%}')
    print(f'  4~5: {((arr>=4)&(arr<5)).mean():.1%}')
    print(f'  3~4: {((arr>=3)&(arr<4)).mean():.1%}')
    print(f'  2~3: {((arr>=2)&(arr<3)).mean():.1%}')
    print(f'  <2(无信号): {(arr<2).mean():.1%}')

    # 汇总
    print('\n' + '='*100)
    print('核心池6等 基准汇总')
    print('='*100)
    print(f'{"等类":<6} {"样本":>8} {"≥1%":>7} {"≥2%":>7} {"≥3%":>7} {"均冲高":>7} {"下柱>0":>7}')
    total_n = 0; total_nh2 = 0
    for c in ['等1','等2','等3','等5','等6','等7']:
        k = f'基准_{c}'
        if k in stats:
            n, n1, n2, n3, avg, dr = pct(stats[k])
            total_n += n; total_nh2 += stats[k]['nh2']
            print(f'{c:<6} {n:>8,} {n1:>7.1%} {n2:>7.1%} {n3:>7.1%} {avg:>6.2f}% {dr:>7.1%}')
    print(f'{"总计":<6} {total_n:>8,} {"":>7} {total_nh2/total_n:>7.1%}')

    print(f'\n总耗时: {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()