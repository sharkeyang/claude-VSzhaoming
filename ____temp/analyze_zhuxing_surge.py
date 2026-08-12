# -*- coding: utf-8 -*-
"""
柱型 × 下日冲高 全量验证
重点：梯(机会) vs 栏栅(需小阳柱确认)
"""
import numpy as np, pandas as pd, os, glob, warnings
warnings.simplefilter('ignore')

DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'

def classify_zhuxing(ct_str):
    """柱型根部分类"""
    if pd.isna(ct_str): return 'NA'
    ct = str(ct_str)
    if '梯' in ct: return '梯'
    elif '栅' in ct: return '栅'
    elif '枝' in ct: return '枝'
    elif '根' in ct: return '根'
    elif '干' in ct: return '干'
    elif '冠' in ct: return '冠'
    elif '蛀' in ct: return '蛀'
    elif '暂' in ct: return '暂'
    else: return '其他'

def classify_zhuxing_sub(ct_str):
    """柱型细分"""
    if pd.isna(ct_str): return 'NA'
    ct = str(ct_str)
    if '梯升连冲' in ct: return '梯升连冲'
    elif '梯升孕冲' in ct: return '梯升孕冲'
    elif '梯升调待' in ct: return '梯升调待'
    elif '梯交调待' in ct: return '梯交调待'
    elif '梯交跌警' in ct: return '梯交跌警'
    elif '栅' in ct: return '栅'
    elif '枝启升冲' in ct: return '枝启升冲'
    elif '枝启踩警' in ct: return '枝启踩警'
    elif '枝贯连待' in ct or '枝贯单待' in ct: return '枝贯待'
    else: return ct[:6]

def classify_dxzc(dxzc_val, dxab_val):
    """DXZC+DXAB条件"""
    if pd.isna(dxzc_val) or pd.isna(dxab_val): return 'NA'
    dxab = str(dxab_val)
    zc = float(dxzc_val)
    if zc > 0:
        return 'ZC>0_任意AB'
    else:
        if dxab in ('甲','乙','己'): return 'ZC<0_甲乙己'
        else: return 'ZC<0_丙丁戊'

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    # 用全部数据
    print(f'总文件: {len(files)}', flush=True)

    # 统计结构
    stats = {}

    def add(cat, nh_val, gf_val, zc_val, dxab_val):
        if cat not in stats:
            stats[cat] = {'n':0, 'nh2':0, 'nh3':0, 'nh_sum':0.0, 'gf2':0, 'gf3':0, 'gf_sum':0.0}
        s = stats[cat]
        s['n'] += 1
        if not pd.isna(nh_val):
            if nh_val >= 2: s['nh2'] += 1
            if nh_val >= 3: s['nh3'] += 1
            s['nh_sum'] += nh_val
        if not pd.isna(gf_val):
            if gf_val >= 2: s['gf2'] += 1
            if gf_val >= 3: s['gf3'] += 1
            s['gf_sum'] += gf_val

    for i, f in enumerate(files):
        if i % 500 == 0: print(f'  处理: {i}/{len(files)}', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['柱型','日ZA','次日高幅','高幅','DXZC','DXAB','日ZC','DXCD'])
        except: continue
        if len(df) < 100: continue

        # 下日ZA作为方向判断
        next_za = df['日ZA'].shift(-1)
        next_gf = df['次日高幅'].astype(float)
        current_gf = df['高幅'].astype(float)
        # 周门条件：ZC>0 且 DXCD=上
        zc_gt0 = df['日ZC'].astype(float) > 0
        dxcd_up = df['DXCD'].astype(str) == '上'
        zhoumen = zc_gt0 & dxcd_up

        for idx in range(len(df)):
            zx = classify_zhuxing(df.iloc[idx]['柱型'])
            zx_sub = classify_zhuxing_sub(df.iloc[idx]['柱型'])
            nh = next_gf.iloc[idx]
            gf = current_gf.iloc[idx]
            dxzc = df.iloc[idx]['DXZC']
            dxab = df.iloc[idx]['DXAB']
            dzc = classify_dxzc(dxzc, dxab)

            # 基础柱型统计
            add(zx, nh, gf, dxzc, dxab)
            # 细分柱型统计
            add(zx_sub, nh, gf, dxzc, dxab)
            # 柱型 × DXZC条件
            add(f'{zx}_{dzc}', nh, gf, dxzc, dxab)
            # 栅 + 当前高幅条件
            if zx == '栅':
                if not pd.isna(gf) and gf < 2: add('栅_当日低幅<2%', nh, gf, dxzc, dxab)
                elif not pd.isna(gf) and gf >= 2: add('栅_当日高幅>=2%', nh, gf, dxzc, dxab)
            # 周门内柱型统计
            if zhoumen.iloc[idx]:
                add(f'周门_{zx}', nh, gf, dxzc, dxab)

    # 输出结果
    print(f'\n{"="*80}')
    print(f'柱型 × 下日冲高 全量验证（{len(files)}个文件）')
    print(f'{"="*80}')
    print(f'{"分类":<20} {"样本":>6} {"P(≥2%)":>8} {"P(≥3%)":>8} {"均次高幅":>8} {"均当日高幅":>8}')
    print(f'{"-"*60}')

    # 基础柱型
    for cat in ['梯','栅','枝','根','干','冠','蛀','暂','其他']:
        if cat in stats:
            s = stats[cat]
            print(f'{"【柱型】"+cat:<20} {s["n"]:>6} {s["nh2"]/s["n"]*100:>7.1f}% {s["nh3"]/s["n"]*100:>7.1f}% {s["nh_sum"]/s["n"]:>7.2f}% {s["gf_sum"]/s["n"]:>7.2f}%')

    print(f'\n{"-"*60}')
    print(f'细分柱型')
    print(f'{"-"*60}')
    for cat, s in sorted(stats.items()):
        if s['n'] < 500: continue
        if not any(c in cat for c in ['梯','栅','枝','根']): continue
        if '周门' in cat or 'ZC<' in cat or 'ZC>' in cat: continue
        if '栅_' in cat: continue
        print(f'{cat:<20} {s["n"]:>6} {s["nh2"]/s["n"]*100:>7.1f}% {s["nh3"]/s["n"]*100:>7.1f}% {s["nh_sum"]/s["n"]:>7.2f}% {s["gf_sum"]/s["n"]:>7.2f}%')

    print(f'\n{"-"*60}')
    print(f'栅 × 当日高幅条件')
    print(f'{"-"*60}')
    for cat in ['栅_当日低幅<2%', '栅_当日高幅>=2%']:
        if cat in stats:
            s = stats[cat]
            print(f'{cat:<20} {s["n"]:>6} {s["nh2"]/s["n"]*100:>7.1f}% {s["nh3"]/s["n"]*100:>7.1f}%')

    print(f'\n{"-"*60}')
    print(f'DXZC条件 × 柱型')
    print(f'{"-"*60}')
    for cat, s in sorted(stats.items()):
        if s['n'] < 300: continue
        if 'ZC>' in cat or 'ZC<' in cat:
            print(f'{cat:<25} {s["n"]:>6} {s["nh2"]/s["n"]*100:>7.1f}% {s["nh3"]/s["n"]*100:>7.1f}%')

    print(f'\n{"-"*60}')
    print(f'周门(ZC>0+DXCD=上) × 柱型')
    print(f'{"-"*60}')
    for cat, s in sorted(stats.items()):
        if s['n'] < 200: continue
        if '周门' in cat:
            print(f'{cat:<20} {s["n"]:>6} {s["nh2"]/s["n"]*100:>7.1f}% {s["nh3"]/s["n"]*100:>7.1f}%')

    # 最佳机会提示
    print(f'\n{"="*80}')
    print(f'结论：下日冲高机会/风险提示')
    print(f'{"="*80}')
    # 按P(≥2%)排序
    ranked = [(cat, s) for cat, s in stats.items() if '周门' not in cat and 'ZC' not in cat and '栅_' not in cat and s['n'] >= 500]
    ranked.sort(key=lambda x: x[1]['nh2']/x[1]['n'], reverse=True)
    print(f'\n最佳机会（P(≥2%)从高到低）：')
    for cat, s in ranked[:10]:
        print(f'  {cat:<15} P(≥2%)={s["nh2"]/s["n"]*100:.1f}%  P(≥3%)={s["nh3"]/s["n"]*100:.1f}%  样本={s["n"]}')
    print(f'\n最差风险（P(≥2%)从低到高）：')
    for cat, s in ranked[-10:]:
        print(f'  {cat:<15} P(≥2%)={s["nh2"]/s["n"]*100:.1f}%  P(≥3%)={s["nh3"]/s["n"]*100:.1f}%  样本={s["n"]}')

if __name__ == '__main__':
    main()