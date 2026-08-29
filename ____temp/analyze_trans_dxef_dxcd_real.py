# -*- coding: utf-8 -*-
"""
analyze_trans_dxef_dxcd_real.py
================================
用真实 DXEF/DXCD 重跑日级别护型转移矩阵 + 次日HR≥3% 区分度分析。

数据：新 昭明算展/谕组日（7460只），高波池（Qic+Qim+Qit）。
真实 DXEF = 月策带日(col50) 第一括号 token（金/银/唏/嘘/尿/屎）
真实 DXCD = 月策带日(col50) 第二括号 token（上/中/下/忐/忠/忑）
次日高幅 = col26（已验证 = 下一日高幅 col6）
护型 = DXAB(col9) 首字符，乙/戊按日ZA(col13)符号拆分子行+子列。
转移 = 当前日护型 → 次日日护型。
"""
import csv, os, json, io
from collections import defaultdict

OUTF = io.open('____temp/_trans_dxef_dxcd_real.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
DATA_DIR = '昭明算展/谕组日'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']
DXCD_ORDER = ['上', '中', '下', '忐', '忠', '忑']
DXEF_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

def parse_mc(mc):
    """月策带日 '(EF)X(CD)Y(AB)' → (ef, cd, ab)"""
    if not mc or not mc.startswith('('):
        return None, None, None
    parts = mc.split('(')
    if len(parts) < 4:
        return None, None, None
    ef = parts[1][0] if parts[1] else None
    cd = parts[2][0] if parts[2] else None
    ab = parts[3][0] if parts[3] else None
    return ef, cd, ab

def hx_key(dxab, za):
    if len(dxab) < 2:
        return None
    c = dxab[0]
    hx = HX_MAP.get(c)
    if not hx:
        return None
    try:
        za_f = float(za)
    except:
        za_f = 0
    if hx == '乙':
        return '乙(ZA>0)' if za_f > 0 else '乙(ZA≤0)'
    if hx == '戊':
        return '戊(ZA>0)' if za_f > 0 else '戊(ZA≤0)'
    return hx

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]
    out(f'总文件: {len(files)}')

    # 转移矩阵聚合器
    trans_dxef = defaultdict(int)   # (ef_cls, zc_gt0, cur, nxt)
    trans_dxcd = defaultdict(int)   # (cd_cls, zc_gt0, cur, nxt)
    # 次日HR>=3% 区分度聚合器
    hr_dxef = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # ef_cls -> hx -> [n, hr3]
    hr_dxcd = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # cd_cls -> hx -> [n, hr3]
    # 次日HR>=3% 按 DXZC 拆分（用于 §2.11 快速决策表）
    hr_dxef_zc = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # (ef_cls, zc_gt0) -> hx -> [n, hr3]
    # DXCD 新旧方法对比
    cd_old_new = defaultdict(int)   # (old, new) -> count
    cd_total = 0
    total_rows = 0
    gb_rows = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            out(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue

        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, 'r', encoding='gbk', errors='replace') as f:
                r = csv.reader(f)
                header = next(r)
                prev = None  # (hx_key, ef_cls, cd_cls, zc_gt0)
                for row in r:
                    if len(row) < 51:
                        continue
                    dxab = row[9]
                    za = row[13]
                    zc = row[14]
                    mc = row[50]
                    ef_cls, cd_cls, ab_cls = parse_mc(mc)
                    if ef_cls not in DXEF_ORDER:
                        ef_cls = None
                    if cd_cls not in DXCD_ORDER:
                        cd_cls = None
                    cur = hx_key(dxab, za)
                    if not cur:
                        continue
                    try:
                        zc_gt0 = float(zc) > 0
                    except:
                        zc_gt0 = False

                    total_rows += 1
                    gb_rows += 1

                    # 次日HR>=3%（col26 次日高幅）
                    try:
                        hr = float(row[26])
                    except:
                        hr = None

                    if ef_cls and hr is not None:
                        hr_dxef[ef_cls][cur][0] += 1
                        if hr >= 3:
                            hr_dxef[ef_cls][cur][1] += 1
                        hr_dxef_zc[(ef_cls, zc_gt0)][cur][0] += 1
                        if hr >= 3:
                            hr_dxef_zc[(ef_cls, zc_gt0)][cur][1] += 1
                    if cd_cls and hr is not None:
                        hr_dxcd[cd_cls][cur][0] += 1
                        if hr >= 3:
                            hr_dxcd[cd_cls][cur][1] += 1

                    # DXCD 新旧对比：旧=CSV col8，新=月策带日第二token
                    old_cd = row[8].strip()
                    if old_cd in DXCD_ORDER and cd_cls:
                        cd_old_new[(old_cd, cd_cls)] += 1
                        cd_total += 1

                    if prev is not None:
                        p_cur, p_ef, p_cd, p_zc = prev
                        if p_ef and ef_cls:
                            trans_dxef[(p_ef, p_zc, p_cur, cur)] += 1
                        if p_cd and cd_cls:
                            trans_dxcd[(p_cd, p_zc, p_cur, cur)] += 1
                    prev = (cur, ef_cls, cd_cls, zc_gt0)
        except Exception as e:
            out(f'  跳过 {fname}: {e}')
            continue

    out(f'高波池行数: {gb_rows}')

    # ── DXCD 新旧方法对比 ──
    out('')
    out('=' * 90)
    out('DXCD 新旧方法对比（旧=CSV col8，新=月策带日第二token）')
    out('=' * 90)
    out(f'DXCD 总样本: {cd_total:,}')
    match = sum(v for (o, n), v in cd_old_new.items() if o == n)
    out(f'新旧一致: {match:,} ({match/cd_total*100:.2f}%)')
    out('不一致明细 (旧->新):')
    for (o, n), v in sorted(cd_old_new.items(), key=lambda x: -x[1]):
        if o != n:
            out(f'  {o}->{n}: {v:,} ({v/cd_total*100:.2f}%)')

    # ── 次日HR>=3% 区分度 ──
    out('')
    out('=' * 90)
    out('次日HR≥3% 区分度（真实DXEF 六类）')
    out('=' * 90)
    out('| 护型 | ' + ' | '.join(DXEF_ORDER) + ' | 极差 |')
    out('|:---:|' + '|:---:|' * len(DXEF_ORDER) + '|:---:|')
    for hx in HX_ORDER:
        vals = []
        for ef in DXEF_ORDER:
            n, c = hr_dxef[ef][hx]
            vals.append(f'{c/n*100:.1f}%' if n else '—')
        nums = [c/n*100 for ef in DXEF_ORDER for n, c in [hr_dxef[ef][hx]] if n]
        rng = f'{max(nums)-min(nums):.1f}pp' if nums else '—'
        out(f'| **{hx}** | ' + ' | '.join(vals) + f' | {rng} |')

    out('')
    out('=' * 90)
    out('次日HR≥3% 区分度（真实DXCD 六类）')
    out('=' * 90)
    out('| 护型 | ' + ' | '.join(DXCD_ORDER) + ' | 极差 |')
    out('|:---:|' + '|:---:|' * len(DXCD_ORDER) + '|:---:|')
    for hx in HX_ORDER:
        vals = []
        for cd in DXCD_ORDER:
            n, c = hr_dxcd[cd][hx]
            vals.append(f'{c/n*100:.1f}%' if n else '—')
        nums = [c/n*100 for cd in DXCD_ORDER for n, c in [hr_dxcd[cd][hx]] if n]
        rng = f'{max(nums)-min(nums):.1f}pp' if nums else '—'
        out(f'| **{hx}** | ' + ' | '.join(vals) + f' | {rng} |')

    # ── 次日HR>=3% 按 DXZC 拆分（§2.11 用） ──
    out('')
    out('=' * 90)
    out('次日HR≥3% 按 DXZC 拆分（真实DXEF 六类，§2.11 用）')
    out('=' * 90)
    for zc_gt0 in [True, False]:
        zc_label = 'DXZC>0' if zc_gt0 else 'DXZC≤0'
        out('')
        out(f'**{zc_label}：**')
        out('| 护型 | ' + ' | '.join(DXEF_ORDER) + ' |')
        out('|:---:|' + '|:---:|' * len(DXEF_ORDER) + '|')
        for hx in HX_ORDER:
            vals = []
            for ef in DXEF_ORDER:
                n, c = hr_dxef_zc[(ef, zc_gt0)][hx]
                vals.append(f'{c/n*100:.1f}%' if n else '—')
            out(f'| **{hx}** | ' + ' | '.join(vals) + ' |')

    # ── 输出 DXEF 六类转移矩阵 ──
    out('')
    out('=' * 90)
    out('一、按真实 DXEF 六类拆分的完整护型转移矩阵（高波池，区分DXZC）')
    out('=' * 90)
    for cls in DXEF_ORDER:
        for zc_gt0 in [True, False]:
            zc_label = 'DXZC>0' if zc_gt0 else 'DXZC≤0'
            out('')
            out(f'### DXEF={cls}（{zc_label}）')
            out(f'| 当前 | 样本 | →甲 | →乙(ZA>0) | →乙(ZA≤0) | →丙 | →丁 | →戊(ZA>0) | →戊(ZA≤0) | →己 |')
            out(f'|:----:|:----:|:---:|:---------:|:---------:|:---:|:---:|:---------:|:---------:|:---:|')
            for cur in HX_ORDER:
                row_total = sum(trans_dxef[(cls, zc_gt0, cur, nxt)] for nxt in HX_ORDER)
                if row_total == 0:
                    continue
                cells = []
                for nxt in HX_ORDER:
                    cnt = trans_dxef[(cls, zc_gt0, cur, nxt)]
                    pct = cnt / row_total * 100
                    if pct >= 30:
                        cells.append(f'**{pct:.1f}%**')
                    elif cnt > 0:
                        cells.append(f'{pct:.1f}%')
                    else:
                        cells.append('—')
                out(f'| **{cur}** | {row_total:,} | ' + ' | '.join(cells) + ' |')

    # ── 输出 DXCD 六类转移矩阵 ──
    out('')
    out('=' * 90)
    out('二、按真实 DXCD 六类拆分的完整护型转移矩阵（高波池，区分DXZC）')
    out('=' * 90)
    for cls in DXCD_ORDER:
        for zc_gt0 in [True, False]:
            zc_label = 'DXZC>0' if zc_gt0 else 'DXZC≤0'
            out('')
            out(f'### DXCD={cls}（{zc_label}）')
            out(f'| 当前 | 样本 | →甲 | →乙(ZA>0) | →乙(ZA≤0) | →丙 | →丁 | →戊(ZA>0) | →戊(ZA≤0) | →己 |')
            out(f'|:----:|:----:|:---:|:---------:|:---------:|:---:|:---:|:---------:|:---------:|:---:|')
            for cur in HX_ORDER:
                row_total = sum(trans_dxcd[(cls, zc_gt0, cur, nxt)] for nxt in HX_ORDER)
                if row_total == 0:
                    continue
                cells = []
                for nxt in HX_ORDER:
                    cnt = trans_dxcd[(cls, zc_gt0, cur, nxt)]
                    pct = cnt / row_total * 100
                    if pct >= 30:
                        cells.append(f'**{pct:.1f}%**')
                    elif cnt > 0:
                        cells.append(f'{pct:.1f}%')
                    else:
                        cells.append('—')
                out(f'| **{cur}** | {row_total:,} | ' + ' | '.join(cells) + ' |')

    OUTF.close()
    print('Done')

if __name__ == '__main__':
    main()
