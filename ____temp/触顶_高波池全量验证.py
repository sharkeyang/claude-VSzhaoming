# -*- coding: utf-8 -*-
"""
触顶_高波池全量验证.py
======================
用高波池数据（Qic+Qim+Qit）重新计算 MC3.3.5 日级别触顶研究的所有统计表。
数据将用于替代 MC3.3.2 §6.3 触顶 的内容。

指标定义：
- P3 = 下日高幅（次日高幅）>= 3% 的概率
- 期望HR = 下日高幅的平均值
- 触顶 = 上符串末位为 'A'（今天创新高）
- 触哼 = 上符串末位为 'B'（触到哼JA）
- 强触顶 = BSHA>=5 且 触顶
- 合顶天数 = 连续触顶天数（从上符串中从右往左数连续A的个数）
"""
import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'

# 高波池定义（与 MC3.3.2 §2.2.1 一致：Qic+Qim+Qit）
高波池板块 = {'Qic', 'Qim', 'Qit'}


class IncAgg:
    """增量聚合器"""
    def __init__(self):
        self.n = 0
        self.sum_hr = 0.0
        self.n_p0 = 0
        self.n_p1 = 0
        self.n_p2 = 0
        self.n_p3 = 0
        self.n_p5 = 0
        self.sum_future = 0.0  # 未来N天累计收益（用于合顶周期分析）
        self.n_future = 0

    def add(self, next_hr):
        self.n += 1
        self.sum_hr += next_hr
        if next_hr >= 0: self.n_p0 += 1
        if next_hr >= 1: self.n_p1 += 1
        if next_hr >= 2: self.n_p2 += 1
        if next_hr >= 3: self.n_p3 += 1
        if next_hr >= 5: self.n_p5 += 1

    def add_future(self, future_ret):
        """添加未来N天累计收益"""
        self.n_future += 1
        self.sum_future += future_ret

    def stats(self):
        if self.n == 0:
            return None
        return {
            'n': self.n,
            'P0': self.n_p0 / self.n * 100,
            'P1': self.n_p1 / self.n * 100,
            'P2': self.n_p2 / self.n * 100,
            'P3': self.n_p3 / self.n * 100,
            'P5': self.n_p5 / self.n * 100,
            '期望HR': self.sum_hr / self.n,
        }

    def future_stats(self):
        if self.n_future == 0:
            return None
        return {
            'n': self.n_future,
            '均收益': self.sum_future / self.n_future * 100,
        }


def calc_等高线(za, zhongfu_str):
    """根据日ZA和中符串末位计算等高线（等1-等7）"""
    if za > 0:
        if za == 1:
            return '等1'
        mw = zhongfu_str[-1] if len(zhongfu_str) > 0 else ''
        if mw in ('A', 'B'):
            return '等3'
        else:
            return '等2'
    elif za < 0:
        if za == -1:
            return '等5'
        mw = zhongfu_str[-1] if len(zhongfu_str) > 0 else ''
        if mw in ('A', 'B', 'C', 'D'):
            return '等6'
        else:
            return '等7'
    else:
        return '等4' 


def calc_合顶天数(shangfu_str):
    """计算合顶天数（从上符串末位开始往左数连续A的个数）"""
    if not shangfu_str or len(shangfu_str) == 0:
        return 0
    count = 0
    for ch in reversed(shangfu_str):
        if ch == 'A':
            count += 1
        else:
            break
    return count


def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    t0 = time.time()
    board_map = load_board_map()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    # ── 聚合器 ──
    # 1. ZC方向×触顶状态
    agg_zc_touch = defaultdict(IncAgg)
    # 2. 触顶频率（ZC>0范围内）
    agg_freq = defaultdict(IncAgg)
    # 3. 合顶天数
    agg_合顶 = defaultdict(IncAgg)
    # 4. 触顶+宽哼JC
    agg_宽哼 = defaultdict(IncAgg)
    # 5. 触顶+顶型
    agg_顶型 = defaultdict(IncAgg)
    # 6. 触顶+BSHA
    agg_bsha = defaultdict(IncAgg)
    # 7. 触顶+叠幅
    agg_叠幅 = defaultdict(IncAgg)
    # 8. 触顶+等高线
    agg_等高线 = defaultdict(IncAgg)
    # 9. 合顶中断
    agg_中断 = defaultdict(IncAgg)
    # 10. 明天是否触顶
    agg_明天触顶 = defaultdict(IncAgg)
    # 11. 触顶 vs 日策略P2/日层段
    agg_p2 = defaultdict(IncAgg)
    # 12. 合顶周期（未来N天累计收益）
    agg_合顶周期 = defaultdict(IncAgg)
    agg_合顶周期_p3 = defaultdict(IncAgg)
    # 13. 合顶×BSHA交叉
    agg_合顶_bsha = defaultdict(IncAgg)

    # 触顶计数（用于"明天是否触顶"）
    touch_today_count = 0
    touch_tomorrow_count = 0

    total_rows = 0
    gb_rows = 0

    for i, f in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) < 6:  # 需要至少6行才能算未来5天
                continue
        except Exception:
            continue

        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        is_gb = board in 高波池板块
        if not is_gb:
            continue

        n = len(df)
        total_rows += n
        gb_rows += n

        # 提取列
        pr = df['涨幅'].astype(float).values
        hr = df['高幅'].astype(float).values
        next_hr = df['次日高幅'].astype(float).values
        za = df['日ZA'].astype(float).values
        zc = df['日ZC'].astype(float).values
        ze = df['日ZE'].astype(float).values
        duan = df['日段'].astype(str).values
        bsha = df['BSHA'].astype(float).values
        shangfu = df['上符串'].astype(str).values
        zhongfu = df['中符串'].astype(str).values
        dingxing = df['顶型'].astype(str).values
        kuanheng = df['宽哼JC'].astype(float).values
        die_fu = df['叠幅'].astype(float).values
        shangshen = df['上身'].astype(float).values

        for j in range(n - 1):
            if next_hr[j] <= -99:
                continue

            nhr = next_hr[j]
            zc_val = zc[j]
            za_val = za[j]
            ze_val = ze[j]
            bsha_val = bsha[j]
            sf = shangfu[j]
            zf = zhongfu[j]
            dx = dingxing[j]
            kh = kuanheng[j]
            df_val = die_fu[j]
            d = duan[j]

            # 触顶判断
            is_touch = len(sf) > 0 and sf[-1] == 'A'
            is_touch_b = len(sf) > 0 and sf[-1] == 'B'
            is_strong_touch = is_touch and bsha_val >= 5

            # 合顶天数
            合顶 = calc_合顶天数(sf)

            # 等高线
            等线 = calc_等高线(za_val, zf)

            # ── 1. ZC方向×触顶状态 ──
            if zc_val > 0:
                if is_touch:
                    agg_zc_touch[('ZC>0+触顶',)].add(nhr)
                elif is_touch_b:
                    agg_zc_touch[('ZC>0+触哼',)].add(nhr)
                else:
                    agg_zc_touch[('ZC>0+无',)].add(nhr)
            else:
                if is_touch:
                    agg_zc_touch[('ZC<=0+触顶',)].add(nhr)
                elif is_touch_b:
                    agg_zc_touch[('ZC<=0+触哼',)].add(nhr)
                else:
                    agg_zc_touch[('ZC<=0+无',)].add(nhr)

            # ── 2. 触顶频率（ZC>0范围内） ──
            if zc_val > 0:
                if is_touch:
                    # 计算5天中触顶次数
                    touch_count_5 = sum(1 for ch in sf[-5:] if ch == 'A') if len(sf) >= 5 else sum(1 for ch in sf if ch == 'A')
                    if touch_count_5 >= 5:
                        agg_freq[('ZC>0+5天全触顶',)].add(nhr)
                    elif touch_count_5 >= 4:
                        agg_freq[('ZC>0+5天>=4次',)].add(nhr)
                    elif touch_count_5 >= 3:
                        agg_freq[('ZC>0+5天>=3次',)].add(nhr)
                    elif touch_count_5 == 1:
                        agg_freq[('ZC>0+5天仅1次',)].add(nhr)
                    agg_freq[('ZC>0+今天触顶',)].add(nhr)
                else:
                    agg_freq[('ZC>0+今天未触顶',)].add(nhr)

                # 连续触顶 vs 中断后触顶
                if is_touch:
                    yesterday_touch = len(sf) > 1 and sf[-2] == 'A'
                    if yesterday_touch:
                        agg_freq[('ZC>0+连续触顶',)].add(nhr)
                    else:
                        agg_freq[('ZC>0+中断后触顶',)].add(nhr)

            # ── 3. 合顶天数 ──
            agg_合顶[(合顶,)].add(nhr)
            if zc_val > 0:
                agg_合顶[('ZC>0', 合顶)].add(nhr)

            # ── 4. 触顶+宽哼JC（ZC>0+触顶） ──
            if zc_val > 0 and is_touch and not np.isnan(kh):
                if kh < 5:
                    agg_宽哼[('kh<5',)].add(nhr)
                elif kh < 20:
                    agg_宽哼[('kh5~20',)].add(nhr)
                else:
                    agg_宽哼[('kh>=20',)].add(nhr)

            # ── 5. 触顶+顶型（ZC>0+触顶） ──
            if zc_val > 0 and is_touch:
                if '龙' in dx:
                    agg_顶型[('a龙',)].add(nhr)
                else:
                    agg_顶型[('非龙',)].add(nhr)

            # ── 6. 触顶+BSHA（ZC>0+触顶） ──
            if zc_val > 0 and is_touch and not np.isnan(bsha_val):
                if bsha_val < 1:
                    agg_bsha[('BSHA0~1',)].add(nhr)
                elif bsha_val < 2:
                    agg_bsha[('BSHA1~2',)].add(nhr)
                elif bsha_val < 3:
                    agg_bsha[('BSHA2~3',)].add(nhr)
                elif bsha_val < 5:
                    agg_bsha[('BSHA3~5',)].add(nhr)
                elif bsha_val < 10:
                    agg_bsha[('BSHA5~10',)].add(nhr)
                else:
                    agg_bsha[('BSHA>=10',)].add(nhr)

            # ── 7. 触顶+叠幅（ZC>0+触顶） ──
            if zc_val > 0 and is_touch and not np.isnan(df_val):
                if df_val < 0:
                    agg_叠幅[('叠幅<0',)].add(nhr)
                elif df_val < 3:
                    agg_叠幅[('叠幅0~3',)].add(nhr)
                elif df_val < 5:
                    agg_叠幅[('叠幅3~5',)].add(nhr)
                elif df_val < 10:
                    agg_叠幅[('叠幅5~10',)].add(nhr)
                else:
                    agg_叠幅[('叠幅>=10',)].add(nhr)

            # ── 8. 触顶+等高线（ZC>0+触顶） ──
            if zc_val > 0 and is_touch:
                agg_等高线[(等线,)].add(nhr)

            # ── 9. 合顶中断后的走势（ZC>0） ──
            if zc_val > 0:
                yesterday_touch = len(sf) > 1 and sf[-2] == 'A'
                if yesterday_touch and not is_touch:
                    # 合顶中断
                    die_fu_val = pr[j]  # 用涨幅代替跌幅
                    if not np.isnan(die_fu_val):
                        if die_fu_val < -3:
                            agg_中断[('中断+跌幅>3%',)].add(nhr)
                        elif die_fu_val < -1:
                            agg_中断[('中断+跌幅1~3%',)].add(nhr)
                        elif die_fu_val < 0:
                            agg_中断[('中断+跌幅0~1%',)].add(nhr)
                        else:
                            agg_中断[('中断+上涨',)].add(nhr)

            # ── 10. 明天是否触顶 ──
            if is_touch:
                touch_today_count += 1
                # 检查明天是否触顶（下一行的上符串）
                if j + 1 < n - 1:
                    sf_next = shangfu[j + 1]
                    tomorrow_touch = len(sf_next) > 0 and sf_next[-1] == 'A'
                    if tomorrow_touch:
                        touch_tomorrow_count += 1
                    # 按宽哼JC分组统计（用单独的计数器）
                    if not np.isnan(kh):
                        if kh < 5:
                            agg_明天触顶[('kh<5',)].n += 1
                            if tomorrow_touch:
                                agg_明天触顶[('kh<5',)].n_p0 += 1
                        elif kh < 20:
                            agg_明天触顶[('kh5~20',)].n += 1
                            if tomorrow_touch:
                                agg_明天触顶[('kh5~20',)].n_p0 += 1
                        else:
                            agg_明天触顶[('kh>=20',)].n += 1
                            if tomorrow_touch:
                                agg_明天触顶[('kh>=20',)].n_p0 += 1

            # ── 11. 触顶 vs 日策略P2/日层段 ──
            if zc_val > 0 and is_touch:
                # 等高线×BSHA×触顶
                if bsha_val >= 5:
                    agg_p2[(等线, '偏5', '触顶')].add(nhr)
                # 日层段
                if d in ('持主', '持被', '卖浮'):
                    if is_strong_touch:
                        agg_p2[(d, '强触顶')].add(nhr)
                    if is_touch:
                        agg_p2[(d, '触顶')].add(nhr)
                    else:
                        agg_p2[(d, '未触顶')].add(nhr)

            # ── 12. 合顶周期（未来N天累计收益） ──
            if 合顶 >= 1:
                # 未来1天
                f1 = pr[j+1] if j+1 < n else 0
                agg_合顶周期[(合顶, 1)].add_future(f1)
                # 未来3天
                f3 = sum(pr[j+1:min(j+4, n)])
                agg_合顶周期[(合顶, 3)].add_future(f3)
                # 未来5天
                f5 = sum(pr[j+1:min(j+6, n)])
                agg_合顶周期[(合顶, 5)].add_future(f5)
                # 未来10天
                f10 = sum(pr[j+1:min(j+11, n)])
                agg_合顶周期[(合顶, 10)].add_future(f10)
                # 未来20天
                f20 = sum(pr[j+1:min(j+21, n)])
                agg_合顶周期[(合顶, 20)].add_future(f20)

                # 未来N天冲高>=3%概率（用下日高幅）
                for days, label in [(1, 1), (3, 3), (5, 5), (10, 10)]:
                    end = min(j+1+days, n)
                    max_nhr = max(next_hr[j+1:end]) if end > j+1 else 0
                    agg_合顶周期_p3[(合顶, label)].n += 1
                    if max_nhr >= 3:
                        agg_合顶周期_p3[(合顶, label)].n_p0 += 1

            # ── 13. 合顶×BSHA交叉 ──
            if zc_val > 0 and 合顶 >= 1:
                f5_local = sum(pr[j+1:min(j+6, n)])
                if bsha_val >= 5:
                    agg_合顶_bsha[('偏5', 合顶)].add_future(f5_local)
                elif bsha_val >= 3:
                    agg_合顶_bsha[('偏3', 合顶)].add_future(f5_local)
                else:
                    agg_合顶_bsha[('非偏', 合顶)].add_future(f5_local)

    print(f'  高波池: {gb_rows:,} 行', flush=True)

    # ── 输出结果 ──
    out = []
    out.append('=' * 80)
    out.append('触顶高波池全量验证（Qic+Qim+Qit）')
    out.append('=' * 80)
    out.append(f'高波池样本: {gb_rows:,} 行')
    out.append('')

    # 1. ZC方向×触顶状态
    out.append('【1. ZC方向×触顶状态 核心模型】')
    out.append(f'{"条件":<20s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 45)
    for key in ['ZC>0+触顶', 'ZC>0+触哼', 'ZC>0+无', 'ZC<=0+触顶', 'ZC<=0+触哼', 'ZC<=0+无']:
        s = agg_zc_touch[(key,)].stats()
        if s:
            out.append(f'{key:<20s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 2. 触顶频率
    out.append('【2. 触顶频率（ZC>0范围内）】')
    out.append(f'{"条件":<30s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 50)
    for key in ['ZC>0+今天未触顶', 'ZC>0+今天触顶', 'ZC>0+5天仅1次', 'ZC>0+5天>=3次', 'ZC>0+5天>=4次', 'ZC>0+5天全触顶']:
        s = agg_freq[(key,)].stats()
        if s:
            out.append(f'{key:<30s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')
    out.append(f'{"连续触顶 vs 中断后触顶":<30s}')
    for key in ['ZC>0+中断后触顶', 'ZC>0+连续触顶']:
        s = agg_freq[(key,)].stats()
        if s:
            out.append(f'  {key:<28s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 3. 合顶天数
    out.append('【3. 合顶天数】')
    out.append(f'{"合顶天数":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for d in range(0, 6):
        s = agg_合顶[(d,)].stats()
        if s:
            out.append(f'{d}天{"":<8s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')
    out.append(f'{"合顶天数×ZC>0":<20s}')
    for d in range(0, 6):
        s = agg_合顶[('ZC>0', d)].stats()
        if s:
            out.append(f'  ZC>0+{d}天{"":<10s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 4. 触顶+宽哼JC
    out.append('【4. 触顶+宽哼JC（ZC>0+触顶）】')
    out.append(f'{"宽哼JC":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for key in ['kh<5', 'kh5~20', 'kh>=20']:
        s = agg_宽哼[(key,)].stats()
        if s:
            out.append(f'{key:<12s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 5. 触顶+顶型
    out.append('【5. 触顶+顶型（ZC>0+触顶）】')
    out.append(f'{"顶型":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for key in ['a龙', '非龙']:
        s = agg_顶型[(key,)].stats()
        if s:
            out.append(f'{key:<12s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 6. 触顶+BSHA
    out.append('【6. 触顶+BSHA（ZC>0+触顶）】')
    out.append(f'{"BSHA":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for key in ['BSHA0~1', 'BSHA1~2', 'BSHA2~3', 'BSHA3~5', 'BSHA5~10', 'BSHA>=10']:
        s = agg_bsha[(key,)].stats()
        if s:
            out.append(f'{key:<12s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 7. 触顶+叠幅
    out.append('【7. 触顶+叠幅（ZC>0+触顶）】')
    out.append(f'{"叠幅":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for key in ['叠幅<0', '叠幅0~3', '叠幅3~5', '叠幅5~10', '叠幅>=10']:
        s = agg_叠幅[(key,)].stats()
        if s:
            out.append(f'{key:<12s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 8. 触顶+等高线
    out.append('【8. 触顶+等高线（ZC>0+触顶）】')
    out.append(f'{"等高线":<12s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 35)
    for key in ['等1', '等2', '等3', '等5', '等6', '等7']:
        s = agg_等高线[(key,)].stats()
        if s:
            out.append(f'{key:<12s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 9. 合顶中断
    out.append('【9. 合顶中断后的走势（ZC>0）】')
    out.append(f'{"条件":<20s}  {"P3":>8s}  {"样本":>10s}')
    out.append('-' * 45)
    for key in ['中断+跌幅>3%', '中断+跌幅1~3%', '中断+跌幅0~1%', '中断+上涨']:
        s = agg_中断[(key,)].stats()
        if s:
            out.append(f'{key:<20s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 10. 明天是否触顶
    out.append('【10. 触顶后次日是否还能触顶】')
    if touch_today_count > 0:
        out.append(f'今天触顶→明天也触顶: {touch_tomorrow_count}/{touch_today_count} = {touch_tomorrow_count/touch_today_count*100:.1f}%')
    out.append(f'{"宽哼JC":<12s}  {"明天触顶概率":>12s}')
    out.append('-' * 30)
    for key in ['kh<5', 'kh5~20', 'kh>=20']:
        s = agg_明天触顶[(key,)]
        if s and s.n > 0:
            out.append(f'{key:<12s}  {s.n_p0/s.n*100:>11.1f}%')
    out.append('')

    # 11. 触顶 vs 日策略P2/日层段
    out.append('【11. 触顶 vs 日策略P2/日层段】')
    out.append('--- 等高线×BSHA×触顶 ---')
    out.append(f'{"条件":<30s}  {"P3":>8s}  {"样本":>10s}')
    for key in ['等1', '等2', '等3']:
        for bsha_label in ['偏5']:
            s = agg_p2[(key, bsha_label, '触顶')].stats()
            if s:
                out.append(f'{key}+{bsha_label}+触顶{"":<10s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')
    out.append('--- 日层段 ---')
    out.append(f'{"条件":<30s}  {"P3":>8s}  {"样本":>10s}')
    for d in ['持主', '持被', '卖浮']:
        for t in ['强触顶', '触顶', '未触顶']:
            s = agg_p2[(d, t)].stats()
            if s:
                out.append(f'{d}+{t}{"":<15s}  {s["P3"]:>7.1f}%  {s["n"]:>10,d}')
    out.append('')

    # 12. 合顶周期
    out.append('【12. 合顶周期（趋势延续）】')
    out.append(f'{"合顶天数":<10s}  {"未来1天":>8s}  {"未来3天":>8s}  {"未来5天":>8s}  {"未来10天":>8s}  {"未来20天":>8s}')
    out.append('-' * 55)
    for d in range(1, 6):
        row = [f'{d}天']
        for days in [1, 3, 5, 10, 20]:
            s = agg_合顶周期[(d, days)].future_stats()
            if s:
                row.append(f'{s["均收益"]:>7.2f}%')
            else:
                row.append(f'{"-":>8s}')
        out.append('  '.join(row))
    out.append('')
    out.append('--- 未来N天冲高>=3%概率 ---')
    out.append(f'{"合顶天数":<10s}  {"未来1天":>8s}  {"未来3天":>8s}  {"未来5天":>8s}  {"未来10天":>8s}')
    out.append('-' * 50)
    for d in range(1, 6):
        row = [f'{d}天']
        for days in [1, 3, 5, 10]:
            s = agg_合顶周期_p3[(d, days)]
            if s and s.n > 0:
                row.append(f'{s.n_p0/s.n*100:>7.1f}%')
            else:
                row.append(f'{"-":>8s}')
        out.append('  '.join(row))
    out.append('')

    # 13. 合顶×BSHA交叉
    out.append('【13. 合顶×BSHA交叉验证】')
    out.append('--- 偏5（BSHA>=5）条件下 ---')
    out.append(f'{"合顶天数":<10s}  {"未来5天":>8s}')
    for d in range(1, 6):
        s = agg_合顶_bsha[('偏5', d)].future_stats()
        if s:
            out.append(f'{d}天{"":<6s}  {s["均收益"]:>7.2f}%')
    out.append('')
    out.append('--- 偏3（BSHA3~5）条件下 ---')
    for d in range(1, 6):
        s = agg_合顶_bsha[('偏3', d)].future_stats()
        if s:
            out.append(f'{d}天{"":<6s}  {s["均收益"]:>7.2f}%')
    out.append('')
    out.append('--- 非偏（BSHA<3）条件下 ---')
    for d in range(1, 6):
        s = agg_合顶_bsha[('非偏', d)].future_stats()
        if s:
            out.append(f'{d}天{"":<6s}  {s["均收益"]:>7.2f}%')
    out.append('')

    result = '\n'.join(out)
    print(result)

    out_path = '____temp/触顶_高波池结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()