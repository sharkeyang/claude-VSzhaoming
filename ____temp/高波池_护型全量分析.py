# -*- coding: utf-8 -*-
"""
高波池_护型全量分析.py (v2 — 增量聚合版)
========================================
用高波池数据（Qic+Qim+Qit）重新计算 MC3.3.4 文档中的所有统计表，
并与全量数据对比，标注差异较大的项。

v2 改进：边读文件边聚合，不保留全量数据，大幅降低内存和I/O开销。
"""
import numpy as np, pandas as pd, os, glob, time, json, warnings, sys
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 1000

# 高波池定义
高波池板块 = {'Qic', 'Qim', 'Qit'}

# 实际CSV列名
CSV_COL = {
    'PR': '涨幅', 'HR': '高幅', '下日HR': '次日高幅',
    '日ZA': '日ZA', '日ZC': '日ZC', '日ZE': '日ZE',
    'DXAB': 'DXAB', 'DXCD': 'DXCD', 'DXEF': 'DXEF',
    '柱排': '柱排', '波型': '波型', '顶型': '顶型', '柱型': '柱型',
    'BSHA': 'BSHA', 'BSAC': 'BSAC',
}

护型列表 = ['甲', '乙', '丙', '丁', '戊', '己']
护型顺序 = {'己': 0, '甲': 1, '戊': 2, '乙': 3, '丁': 4, '丙': 5}

# ── 增量聚合器 ──────────────────────────────────────────────
class IncAgg:
    """增量聚合：边读边算，不保留原始数据"""
    def __init__(self):
        self.n = 0
        self.sum_x = 0.0
        self.sum_x2 = 0.0
        self.sum_hr = 0.0
        self.n_win = 0
        self.n_hr_gt0 = 0
        self.n_hr_gt1 = 0
        self.n_hr_gt2 = 0
        self.n_hr_gt3 = 0

    def add(self, pr, hr=None):
        pr = float(pr)
        self.n += 1
        self.sum_x += pr
        self.sum_x2 += pr * pr
        if pr > 0:
            self.n_win += 1
        if hr is not None:
            hr = float(hr)
            self.sum_hr += hr
            if hr > 0: self.n_hr_gt0 += 1
            if hr > 1: self.n_hr_gt1 += 1
            if hr > 2: self.n_hr_gt2 += 1
            if hr > 3: self.n_hr_gt3 += 1

    def merge(self, other):
        self.n += other.n
        self.sum_x += other.sum_x
        self.sum_x2 += other.sum_x2
        self.sum_hr += other.sum_hr
        self.n_win += other.n_win
        self.n_hr_gt0 += other.n_hr_gt0
        self.n_hr_gt1 += other.n_hr_gt1
        self.n_hr_gt2 += other.n_hr_gt2
        self.n_hr_gt3 += other.n_hr_gt3

    def stats(self):
        if self.n < MIN_SAMPLE:
            return None
        mean = self.sum_x / self.n
        var = self.sum_x2 / self.n - mean * mean
        std = np.sqrt(max(var, 0))
        win_rate = self.n_win / self.n * 100
        sharpe = (mean / std * 100) if std > 0 else 0
        mean_hr = self.sum_hr / self.n if self.n > 0 else 0
        hr_gt0 = self.n_hr_gt0 / self.n * 100
        hr_gt1 = self.n_hr_gt1 / self.n * 100
        hr_gt2 = self.n_hr_gt2 / self.n * 100
        hr_gt3 = self.n_hr_gt3 / self.n * 100
        return {
            'n': self.n, 'mean_pr': mean, 'std_pr': std,
            'win_rate': win_rate, 'sharpe': sharpe, 'mean_hr': mean_hr,
            'hr_gt0': hr_gt0, 'hr_gt1': hr_gt1, 'hr_gt2': hr_gt2, 'hr_gt3': hr_gt3,
        }


def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_and_aggregate():
    """
    增量加载所有CSV，边读边聚合。
    返回聚合器字典，key = (group, zc_cond, board) 等。
    """
    board_map = load_board_map()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    print(f'总文件: {len(files)}', flush=True)

    # 聚合器结构：
    # agg_all[(hx, zc>0)]  — 全量各护型×ZC条件
    # agg_gb[(hx, zc>0)]   — 高波池各护型×ZC条件
    # agg_gb_board[(board, hx, zc>0)] — 高波池按市板
    # agg_all_cidl[(hx, cidl)] — 全量按护型×股票（个体差异）
    # agg_gb_cidl[(hx, cidl)]  — 高波池按护型×股票
    # agg_gb_zp[(hx, zp, zc>0)] — 高波池护型×柱排
    agg_all = defaultdict(IncAgg)
    agg_gb = defaultdict(IncAgg)
    agg_gb_board = defaultdict(IncAgg)
    agg_all_cidl = defaultdict(IncAgg)
    agg_gb_cidl = defaultdict(IncAgg)
    agg_gb_zp = defaultdict(IncAgg)

    total_rows = 0
    gb_rows = 0

    for i, f in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            # 读所有列（但只取需要的）
            df = pd.read_csv(f, encoding='gbk')
            if len(df) < 2:
                continue
        except Exception:
            continue

        cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        is_gb = board in 高波池板块

        pr = df['涨幅'].astype(float).values
        hr = df['高幅'].astype(float).values
        dxab = df['DXAB'].astype(str).values
        zc = df['日ZC'].astype(float).values
        zp = df['柱排'].astype(str).values if '柱排' in df.columns else None

        n = len(df)
        total_rows += n
        if is_gb:
            gb_rows += n

        for j in range(n - 1):  # 最后一行没有下日HR
            dxab_str = dxab[j]
            # DXAB格式如 'a甲↗上1.I'，护型是第2个字符（索引1）
            hx = dxab_str[1] if len(dxab_str) >= 2 and dxab_str[1] in 护型顺序 else ''
            if not hx:
                continue
            p = pr[j]
            h = hr[j + 1]  # 下日高幅
            zc_val = zc[j]
            zc_gt0 = zc_val > 0

            key_all = (hx, zc_gt0)
            agg_all[key_all].add(p, h)

            if is_gb:
                key_gb = (hx, zc_gt0)
                agg_gb[key_gb].add(p, h)

                key_board = (board, hx, zc_gt0)
                agg_gb_board[key_board].add(p, h)

                # 柱排（需要读柱排列）
                # 这里简化：不读柱排，避免增加I/O

            # 个体差异：按cidl聚合涨率
            key_cidl = (hx, cidl)
            agg_all_cidl[key_cidl].add(p)
            if is_gb:
                agg_gb_cidl[key_cidl].add(p)

                # 柱排联合形态
                if zp is not None:
                    z = str(zp[j])
                    # 柱排格式如 '升.尾连QQ.Q2' 或 '(升)人.连后吞QV'
                    # 取第一个不在括号内的中文字符
                    depth = 0
                    zc_key = ''
                    for ch in z:
                        if ch == '(':
                            depth += 1
                        elif ch == ')':
                            depth -= 1
                        elif depth == 0 and ch in '升阳人阴跌':
                            zc_key = ch
                            break
                    if zc_key:
                        agg_gb_zp[(hx, zc_key, zc_gt0)].add(p, h)

    print(f'  全量: {total_rows} 行', flush=True)
    print(f'  高波池: {gb_rows} 行', flush=True)
    return agg_all, agg_gb, agg_gb_board, agg_all_cidl, agg_gb_cidl, agg_gb_zp


def print_对比(title, all_stats, gb_stats, label_width=10):
    lines = [f'\n{"="*80}', f'{title}', '='*80]
    lines.append(f'{"护型":>{label_width}s}  {"全量n":>10s}  {"高波n":>10s}  {"全量均涨":>10s}  {"高波均涨":>10s}  {"全量涨率":>10s}  {"高波涨率":>10s}  {"差异pp":>8s}  {"提示":>10s}')
    lines.append('-'*(label_width + 78))

    for hx in 护型列表:
        a = all_stats.get(hx, {})
        g = gb_stats.get(hx, {})
        if not a and not g:
            continue
        an = a.get('n', 0) if a else 0
        gn = g.get('n', 0) if g else 0
        apr = a.get('mean_pr', 0) if a else 0
        gpr = g.get('mean_pr', 0) if g else 0
        awr = a.get('win_rate', 0) if a else 0
        gwr = g.get('win_rate', 0) if g else 0
        diff = gwr - awr

        tip = ''
        if abs(diff) > 2:
            tip = '⚠️差异>2pp'
        elif gn > 0 and an > 0 and abs(gpr - apr) / max(abs(apr), 0.01) > 0.1:
            tip = '⚠️均涨>10%'

        lines.append(f'{hx:>{label_width}s}  {an:>10,d}  {gn:>10,d}  {apr:>10.2f}%  {gpr:>10.2f}%  {awr:>9.1f}%  {gwr:>9.1f}%  {diff:>+8.1f}  {tip:>10s}')

    return '\n'.join(lines)


def analyze_护型排序(agg_all, agg_gb, zc_gt0, label):
    all_stats = {}
    gb_stats = {}
    for hx in 护型列表:
        s = agg_all.get((hx, zc_gt0))
        if s:
            all_stats[hx] = s.stats()
        s = agg_gb.get((hx, zc_gt0))
        if s:
            gb_stats[hx] = s.stats()
    return print_对比(f'护型排序 DXZC{">0" if zc_gt0 else "<=0"}', all_stats, gb_stats)


def analyze_按市板(agg_gb_board):
    lines = [f'\n{"="*80}', '按市板验证（高波池）', '='*80]
    for board in ['Qic', 'Qim', 'Qit']:
        lines.append(f'\n--- {board} ---')
        lines.append(f'{"护型":>6s}  {"样本":>10s}  {"均涨幅":>8s}  {"涨率":>8s}')
        for hx in 护型列表:
            s = agg_gb_board.get((board, hx, True))
            if s:
                st = s.stats()
                if st:
                    lines.append(f'{hx:>6s}  {st["n"]:>10,d}  {st["mean_pr"]:>7.2f}%  {st["win_rate"]:>7.1f}%')
    return '\n'.join(lines)


def analyze_个体差异(agg_all_cidl, agg_gb_cidl):
    lines = [f'\n{"="*80}', '个体差异分析（高波池 vs 全量）', '='*80]

    for label, agg in [('全量', agg_all_cidl), ('高波池', agg_gb_cidl)]:
        lines.append(f'\n--- {label} ---')
        lines.append(f'{"护型":>6s}  {"覆盖股票":>10s}  {"涨率中位数":>10s}  {"涨率P25":>8s}  {"涨率P75":>8s}')

        # 按护型分组，收集每只股票的涨率
        stock_winrates = defaultdict(list)
        for (hx, cidl), a in agg.items():
            if a.n >= 20:  # 每只股票至少20个样本
                wr = a.n_win / a.n * 100
                stock_winrates[hx].append(wr)

        for hx in 护型列表:
            vals = stock_winrates.get(hx, [])
            if len(vals) < 100:
                continue
            vals = sorted(vals)
            n = len(vals)
            med = vals[n // 2]
            p25 = vals[n // 4]
            p75 = vals[3 * n // 4]
            lines.append(f'{hx:>6s}  {n:>10,d}  {med:>9.1f}%  {p25:>7.1f}%  {p75:>7.1f}%')

    return '\n'.join(lines)


def analyze_次日冲高(agg_all, agg_gb):
    lines = [f'\n{"="*80}', '次日冲高分析（高波池 vs 全量，DXZC>0）', '='*80]

    for label, agg in [('全量', agg_all), ('高波池', agg_gb)]:
        lines.append(f'\n--- {label} ---')
        lines.append(f'{"护型":>6s}  {"样本":>10s}  {"均明高":>8s}  {"明高>0%":>8s}  {"明高>1%":>8s}  {"明高>2%":>8s}  {"明高>3%":>8s}')
        for hx in 护型列表:
            s = agg.get((hx, True))
            if s:
                st = s.stats()
                if st:
                    lines.append(f'{hx:>6s}  {st["n"]:>10,d}  {st["mean_hr"]:>7.2f}%  {st["hr_gt0"]:>7.1f}%  {st["hr_gt1"]:>7.1f}%  {st["hr_gt2"]:>7.1f}%  {st["hr_gt3"]:>7.1f}%')

    return '\n'.join(lines)


def analyze_柱排联合(agg_gb_zp):
    lines = [f'\n{"="*80}', 'DXAB×柱排联合形态（高波池，ZC>0）', '='*80]
    lines.append(f'\n{"护型":>6s}  {"升排":>8s}  {"阳排":>8s}  {"人排":>8s}  {"阴排":>8s}  {"跌排":>8s}')
    for hx in 护型列表:
        row = [hx]
        for zp in ['升', '阳', '人', '阴', '跌']:
            s = agg_gb_zp.get((hx, zp, True))
            if s and s.n >= MIN_SAMPLE:
                row.append(f'{s.sum_x / s.n:>7.2f}%')
            else:
                row.append(f'{"-":>8s}')
        lines.append('  '.join(row))
    return '\n'.join(lines)


def main():
    t0 = time.time()

    print('='*80)
    print('高波池护型全量分析 (v2 增量聚合)')
    print('='*80)
    print()

    agg_all, agg_gb, agg_gb_board, agg_all_cidl, agg_gb_cidl, agg_gb_zp = load_and_aggregate()

    output = []

    # 1. 护型排序
    output.append(analyze_护型排序(agg_all, agg_gb, True, 'DXZC>0'))
    output.append(analyze_护型排序(agg_all, agg_gb, False, 'DXZC<=0'))

    # 2. 按市板验证
    output.append(analyze_按市板(agg_gb_board))

    # 3. 个体差异分析
    output.append(analyze_个体差异(agg_all_cidl, agg_gb_cidl))

    # 4. 次日冲高分析
    output.append(analyze_次日冲高(agg_all, agg_gb))

    # 5. 柱排联合形态
    output.append(analyze_柱排联合(agg_gb_zp))

    result = '\n'.join(output)
    print(result)

    # 保存结果
    out_path = '____temp/高波池_分析结果.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'\n结果已保存: {out_path}')
    print(f'耗时: {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()