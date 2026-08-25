# -*- coding: utf-8 -*-
"""
analyze_trans_dxef_dxcd_full.py
================================
计算日级别护型转移矩阵（完整 8×8），分别按 DXEF 六类（金/银/唏/嘘/尿/屎）
和 DXCD 六类（上/中/下/忐/忠/忑）拆分，用于验证转移矩阵是否受高阶均线影响。

数据：高波池（Qic+Qim+Qit）3451 只，谕组日 CSV。
护型 = DXAB 首字符（a甲/b乙/c丙/z丁/y戊/r己），乙/戊按日ZA符号拆分子行+子列。
转移 = 当前日护型 → 次日日护型。
"""
import csv, os, json, io, sys
from collections import defaultdict

OUTF = io.open('____temp/_trans_dxef_dxcd_full.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

# 高波池板块
高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'

# 护型字母 → 中文
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
# 转移矩阵行/列顺序（乙/戊按ZA拆分）
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']

# DXEF 六类映射：日向首字符（升/待/降）+ 日ZE符号
def dxef_to_class(ef, ze):
    """DXEF列格式 '日向/周向'，取日向首字符（升/待/降），结合日ZE符号"""
    try:
        ze_f = float(ze)
    except:
        return None
    parts = ef.split('/')
    if len(parts) != 2:
        return None
    rx = parts[0].strip()
    if not rx:
        return None
    rx_first = rx[0]
    # 日向首字符 → 升/待/降
    if rx_first == '升':
        ri = '升'
    elif rx_first == '待':
        ri = '待'
    elif rx_first == '降':
        ri = '降'
    else:
        return None
    # 结合日ZE符号 → 六类
    if ze_f > 0:
        return {'升': '金', '待': '银', '降': '唏'}[ri]
    else:
        return {'升': '嘘', '待': '尿', '降': '屎'}[ri]

# DXCD 六类
DXCD_ORDER = ['上', '中', '下', '忐', '忠', '忑']
DXEF_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

def hx_key(dxab, za):
    """护型 + ZA拆分 → 转移矩阵行/列key"""
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
    files = sorted(os.listdir('昭明算展/谕组日0825'))
    files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]
    out(f'总文件: {len(files)}')

    # 聚合器：trans[(split_type, split_val, zc_gt0, cur, nxt)] = count
    # split_type: 'DXEF' 或 'DXCD'
    trans_dxef = defaultdict(int)   # (dxef_class, zc_gt0, cur, nxt)
    trans_dxcd = defaultdict(int)   # (dxcd_class, zc_gt0, cur, nxt)
    total_rows = 0
    gb_rows = 0

    for i, fname in enumerate(files):
        if i % 1000 == 0:
            out(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        is_gb = board in 高波池板块
        if not is_gb:
            continue

        path = os.path.join('昭明算展/谕组日0825', fname)
        try:
            with open(path, 'r', encoding='gbk', errors='replace') as f:
                r = csv.reader(f)
                header = next(r)
                prev = None  # (hx_key, dxef_class, dxcd_class, zc_gt0)
                for row in r:
                    if len(row) < 16:
                        continue
                    dxab = row[9]
                    za = row[13]
                    zc = row[14]
                    ze = row[15]
                    ef = row[7]
                    cd = row[8]
                    if len(dxab) < 2:
                        continue
                    cur = hx_key(dxab, za)
                    if not cur:
                        continue
                    ef_cls = dxef_to_class(ef, ze)
                    cd_cls = cd.strip() if cd.strip() in DXCD_ORDER else None
                    try:
                        zc_gt0 = float(zc) > 0
                    except:
                        zc_gt0 = False

                    total_rows += 1
                    gb_rows += 1

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

    # ── 输出 DXEF 六类转移矩阵 ──
    out('')
    out('=' * 90)
    out('一、按 DXEF 六类拆分的完整护型转移矩阵（高波池，区分DXZC）')
    out('=' * 90)
    for cls in DXEF_ORDER:
        for zc_gt0 in [True, False]:
            zc_label = 'DXZC>0' if zc_gt0 else 'DXZC≤0'
            out('')
            out(f'### DXEF={cls}（{zc_label}）')
            out(f'| 当前 | 样本 | →甲 | →乙(ZA>0) | →乙(ZA≤0) | →丙 | →丁 | →戊(ZA>0) | →戊(ZA≤0) | →己 |')
            out(f'|:----:|:----:|:---:|:---------:|:---------:|:---:|:---:|:---------:|:---------:|:---:|')
            for cur in HX_ORDER:
                # 该行总样本
                row_total = sum(trans_dxef[(cls, zc_gt0, cur, nxt)] for nxt in HX_ORDER)
                if row_total == 0:
                    continue
                cells = []
                for nxt in HX_ORDER:
                    cnt = trans_dxef[(cls, zc_gt0, cur, nxt)]
                    pct = cnt / row_total * 100
                    # 高亮主转移（>30%）
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
    out('二、按 DXCD 六类拆分的完整护型转移矩阵（高波池，区分DXZC）')
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