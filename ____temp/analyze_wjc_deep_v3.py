# -*- coding: utf-8 -*-
"""
WJC（周级别JC=月级别JA=MJA）最重要均线验证 v3
核心命题：
  ① 站上WJC=在MJA之上=升势
  ② WXZC<0时，即使WXZB>0或WXZA>0，WJC压制反弹
  ③ WJC/MJA作为趋势线区分器

关键变量理解（已纠正）：
  - 日ZC = 日类BTZC = 价格 vs 日线JC(EMA26)的交叉天数计数
  - ZC周 = 周类BTZC = WXZC = 价格 vs WJC(周EMA26)的交叉天数计数
  - ZB周 = 周类BTZB = WXZB = 价格 vs WJB(周EMA12)的交叉天数计数
  - ZA周 = 周类BTZA = WXZA = 价格 vs WJA(周EMA5)的交叉天数计数
  - WJC = 周线JC(EMA26) = MJA(月线JA(EMA5)) 同一趋势线
"""
import numpy as np, pandas as pd, os, glob, warnings
warnings.simplefilter('ignore')

DATA_DIR_DAY = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
DATA_DIR_WEEK = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组周'
OUT_DIR = r'D:\@VSwork\VS昭明计划VBA优化\____temp'

def classify_zhuxing(ct_str):
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

def extract_longzhu(bo_str):
    """从波型中提取龙猪信息"""
    if pd.isna(bo_str): return 'NA'
    s = str(bo_str)
    if '龙猪' in s: return '龙猪'
    elif '龙管' in s: return '龙管'
    elif '龙' in s: return '龙(其他)'
    elif '震' in s: return '震'
    elif '头' in s: return '头'
    elif '栅' in s: return '栅'
    return '其他波型'

def main():
    day_files = sorted(glob.glob(os.path.join(DATA_DIR_DAY, '谕组日_*.csv')))
    week_files = sorted(glob.glob(os.path.join(DATA_DIR_WEEK, '谕组周_*.csv')))
    print(f'日线文件: {len(day_files)}, 周线文件: {len(week_files)}', flush=True)

    # ====== 统计结构 ======
    class Stat:
        def __init__(self):
            self.n = 0
            self.nh2 = 0
            self.nh3 = 0
            self.nh_sum = 0.0

    def add(stats, cat, nh_val):
        if cat not in stats:
            stats[cat] = Stat()
        s = stats[cat]
        s.n += 1
        if not pd.isna(nh_val):
            if nh_val >= 2: s.nh2 += 1
            if nh_val >= 3: s.nh3 += 1
            s.nh_sum += nh_val

    # ====== 第一部分：日线数据分析（站上WJC的代理=日ZC>0）======'
    stats_day = {}
    for i, f in enumerate(day_files):
        if i % 500 == 0: print(f'  日线处理: {i}/{len(day_files)}', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk',
                             usecols=['柱型','波型','日ZA','日ZC','日ZE','次日高幅','高幅','DXCD','DXAB','盈提示','顶型'])
        except: continue
        if len(df) < 50: continue

        next_gf = df['次日高幅'].astype(float)
        zc = df['日ZC'].astype(float)

        for idx in range(len(df)):
            nh = next_gf.iloc[idx]
            zc_val = zc.iloc[idx]
            zc_gt0 = zc_val > 0  # 站上日线JC（作为站上WJC代理）
            zc_lt0 = zc_val <= 0

            zx = classify_zhuxing(df.iloc[idx]['柱型'])
            lz = extract_longzhu(df.iloc[idx]['波型'])
            dx = str(df.iloc[idx]['DXCD'])

            # 1. 基础：站上日ZC vs 之下
            if zc_gt0: add(stats_day, '【站上日ZC】日ZC>0', nh)
            else: add(stats_day, '【日ZC之下】日ZC<=0', nh)

            # 2. 日ZC值分级
            add(stats_day, f'日ZC={int(zc_val)}', nh)

            # 3. 柱型 × 站上日ZC
            if zc_gt0: add(stats_day, f'站上日ZC+{zx}', nh)
            else: add(stats_day, f'日ZC之下+{zx}', nh)

            # 4. 龙猪 × 站上日ZC
            if zc_gt0: add(stats_day, f'站上日ZC+{lz}', nh)
            else: add(stats_day, f'日ZC之下+{lz}', nh)

            # 5. DXCD × 站上日ZC
            if zc_gt0: add(stats_day, f'站上日ZC+DXCD={dx}', nh)
            else: add(stats_day, f'日ZC之下+DXCD={dx}', nh)

            # 6. 柱型+龙猪+站上日ZC
            if zc_gt0: add(stats_day, f'站上日ZC+{zx}+{lz}', nh)
            else: add(stats_day, f'日ZC之下+{zx}+{lz}', nh)

    # ====== 第二部分：周线数据分析（WXZC/WXZB/WXZA）======'
    stats_week = {}
    # 也收集周线级别"下周高幅"作为周线层级的冲高指标
    for i, f in enumerate(week_files):
        if i % 1000 == 0: print(f'  周线处理: {i}/{len(week_files)}', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk', usecols=['ZA级','ZB级','ZC级','涨幅','PR','HR','波型'])
        except: continue
        if len(df) < 20: continue

        for idx in range(len(df)):
            zc_w = float(df.iloc[idx]['ZC级']) if not pd.isna(df.iloc[idx]['ZC级']) else 0
            zb_w = float(df.iloc[idx]['ZB级']) if not pd.isna(df.iloc[idx]['ZB级']) else 0
            za_w = float(df.iloc[idx]['ZA级']) if not pd.isna(df.iloc[idx]['ZA级']) else 0
            zz = float(df.iloc[idx]['涨幅']) if not pd.isna(df.iloc[idx]['涨幅']) else 0
            hr = float(df.iloc[idx]['HR']) if not pd.isna(df.iloc[idx]['HR']) else 0

            # 周线冲高指标：HR（周最高幅）或周涨
            week_outcome = hr  # 周高幅作为冲高指标

            # 1. 站上WJC(WXZC>0) vs WXZC<=0
            if zc_w > 0: add(stats_week, '【站上WJC】WXZC>0', week_outcome)
            else: add(stats_week, '【WJC之下】WXZC<=0', week_outcome)

            # 2. WXZC<0 × WXZB>0 条件
            if zc_w <= 0 and zb_w > 0:
                add(stats_week, 'WXZC<=0_WXZB>0', week_outcome)
            if zc_w <= 0 and zb_w <= 0:
                add(stats_week, 'WXZC<=0_WXZB<=0', week_outcome)

            # 3. WXZC<0 × WXZA>0 条件
            if zc_w <= 0 and za_w > 0:
                add(stats_week, 'WXZC<=0_WXZA>0', week_outcome)
            if zc_w <= 0 and za_w <= 0:
                add(stats_week, 'WXZC<=0_WXZA<=0', week_outcome)

            # 4. WXZC<0 × WXZB>0 × WXZA>0 三重条件
            if zc_w <= 0 and zb_w > 0 and za_w > 0:
                add(stats_week, 'WXZC<=0_WXZB>0_WXZA>0', week_outcome)

            # 5. WXZC值分级
            add(stats_week, f'WXZC={int(zc_w)}', week_outcome)

            # 6. 站上WJC × 冲高表现
            if zc_w > 0:
                add(stats_week, 'WXZC>0_周涨>=0', week_outcome)
                if zz >= 0: add(stats_week, 'WXZC>0_周涨正', week_outcome)
                else: add(stats_week, 'WXZC>0_周涨负', week_outcome)
            else:
                add(stats_week, 'WXZC<=0_周涨>=0', week_outcome)
                if zz >= 0: add(stats_week, 'WXZC<=0_周涨正', week_outcome)
                else: add(stats_week, 'WXZC<=0_周涨负', week_outcome)

    # ====== 输出结果 ======
    lines = []
    def out(s=''):
        lines.append(s)
        print(s)

    def print_table(stats_dict, title, keys, cols, sample_min=500):
        """通用表格打印"""
        out(f'\n{"="*90}')
        out(title)
        out(f'{"="*90}')
        header = '  '.join(f'{c:<{cols[i]}}' for i, c in enumerate(['条件','样本','冲高率','P(≥2%)','P(≥3%)','均次高']))
        out(header)
        out(f'{"-"*80}')
        for k in keys:
            if k in stats_dict and stats_dict[k].n >= sample_min:
                s = stats_dict[k]
                out(f'{k:<{cols[0]}} {s.n:>{cols[1]}} {s.nh_sum/s.n:>{cols[2]}.2f}% {s.nh2/s.n*100:>{cols[3]}.1f}% {s.nh3/s.n*100:>{cols[4]}.1f}% {s.nh_sum/s.n:>{cols[5]}.2f}%')

    # ========== 第一部分输出 ==========
    out(f'{"="*90}')
    out(f'WJC（周级别JC=月级别JA=MJA）最重要均线验证')
    out(f'{"="*90}')
    out(f'\n日线数据：{len(day_files)}只，周线数据：{len(week_files)}只')

    # 一、站上日ZC vs 之下
    out(f'\n{"="*90}')
    out(f'一、站上日ZC（日ZC>0，作为站上WJC的日线代理）vs 日ZC之下')
    out(f'{"="*90}')
    out(f'{"条件":<30} {"样本":>8} {"冲高率":>8} {"P(≥2%)":>8} {"P(≥3%)":>8} {"均次高":>8}')
    out(f'{"-"*70}')
    for cat in ['【站上日ZC】日ZC>0', '【日ZC之下】日ZC<=0']:
        if cat in stats_day:
            s = stats_day[cat]
            out(f'{cat:<30} {s.n:>8} {s.nh_sum/max(s.n,1):>7.2f}% {s.nh2/s.n*100:>7.1f}% {s.nh3/s.n*100:>7.1f}% {s.nh_sum/s.n:>7.2f}%')

    # 二、日ZC值分级
    out(f'\n{"="*90}')
    out(f'二、日ZC值分级（正值越大=越稳站WJC之上，负值越深=越深跌破WJC）')
    out(f'{"="*90}')
    out(f'{"日ZC值":<12} {"样本":>8} {"P(≥2%)":>8} {"P(≥3%)":>8} {"均次高":>8}')
    out(f'{"-"*50}')
    zc_keys = sorted([k for k in stats_day if k.startswith('日ZC=')], key=lambda k: int(k.replace('日ZC=','')))
    for k in zc_keys:
        s = stats_day[k]
        if s.n >= 200:
            out(f'{k:<12} {s.n:>8} {s.nh2/s.n*100:>7.1f}% {s.nh3/s.n*100:>7.1f}% {s.nh_sum/s.n:>7.2f}%')

    # 三、柱型门控效应
    out(f'\n{"="*90}')
    out(f'三、WJC门控效应——各柱型在站上日ZC vs 之下的表现差')
    out(f'{"="*90}')
    out(f'{"柱型":<10} {"站上日ZC冲高":>14} {"日ZC之下冲高":>14} {"差":>8} {"站上P3":>10} {"之下P3":>10} {"P3差":>8}')
    out(f'{"-"*70}')
    for zx in ['梯','栅','枝','根','干','冠','蛀','暂']:
        up = stats_day.get(f'站上日ZC+{zx}')
        down = stats_day.get(f'日ZC之下+{zx}')
        if up and down and up.n >= 500 and down.n >= 500:
            up_r = up.nh_sum/up.n
            down_r = down.nh_sum/down.n
            up_p3 = up.nh3/up.n*100
            down_p3 = down.nh3/down.n*100
            out(f'{zx:<10} {up_r:>13.2f}% {down_r:>13.2f}% {up_r-down_r:>+7.2f}% {up_p3:>9.1f}% {down_p3:>9.1f}% {up_p3-down_p3:>+7.1f}%')

    # 四、龙猪门控效应
    out(f'\n{"="*90}')
    out(f'四、波型(龙猪) × 站上日ZC')
    out(f'{"="*90}')
    out(f'{"波型":<12} {"站上日ZC":>10} {"站上P3":>10} {"日ZC之下":>10} {"之下P3":>10} {"P3差":>8}')
    out(f'{"-"*65}')
    for lz in ['龙猪','龙管','震','头']:
        up = stats_day.get(f'站上日ZC+{lz}')
        down = stats_day.get(f'日ZC之下+{lz}')
        if up and down and up.n >= 500 and down.n >= 500:
            up_p3 = up.nh3/up.n*100
            down_p3 = down.nh3/down.n*100
            out(f'{lz:<12} {up.n:>10} {up_p3:>9.1f}% {down.n:>10} {down_p3:>9.1f}% {up_p3-down_p3:>+7.1f}%')

    # 五、最佳组合
    out(f'\n{"="*90}')
    out(f'五、站上日ZC + 柱型 + 龙猪 = 最佳组合（按P3排序）')
    out(f'{"="*90}')
    out(f'{"条件":<45} {"样本":>8} {"P(≥3%)":>8} {"均次高":>8}')
    out(f'{"-"*75}')
    combos = [(k, s) for k, s in stats_day.items() if k.startswith('站上日ZC+') and s.n >= 2000]
    combos.sort(key=lambda x: x[1].nh3/x[1].n, reverse=True)
    for k, s in combos[:15]:
        out(f'{k:<45} {s.n:>8} {s.nh3/s.n*100:>7.1f}% {s.nh_sum/s.n:>7.2f}%')

    # ========== 第二部分输出 ==========
    out(f'\n\n{"="*90}')
    out(f'第二部分：周线级别 WXZC/WXZB/WXZA 验证')
    out(f'{"="*90}')

    # 六、WXZC>0 vs WXZC<=0
    out(f'\n{"="*90}')
    out(f'六、站上WJC（WXZC>0，即ZC级>0）vs WJC之下（WXZC<=0）')
    out(f'{"="*90}')
    out(f'{"条件":<30} {"样本":>8} {"周均冲高":>8} {"P(周冲≥2%)":>12} {"P(周冲≥3%)":>12} {"均周高幅":>8}')
    out(f'{"-"*80}')
    for cat in ['【站上WJC】WXZC>0', '【WJC之下】WXZC<=0']:
        if cat in stats_week:
            s = stats_week[cat]
            out(f'{cat:<30} {s.n:>8} {s.nh_sum/max(s.n,1):>7.2f}% {s.nh2/s.n*100:>11.1f}% {s.nh3/s.n*100:>11.1f}% {s.nh_sum/s.n:>7.2f}%')

    # 七、WXZC<0 + WXZB>0/WXZA>0 条件
    out(f'\n{"="*90}')
    out(f'七、WXZC<0条件下的WXZB/WXZA区分力——验证"WJC压制反弹"')
    out(f'{"="*90}')
    out(f'{"条件":<35} {"样本":>8} {"周均冲高":>8} {"P(周冲≥2%)":>12} {"P(周冲≥3%)":>12} {"均周高幅":>8}')
    out(f'{"-"*85}')
    for cat in ['WXZC<=0_WXZB>0', 'WXZC<=0_WXZB<=0', 'WXZC<=0_WXZA>0', 'WXZC<=0_WXZA<=0', 'WXZC<=0_WXZB>0_WXZA>0']:
        if cat in stats_week:
            s = stats_week[cat]
            if s.n >= 200:
                out(f'{cat:<35} {s.n:>8} {s.nh_sum/s.n:>7.2f}% {s.nh2/s.n*100:>11.1f}% {s.nh3/s.n*100:>11.1f}% {s.nh_sum/s.n:>7.2f}%')

    # 八、WXZC值分级
    out(f'\n{"="*90}')
    out(f'八、WXZC值分级（正=站上WJC，负=跌破WJC）')
    out(f'{"="*90}')
    out(f'{"WXZC值":<12} {"样本":>8} {"P(周冲≥2%)":>12} {"P(周冲≥3%)":>12} {"均周高幅":>8}')
    out(f'{"-"*55}')
    wzc_keys = sorted([k for k in stats_week if k.startswith('WXZC=')], key=lambda k: int(k.replace('WXZC=','')))
    for k in wzc_keys:
        s = stats_week[k]
        if s.n >= 200:
            out(f'{k:<12} {s.n:>8} {s.nh2/s.n*100:>11.1f}% {s.nh3/s.n*100:>11.1f}% {s.nh_sum/s.n:>7.2f}%')

    # 九、综合结论
    out(f'\n\n{"="*90}')
    out(f'结论')
    out(f'{"="*90}')

    # 日线结论
    s_up = stats_day.get('【站上日ZC】日ZC>0')
    s_down = stats_day.get('【日ZC之下】日ZC<=0')
    if s_up and s_down:
        up_p3 = s_up.nh3/s_up.n*100
        down_p3 = s_down.nh3/s_down.n*100
        out(f'\n① 站上日ZC（作为站上WJC代理）：')
        out(f'   站上日ZC P(≥3%)={up_p3:.1f}%，样本={s_up.n:,}')
        out(f'   日ZC之下 P(≥3%)={down_p3:.1f}%，样本={s_down.n:,}')
        out(f'   差值={up_p3-down_p3:+.1f}pp，比率为{up_p3/down_p3:.2f}倍')

    # 周线结论
    s_wup = stats_week.get('【站上WJC】WXZC>0')
    s_wdown = stats_week.get('【WJC之下】WXZC<=0')
    if s_wup and s_wdown:
        wup_p3 = s_wup.nh3/s_wup.n*100
        wdown_p3 = s_wdown.nh3/s_wdown.n*100
        out(f'\n② 站上WJC（周线级别，WXZC>0）：')
        out(f'   站上WJC P(周冲≥3%)={wup_p3:.1f}%')
        out(f'   WJC之下 P(周冲≥3%)={wdown_p3:.1f}%')
        out(f'   差值={wup_p3-wdown_p3:+.1f}pp')

    # WXZC<0 + WXZB>0 结论
    s_wxzc_zb = stats_week.get('WXZC<=0_WXZB>0')
    s_wxzc_zb_0 = stats_week.get('WXZC<=0_WXZB<=0')
    if s_wxzc_zb and s_wxzc_zb_0:
        out(f'\n③ WXZC<0条件下，WXZB>0的区分力：')
        out(f'   WXZC<0 + WXZB>0 P(周冲≥3%)={s_wxzc_zb.nh3/s_wxzc_zb.n*100:.1f}%')
        out(f'   WXZC<0 + WXZB<=0 P(周冲≥3%)={s_wxzc_zb_0.nh3/s_wxzc_zb_0.n*100:.1f}%')
        out(f'   差值={s_wxzc_zb.nh3/s_wxzc_zb.n*100 - s_wxzc_zb_0.nh3/s_wxzc_zb_0.n*100:+.1f}pp')

    # 门控效应总结
    out(f'\n④ 门控效应：各柱型在站上日ZC vs 之下的P3差值')
    diffs = []
    for zx in ['梯','栅','枝','根','干','冠','蛀','暂']:
        up = stats_day.get(f'站上日ZC+{zx}')
        down = stats_day.get(f'日ZC之下+{zx}')
        if up and down and up.n >= 500 and down.n >= 500:
            diffs.append((zx, up.nh3/up.n*100 - down.nh3/down.n*100, up.nh3/up.n*100, down.nh3/down.n*100))
    diffs.sort(key=lambda x: x[1], reverse=True)
    for zx, d, up, down in diffs:
        out(f'   {zx:<10} 站上={up:.1f}% → 之下={down:.1f}%  差值={d:+.1f}pp')

    # 保存
    out_path = os.path.join(OUT_DIR, 'WJC深度分析_v3.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n结果已写入: {out_path}')

if __name__ == '__main__':
    main()