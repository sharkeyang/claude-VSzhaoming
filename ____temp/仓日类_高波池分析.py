# -*- coding: utf-8 -*-
"""
仓日类近似分析.py
==================
用谕组日CSV中已有的 DXCD(上/中/下/忐/忠/忑) + DXAB首字(甲/乙/丙/丁/戊/己)
近似代替仓日类，统计各组合的下日概率。

仓日类 = DXCD护级(1位) + DXAB护型首字(1位)，前提是日ZE>0
日ZE<=0 时统一为"无"

与真实仓日类的差异：
- 真实仓日类用护段AB（基于BTZA/BTZB/BTAB），此处用DXAB（基于日ZA/日ZB/日AB）
- 两者在大部分情况下一致，边界情况有差异
"""

import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'

# 高波池（与 MC3.3.1 一致）
高波池板块 = {'Qic', 'Qim', 'Qit'}

# DXAB首字 → 护型映射
DXAB_TO_HUXING = {
    'a': '甲', 'b': '乙', 'c': '丙',
    'r': '己', 'y': '戊', 'z': '丁',
}


class IncAgg:
    def __init__(self):
        self.n = 0
        self.sum_hr = 0.0
        self.n_p0 = 0
        self.n_p1 = 0
        self.n_p2 = 0
        self.n_p3 = 0
        self.n_p5 = 0

    def add(self, next_hr):
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


def extract_dxab_hu(x):
    """从DXAB完整字符串中提取护型首字"""
    if pd.isna(x) or str(x).strip() == '':
        return '?'
    s = str(x).strip()
    first = s[0]
    return DXAB_TO_HUXING.get(first, '?')


def main():
    t0 = time.time()
    board_map = load_board_map()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    # 聚合器
    # agg[('仓日类值',)] — 各仓日类组合
    # agg[('基线',)] — 高波池全量基线
    # agg[('无',)] — DJE之下
    # agg[('DXCD值',)] — 按DXCD分组
    # agg[('DXAB护型',)] — 按DXAB护型分组
    agg = defaultdict(IncAgg)

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

        hr = df['高幅'].astype(float).values
        next_hr = df['次日高幅'].astype(float).values
        ze = df['日ZE'].astype(float).values
        dxcd = df['DXCD'].astype(str).values
        dxab_raw = df['DXAB'].astype(str).values

        for j in range(n - 1):
            if next_hr[j] <= -99:
                continue

            # 基线
            agg[('基线',)].add(next_hr[j])

            # 仓日类近似
            if ze[j] <= 0:
                agg[('无',)].add(next_hr[j])
            else:
                cd = dxcd[j][0] if len(dxcd[j]) > 0 else '?'
                ab_hu = extract_dxab_hu(dxab_raw[j])
                key = cd + ab_hu
                agg[(key,)].add(next_hr[j])

                # 按DXCD分组
                agg[(f'CD_{cd}',)].add(next_hr[j])
                # 按DXAB护型分组
                agg[(f'AB_{ab_hu}',)].add(next_hr[j])

    print(f'  高波池: {gb_rows:,} 行', flush=True)

    # ── 输出结果 ──
    out = []
    out.append('=' * 80)
    out.append('仓日类近似分析（高波池 Qic+Qim+Qit）')
    out.append('=' * 80)
    out.append(f'高波池样本: {gb_rows:,} 行')
    out.append(f'仓日类 = DXCD首字 + DXAB护型首字（日ZE>0时），日ZE<=0时为"无"')
    out.append('')

    # 1. 基线
    b = agg[('基线',)].stats()
    out.append('【基线：高波池全量】')
    out.append(f'{"指标":<12s}  {"基线":>10s}')
    out.append('-' * 30)
    for key in ['P0', 'P1', 'P2', 'P3', 'P5', '期望HR']:
        if key == '期望HR':
            out.append(f'{key:<12s}  {b[key]:>9.2f}%')
        else:
            out.append(f'{key:<12s}  {b[key]:>9.1f}%')
    out.append('')

    # 2. 按DXCD分组
    out.append('【按DXCD分组（日ZE>0时）】')
    out.append(f'{"DXCD":<6s}  {"样本":>10s}  {"P0":>8s}  {"P1":>8s}  {"P2":>8s}  {"P3":>8s}  {"P5":>8s}  {"期望HR":>8s}')
    out.append('-' * 75)
    for cd in ['上', '中', '下', '忐', '忠', '忑']:
        s = agg[(f'CD_{cd}',)].stats()
        if s:
            out.append(f'{cd:<6s}  {s["n"]:>10,d}  {s["P0"]:>7.1f}%  {s["P1"]:>7.1f}%  {s["P2"]:>7.1f}%  {s["P3"]:>7.1f}%  {s["P5"]:>7.1f}%  {s["期望HR"]:>7.2f}%')
    out.append('')

    # 3. 按DXAB护型分组
    out.append('【按DXAB护型分组（日ZE>0时）】')
    out.append(f'{"护型":<6s}  {"样本":>10s}  {"P0":>8s}  {"P1":>8s}  {"P2":>8s}  {"P3":>8s}  {"P5":>8s}  {"期望HR":>8s}')
    out.append('-' * 75)
    for hu in ['甲', '乙', '丙', '丁', '戊', '己']:
        s = agg[(f'AB_{hu}',)].stats()
        if s:
            out.append(f'{hu:<6s}  {s["n"]:>10,d}  {s["P0"]:>7.1f}%  {s["P1"]:>7.1f}%  {s["P2"]:>7.1f}%  {s["P3"]:>7.1f}%  {s["P5"]:>7.1f}%  {s["期望HR"]:>7.2f}%')
    out.append('')

    # 4. 仓日类全组合（按期望HR排序）
    out.append('【仓日类全组合（日ZE>0时，按期望HR降序）】')
    out.append(f'{"仓日类":<8s}  {"样本":>10s}  {"P0":>8s}  {"P1":>8s}  {"P2":>8s}  {"P3":>8s}  {"P5":>8s}  {"期望HR":>8s}')
    out.append('-' * 80)

    # 收集所有组合
    combos = []
    for key, a in agg.items():
        if len(key) == 1 and key[0] not in ('基线', '无') and not key[0].startswith('CD_') and not key[0].startswith('AB_'):
            s = a.stats()
            if s and s['n'] >= 100:  # 过滤小样本
                combos.append((key[0], s))

    combos.sort(key=lambda x: x[1]['期望HR'], reverse=True)

    for code, s in combos:
        out.append(f'{code:<8s}  {s["n"]:>10,d}  {s["P0"]:>7.1f}%  {s["P1"]:>7.1f}%  {s["P2"]:>7.1f}%  {s["P3"]:>7.1f}%  {s["P5"]:>7.1f}%  {s["期望HR"]:>7.2f}%')
    out.append('')

    # 5. "无"（DJE之下）
    s = agg[('无',)].stats()
    out.append('【"无"（日ZE<=0，DJE之下）】')
    out.append(f'{"指标":<12s}  {"无":>10s}')
    out.append('-' * 30)
    for key in ['P0', 'P1', 'P2', 'P3', 'P5', '期望HR']:
        if key == '期望HR':
            out.append(f'{key:<12s}  {s[key]:>9.2f}%')
        else:
            out.append(f'{key:<12s}  {s[key]:>9.1f}%')
    out.append('')

    # 6. 仓日类 vs 基线 对比（关键组合）
    out.append('【仓日类 vs 基线 对比（关键组合）】')
    out.append(f'{"仓日类":<8s}  {"样本":>10s}  {"P3":>8s}  {"P3差异":>8s}  {"期望HR":>8s}  {"HR差异":>8s}')
    out.append('-' * 65)
    for code, s in combos[:15]:  # 前15个
        p3_diff = s['P3'] - b['P3']
        hr_diff = s['期望HR'] - b['期望HR']
        out.append(f'{code:<8s}  {s["n"]:>10,d}  {s["P3"]:>7.1f}%  {p3_diff:>+7.1f}pp  {s["期望HR"]:>7.2f}%  {hr_diff:>+7.2f}pp')
    out.append('')

    # 7. 底部组合（最差的）
    out.append('【仓日类底部组合（期望HR最低，按升序）】')
    out.append(f'{"仓日类":<8s}  {"样本":>10s}  {"P3":>8s}  {"P3差异":>8s}  {"期望HR":>8s}  {"HR差异":>8s}')
    out.append('-' * 65)
    for code, s in reversed(combos[-10:]):
        p3_diff = s['P3'] - b['P3']
        hr_diff = s['期望HR'] - b['期望HR']
        out.append(f'{code:<8s}  {s["n"]:>10,d}  {s["P3"]:>7.1f}%  {p3_diff:>+7.1f}pp  {s["期望HR"]:>7.2f}%  {hr_diff:>+7.2f}pp')
    out.append('')

    result = '\n'.join(out)
    print(result)

    out_path = '____temp/仓日类_高波池结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()