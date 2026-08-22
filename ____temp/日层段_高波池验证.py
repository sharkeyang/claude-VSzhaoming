# -*- coding: utf-8 -*-
"""
日层段_高波池验证.py
====================
用高波池数据（Qic+Qim+Qit+Qin，与 MC3.3.1 口径一致）重新计算
MC3.3.1 §2.6 日层段细分（持主/持被/卖浮）的所有统计表。

对应原 MC3.3.5 §十三 的验证，但数据口径从"抽样500文件/150万行"
统一为"高波池全量"。

指标定义：
- 下日P0/P1/P2/P3/P5 = 下日高幅（次日高幅）>= 0/1/2/3/5% 的概率
- 期望HR = 下日高幅的平均值
- 触顶 = 上符串末位为 'A'（今天创新高）
- 强触顶 = BSHA>=5 且 触顶
"""
import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'

# 高波池定义（与 MC3.3.1 一致：Qic+Qim+Qit+Qin）
高波池板块 = {'Qic', 'Qim', 'Qit', 'Qin'}


class IncAgg:
    """增量聚合：边读边算，不保留原始数据"""
    def __init__(self):
        self.n = 0
        self.sum_hr = 0.0
        self.n_p0 = 0  # 下日高幅>=0
        self.n_p1 = 0  # >=1%
        self.n_p2 = 0  # >=2%
        self.n_p3 = 0  # >=3%
        self.n_p5 = 0  # >=5%

    def add(self, next_hr):
        """next_hr=下日高幅（已排除-100）"""
        self.n += 1
        self.sum_hr += next_hr
        if next_hr >= 0: self.n_p0 += 1
        if next_hr >= 1: self.n_p1 += 1
        if next_hr >= 2: self.n_p2 += 1
        if next_hr >= 3: self.n_p3 += 1
        if next_hr >= 5: self.n_p5 += 1

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


def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    t0 = time.time()
    board_map = load_board_map()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    # 聚合器
    # agg_gb[日段] — 高波池各日段
    # agg_gb[('基线',)] — 高波池全量基线
    # agg_gb[('持主强触顶',)] — 持主+BSHA>=5+触顶
    # agg_gb[('持主触顶',)] — 持主+触顶
    # agg_gb[('持主未触顶',)] — 持主+未触顶
    # agg_gb[('卖浮触顶',)] — 卖浮+触顶
    # agg_gb[('卖浮未触顶',)] — 卖浮+未触顶
    agg = defaultdict(IncAgg)

    # 三线条件一致性统计
    # cond_count[(日段)] 和 cond_count[(理论条件)] 用于 §13.2
    cond_count = defaultdict(int)

    total_rows = 0
    gb_rows = 0

    for i, f in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) < 2:
                continue
        except Exception:
            continue

        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        is_gb = board in 高波池板块

        n = len(df)
        total_rows += n
        if not is_gb:
            continue
        gb_rows += n

        # 提取列
        pr = df['涨幅'].astype(float).values
        hr = df['高幅'].astype(float).values
        next_pr = df['涨幅'].astype(float).values  # 下日涨幅（shift后）
        next_hr = df['次日高幅'].astype(float).values
        za = df['日ZA'].astype(float).values
        zc = df['日ZC'].astype(float).values
        ze = df['日ZE'].astype(float).values
        duan = df['日段'].astype(str).values
        bsha = df['BSHA'].astype(float).values
        shangfu = df['上符串'].astype(str).values

        for j in range(n - 1):  # 最后一行没有下日数据
            # 排除无效数据
            if next_hr[j] <= -99:
                continue

            d = duan[j]
            # 三线条件一致性
            if ze[j] > 0 and zc[j] > 0 and za[j] > 0:
                cond_count['ZE>0+ZC>0+ZA>0'] += 1
            if ze[j] > 0 and zc[j] > 0 and za[j] <= 0:
                cond_count['ZE>0+ZC>0+ZA<=0'] += 1
            if ze[j] > 0 and zc[j] <= 0:
                cond_count['ZE>0+ZC<=0'] += 1
            if d in ('持主', '持被', '卖浮'):
                cond_count[d] += 1

            # 基线（高波池全量）
            agg[('基线',)].add(next_hr[j])

            # 各日段
            if d in ('持主', '持被', '卖浮'):
                agg[(d,)].add(next_hr[j])

            # 触顶判断：上符串末位为 'A'
            is_touch = len(shangfu[j]) > 0 and shangfu[j][-1] == 'A'
            is_strong_touch = is_touch and bsha[j] >= 5

            if d == '持主':
                if is_strong_touch:
                    agg[('持主强触顶',)].add(next_hr[j])
                if is_touch:
                    agg[('持主触顶',)].add(next_hr[j])
                else:
                    agg[('持主未触顶',)].add(next_hr[j])
            elif d == '卖浮':
                if is_touch:
                    agg[('卖浮触顶',)].add(next_hr[j])
                else:
                    agg[('卖浮未触顶',)].add(next_hr[j])

    print(f'  高波池: {gb_rows} 行', flush=True)

    # ── 输出结果 ──────────────────────────────
    out = []
    out.append('=' * 80)
    out.append('日层段高波池验证（Qic+Qim+Qit+Qin）')
    out.append('=' * 80)
    out.append(f'高波池样本: {gb_rows:,} 行')
    out.append('')

    # §13.2 三线条件一致性
    out.append('【§2.6.2 日层段 vs 三线条件一致性】')
    out.append(f'{"理论条件":<20s}  {"日段":<6s}  {"样本":>10s}')
    out.append('-' * 45)
    for cond, label in [
        ('ZE>0+ZC>0+ZA>0', '持主'),
        ('ZE>0+ZC>0+ZA<=0', '持被'),
        ('ZE>0+ZC<=0', '卖浮'),
    ]:
        c = cond_count.get(cond, 0)
        d = cond_count.get(label, 0)
        out.append(f'{cond:<20s}  {label:<6s}  {c:>10,d}  (日段{d:>10,d})')
    out.append('')

    # §13.3 持主是否必赢
    out.append('【§2.6.3 持主是否必赢】')
    out.append(f'{"指标":<12s}  {"持主":>10s}  {"基线":>10s}')
    out.append('-' * 40)
    for key in ['P0', 'P1', 'P2', 'P3', 'P5', '期望HR']:
        z = agg[('持主',)].stats()
        b = agg[('基线',)].stats()
        if key == '期望HR':
            out.append(f'{key:<12s}  {z[key]:>9.2f}%  {b[key]:>9.2f}%')
        else:
            out.append(f'{key:<12s}  {z[key]:>9.1f}%  {b[key]:>9.1f}%')
    out.append('')

    # §13.4 持主+强触顶
    out.append('【§2.6.4 持主+强触顶 是否必赢】')
    s = agg[('持主强触顶',)].stats()
    out.append(f'{"指标":<12s}  {"持主+BSHA>=5+触顶":>20s}')
    out.append('-' * 40)
    for key in ['P0', 'P1', 'P2', 'P3', 'P5', '期望HR']:
        if key == '期望HR':
            out.append(f'{key:<12s}  {s[key]:>19.2f}%')
        else:
            out.append(f'{key:<12s}  {s[key]:>19.1f}%')
    out.append('')

    # §13.5 持主 vs 卖浮
    out.append('【§2.6.5 持主 vs 卖浮】')
    out.append(f'{"指标":<12s}  {"持主":>10s}  {"卖浮":>10s}')
    out.append('-' * 40)
    z = agg[('持主',)].stats()
    m = agg[('卖浮',)].stats()
    for key in ['P0', 'P3', '期望HR']:
        if key == '期望HR':
            out.append(f'{key:<12s}  {z[key]:>9.2f}%  {m[key]:>9.2f}%')
        else:
            out.append(f'{key:<12s}  {z[key]:>9.1f}%  {m[key]:>9.1f}%')
    out.append('')

    # 补充：持主触顶 vs 未触顶（供 §12 参考）
    out.append('【补充：持主触顶 vs 未触顶】')
    out.append(f'{"指标":<12s}  {"持主触顶":>10s}  {"持主未触顶":>12s}')
    out.append('-' * 40)
    t = agg[('持主触顶',)].stats()
    nt = agg[('持主未触顶',)].stats()
    for key in ['P3', '期望HR']:
        if key == '期望HR':
            out.append(f'{key:<12s}  {t[key]:>9.2f}%  {nt[key]:>11.2f}%')
        else:
            out.append(f'{key:<12s}  {t[key]:>9.1f}%  {nt[key]:>11.1f}%')
    out.append('')

    result = '\n'.join(out)
    print(result)

    out_path = '____temp/日层段_高波池结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()