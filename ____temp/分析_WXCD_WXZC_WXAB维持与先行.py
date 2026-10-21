#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WXCD / WXZC / WXAB 维持情况 + WXAB与WXCD重合 + WXAB是否WXCD先行指标

数据来源：谕组周 CSV（高波池 Qic/Qim/Qit），GBK 编码，63 列
列索引（权威元数据 _产出物/_工具/元数据_vba数据映射_周类.md）：
    [4]  WXAB护型（首字母=甲/乙/丙/丁/戊/己）
    [12] 周势型 = WXCD护型（首字符=金/银/唏/嘘/屎/尿）
    [18] WXZC（价格 vs WJC 交叉天数，>0=在WJC上方）
    [22] WXAB（JA vs JB 交叉天数，>0=正交/金叉）
    [27] WXCD（JC vs JD 交叉天数，>0=在WJC上方）

用法：
    python ____temp/分析_WXCD_WXZC_WXAB维持与先行.py
"""
import os, io, csv, json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

DATA_DIR = '昭明算展/谕组周'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
高波池板块 = {'Qic', 'Qim', 'Qit'}
OUT_CSV = '____temp/WXCD_WXZC_WXAB维持与先行结果.csv'

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
WXCD_MAP = {'1': '金', '2': '银', '3': '唏', '4': '嘘', '5': '尿', '6': '屎'}


def load_board_map():
    with open(BOARD_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def parse_wxab_hx(s):
    """解析 WXAB护型[4] 首字母 → 甲/乙/丙/丁/戊/己"""
    if not isinstance(s, str) or len(s) < 1:
        return None
    return HX_MAP.get(s[0])


def parse_wxcd_hx(s):
    """解析 WXCD护型[12] 首字符 → 金/银/唏/嘘/尿/屎"""
    if not isinstance(s, str) or len(s) < 1:
        return None
    return WXCD_MAP.get(s[0])


def find_runs(values):
    """识别连续段，返回 [(value, length), ...]"""
    runs = []
    if not values:
        return runs
    prev = values[0]
    run_len = 1
    for v in values[1:]:
        if v == prev:
            run_len += 1
        else:
            runs.append((prev, run_len))
            prev = v
            run_len = 1
    runs.append((prev, run_len))
    return runs


def main():
    board_map = load_board_map()
    files = sorted(os.listdir(DATA_DIR))
    files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]

    # ========== 统计容器 ==========
    # 1. WXCD护型 维持：state -> [段数, 周数和, 周数列表]
    wxcd_stat = defaultdict(lambda: [0, 0, []])
    # 2. WXZC 维持：sign -> [段数, 周数和, 周数列表]
    wxzc_stat = defaultdict(lambda: [0, 0, []])
    # 3. WXAB护型 维持：state -> [段数, 周数和, 周数列表]
    wxab_stat = defaultdict(lambda: [0, 0, []])
    # 4. WXAB×WXCD 重合：计数
    overlap_count = defaultdict(int)
    # 5. 先行指标
    # 5a. AB转正(CD<0) → CD转正
    lead_ab_up_cd_down = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])  # [n, 1周, 2周, 3周, 5周, 10周]
    # 5b. AB转负(CD>0) → CD转负
    lead_ab_down_cd_up = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
    # 5c. CD转正(AB<0) → AB转正（反向）
    lead_cd_up_ab_down = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
    # 5d. CD转负(AB>0) → AB转负（反向）
    lead_cd_down_ab_up = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
    # 5e. 基线
    baseline = defaultdict(lambda: [0, 0])
    # 5f. 转移矩阵
    wxcd_trans = defaultdict(lambda: defaultdict(int))  # from -> to
    wxab_trans = defaultdict(lambda: defaultdict(int))  # from -> to
    # 5g. 平均领先周数（AB转正→CD转正 的间隔）
    lead_weeks_ab_up = []
    lead_weeks_ab_down = []
    lead_weeks_cd_up = []
    lead_weeks_cd_down = []
    # 5h. CD 转正/转负时 AB 状态分布
    cd_up_ab_state = defaultdict(lambda: [0])
    cd_down_ab_state = defaultdict(lambda: [0])
    # 5i. AB 转正/转负时 CD 状态分布
    ab_up_cd_state = defaultdict(lambda: [0])
    ab_down_cd_state = defaultdict(lambda: [0])
    # 5j. 无条件基线
    baseline_cd_up = defaultdict(lambda: [0, 0])
    baseline_cd_down = defaultdict(lambda: [0, 0])
    baseline_ab_up = defaultdict(lambda: [0, 0])
    baseline_ab_down = defaultdict(lambda: [0, 0])

    n_files = 0
    for i, fname in enumerate(files):
        if i % 500 == 0:
            print(f'  [加载] {i}/{len(files)}...')
        cidl = fname.replace('谕组周_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        n_files += 1
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, fname), encoding='gbk',
                             header=None, skiprows=[0],
                             usecols=[4, 12, 18, 22, 27])
            df.columns = ['WXAB护型', 'WXCD护型', 'WXZC', 'WXAB', 'WXCD']
        except Exception:
            continue
        if df.empty:
            continue

        # 数值列
        for c in ['WXZC', 'WXAB', 'WXCD']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['WXZC', 'WXAB', 'WXCD'])
        if df.empty:
            continue

        # 解析状态
        df['wxab_hx'] = df['WXAB护型'].astype(str).map(parse_wxab_hx)
        df['wxcd_hx'] = df['WXCD护型'].astype(str).map(parse_wxcd_hx)
        df['wxzc_sign'] = np.where(df['WXZC'] > 0, 'ZC>0', 'ZC<0')
        df['wxab_sign'] = np.where(df['WXAB'] > 0, 'AB>0', 'AB<0')
        df['wxcd_sign'] = np.where(df['WXCD'] > 0, 'CD>0', 'CD<0')

        # ===== 1. WXCD护型 维持 =====
        for v, ln in find_runs(df['wxcd_hx'].tolist()):
            if v is not None:
                wxcd_stat[v][0] += 1
                wxcd_stat[v][1] += ln
                wxcd_stat[v][2].append(ln)

        # ===== 2. WXZC 维持 =====
        for v, ln in find_runs(df['wxzc_sign'].tolist()):
            wxzc_stat[v][0] += 1
            wxzc_stat[v][1] += ln
            wxzc_stat[v][2].append(ln)

        # ===== 3. WXAB护型 维持 =====
        for v, ln in find_runs(df['wxab_hx'].tolist()):
            if v is not None:
                wxab_stat[v][0] += 1
                wxab_stat[v][1] += ln
                wxab_stat[v][2].append(ln)

        # ===== 4. WXAB×WXCD 重合 =====
        valid = df.dropna(subset=['wxab_hx', 'wxcd_hx'])
        for _, row in valid.iterrows():
            overlap_count[(row['wxab_hx'], row['wxcd_hx'])] += 1

        # ===== 5. 先行指标 =====
        n = len(df)
        ab_val = df['WXAB'].values
        cd_val = df['WXCD'].values
        ab_sign = df['wxab_sign'].values
        cd_sign = df['wxcd_sign'].values

        # 5a. AB转正(CD<0) → CD转正
        for idx in range(1, n):
            if ab_val[idx] > 0 and ab_val[idx-1] <= 0 and cd_val[idx] < 0:
                lead_ab_up_cd_down['n'][0] += 1
                for k in range(1, min(11, n - idx)):
                    if cd_val[idx + k] > 0:
                        if k <= 1: lead_ab_up_cd_down['n'][1] += 1
                        if k <= 2: lead_ab_up_cd_down['n'][2] += 1
                        if k <= 3: lead_ab_up_cd_down['n'][3] += 1
                        if k <= 5: lead_ab_up_cd_down['n'][4] += 1
                        if k <= 10: lead_ab_up_cd_down['n'][5] += 1
                        lead_weeks_ab_up.append(k)
                        break

        # 5b. AB转负(CD>0) → CD转负
        for idx in range(1, n):
            if ab_val[idx] < 0 and ab_val[idx-1] >= 0 and cd_val[idx] > 0:
                lead_ab_down_cd_up['n'][0] += 1
                for k in range(1, min(11, n - idx)):
                    if cd_val[idx + k] < 0:
                        if k <= 1: lead_ab_down_cd_up['n'][1] += 1
                        if k <= 2: lead_ab_down_cd_up['n'][2] += 1
                        if k <= 3: lead_ab_down_cd_up['n'][3] += 1
                        if k <= 5: lead_ab_down_cd_up['n'][4] += 1
                        if k <= 10: lead_ab_down_cd_up['n'][5] += 1
                        lead_weeks_ab_down.append(k)
                        break

        # 5c. CD转正(AB<0) → AB转正（反向）
        for idx in range(1, n):
            if cd_val[idx] > 0 and cd_val[idx-1] <= 0 and ab_val[idx] < 0:
                lead_cd_up_ab_down['n'][0] += 1
                for k in range(1, min(11, n - idx)):
                    if ab_val[idx + k] > 0:
                        if k <= 1: lead_cd_up_ab_down['n'][1] += 1
                        if k <= 2: lead_cd_up_ab_down['n'][2] += 1
                        if k <= 3: lead_cd_up_ab_down['n'][3] += 1
                        if k <= 5: lead_cd_up_ab_down['n'][4] += 1
                        if k <= 10: lead_cd_up_ab_down['n'][5] += 1
                        lead_weeks_cd_up.append(k)
                        break

        # 5d. CD转负(AB>0) → AB转负（反向）
        for idx in range(1, n):
            if cd_val[idx] < 0 and cd_val[idx-1] >= 0 and ab_val[idx] > 0:
                lead_cd_down_ab_up['n'][0] += 1
                for k in range(1, min(11, n - idx)):
                    if ab_val[idx + k] < 0:
                        if k <= 1: lead_cd_down_ab_up['n'][1] += 1
                        if k <= 2: lead_cd_down_ab_up['n'][2] += 1
                        if k <= 3: lead_cd_down_ab_up['n'][3] += 1
                        if k <= 5: lead_cd_down_ab_up['n'][4] += 1
                        if k <= 10: lead_cd_down_ab_up['n'][5] += 1
                        lead_weeks_cd_down.append(k)
                        break

        # 5e. 基线
        for idx in range(n):
            if ab_val[idx] > 0:
                baseline['AB>0时CD>0'][0] += 1
                if cd_val[idx] > 0:
                    baseline['AB>0时CD>0'][1] += 1
            if ab_val[idx] < 0:
                baseline['AB<0时CD<0'][0] += 1
                if cd_val[idx] < 0:
                    baseline['AB<0时CD<0'][1] += 1

        # 5f. 转移矩阵
        wxcd_hx_list = df['wxcd_hx'].tolist()
        wxab_hx_list = df['wxab_hx'].tolist()
        for j in range(1, n):
            if wxcd_hx_list[j-1] is not None and wxcd_hx_list[j] is not None:
                wxcd_trans[wxcd_hx_list[j-1]][wxcd_hx_list[j]] += 1
            if wxab_hx_list[j-1] is not None and wxab_hx_list[j] is not None:
                wxab_trans[wxab_hx_list[j-1]][wxab_hx_list[j]] += 1

        # 5g. CD 转正/转负时 AB 的状态分布（所有事件，非条件）
        for idx in range(1, n):
            if cd_val[idx] > 0 and cd_val[idx-1] <= 0:
                # CD 刚转正
                if ab_val[idx] > 0:
                    cd_up_ab_state['AB>0'][0] += 1
                elif ab_val[idx] == 0:
                    cd_up_ab_state['AB=0'][0] += 1
                else:
                    cd_up_ab_state['AB<0'][0] += 1
            if cd_val[idx] < 0 and cd_val[idx-1] >= 0:
                # CD 刚转负
                if ab_val[idx] < 0:
                    cd_down_ab_state['AB<0'][0] += 1
                elif ab_val[idx] == 0:
                    cd_down_ab_state['AB=0'][0] += 1
                else:
                    cd_down_ab_state['AB>0'][0] += 1

        # 5h. AB 转正/转负时 CD 的状态分布（所有事件，非条件）
        for idx in range(1, n):
            if ab_val[idx] > 0 and ab_val[idx-1] <= 0:
                # AB 刚转正
                if cd_val[idx] > 0:
                    ab_up_cd_state['CD>0'][0] += 1
                elif cd_val[idx] == 0:
                    ab_up_cd_state['CD=0'][0] += 1
                else:
                    ab_up_cd_state['CD<0'][0] += 1
            if ab_val[idx] < 0 and ab_val[idx-1] >= 0:
                # AB 刚转负
                if cd_val[idx] < 0:
                    ab_down_cd_state['CD<0'][0] += 1
                elif cd_val[idx] == 0:
                    ab_down_cd_state['CD=0'][0] += 1
                else:
                    ab_down_cd_state['CD>0'][0] += 1

        # 5i. 无条件 CD 转正/转负概率（基线）
        for idx in range(1, n):
            if cd_val[idx-1] <= 0:
                baseline_cd_up['n'][0] += 1
                if cd_val[idx] > 0:
                    baseline_cd_up['n'][1] += 1
            if cd_val[idx-1] >= 0:
                baseline_cd_down['n'][0] += 1
                if cd_val[idx] < 0:
                    baseline_cd_down['n'][1] += 1

        # 5j. 无条件 AB 转正/转负概率（基线）
        for idx in range(1, n):
            if ab_val[idx-1] <= 0:
                baseline_ab_up['n'][0] += 1
                if ab_val[idx] > 0:
                    baseline_ab_up['n'][1] += 1
            if ab_val[idx-1] >= 0:
                baseline_ab_down['n'][0] += 1
                if ab_val[idx] < 0:
                    baseline_ab_down['n'][1] += 1

    print(f'\n处理完成：{n_files} 只股票')

    # ========== 输出 ==========
    out_lines = []
    out_lines.append('=' * 80)
    out_lines.append('WXCD / WXZC / WXAB 维持情况 + WXAB与WXCD重合 + 先行指标分析')
    out_lines.append('=' * 80)

    # ---- 1. WXCD护型 维持 ----
    out_lines.append('\n' + '=' * 80)
    out_lines.append('一、WXCD 护型维持情况（周类，高波池）')
    out_lines.append('=' * 80)
    out_lines.append(f'{"WXCD状态":<8} {"段数":>8} {"平均(周)":>8} {"中位(周)":>8} {"最长(周)":>8} {"占比%":>8}')
    out_lines.append('-' * 55)
    total_seg = sum(s[0] for s in wxcd_stat.values())
    for state in ['金', '银', '唏', '嘘', '尿', '屎']:
        s = wxcd_stat.get(state, [0, 0, []])
        if s[0] == 0:
            continue
        n = s[0]
        avg = s[1] / n
        median = sorted(s[2])[len(s[2]) // 2] if s[2] else 0
        pct = n / total_seg * 100
        out_lines.append(f'{state:<8} {n:>8} {avg:>8.2f} {median:>8} {max(s[2]):>8} {pct:>7.1f}%')

    # ---- 1b. WXCD 转移矩阵 ----
    out_lines.append('\n--- WXCD 状态转移矩阵（行=当前，列=下一周）---')
    cd_states = ['金', '银', '唏', '嘘', '尿', '屎']
    header = f'{"当前/下周":<8}'
    for cd in cd_states:
        header += f' {cd:>8}'
    header += f' {"n":>10}'
    out_lines.append(header)
    out_lines.append('-' * 70)
    for from_state in cd_states:
        row = wxcd_trans.get(from_state, {})
        row_total = sum(row.values())
        if row_total == 0:
            continue
        line = f'{from_state:<8}'
        for to_state in cd_states:
            cnt = row.get(to_state, 0)
            pct = cnt / row_total * 100 if row_total else 0
            line += f' {pct:>7.1f}%'
        line += f' {row_total:>10,}'
        out_lines.append(line)

    # ---- 2. WXZC 维持 ----
    out_lines.append('\n' + '=' * 80)
    out_lines.append('二、WXZC 维持情况（周类，高波池）')
    out_lines.append('=' * 80)
    out_lines.append(f'{"WXZC状态":<8} {"段数":>8} {"平均(周)":>8} {"中位(周)":>8} {"最长(周)":>8} {"占比%":>8}')
    out_lines.append('-' * 55)
    total_seg_zc = sum(s[0] for s in wxzc_stat.values())
    for state in ['ZC>0', 'ZC<0']:
        s = wxzc_stat.get(state, [0, 0, []])
        if s[0] == 0:
            continue
        n = s[0]
        avg = s[1] / n
        median = sorted(s[2])[len(s[2]) // 2] if s[2] else 0
        pct = n / total_seg_zc * 100
        out_lines.append(f'{state:<8} {n:>8} {avg:>8.2f} {median:>8} {max(s[2]):>8} {pct:>7.1f}%')

    # ---- 3. WXAB护型 维持 ----
    out_lines.append('\n' + '=' * 80)
    out_lines.append('三、WXAB 护型维持情况（周类，高波池）')
    out_lines.append('=' * 80)
    out_lines.append(f'{"WXAB状态":<8} {"段数":>8} {"平均(周)":>8} {"中位(周)":>8} {"最长(周)":>8} {"占比%":>8}')
    out_lines.append('-' * 55)
    total_seg_ab = sum(s[0] for s in wxab_stat.values())
    for state in ['甲', '乙', '丙', '丁', '戊', '己']:
        s = wxab_stat.get(state, [0, 0, []])
        if s[0] == 0:
            continue
        n = s[0]
        avg = s[1] / n
        median = sorted(s[2])[len(s[2]) // 2] if s[2] else 0
        pct = n / total_seg_ab * 100
        out_lines.append(f'{state:<8} {n:>8} {avg:>8.2f} {median:>8} {max(s[2]):>8} {pct:>7.1f}%')

    # ---- 3b. WXAB 转移矩阵 ----
    out_lines.append('\n--- WXAB 状态转移矩阵（行=当前，列=下一周）---')
    ab_states = ['甲', '乙', '丙', '丁', '戊', '己']
    header = f'{"当前/下周":<8}'
    for ab in ab_states:
        header += f' {ab:>8}'
    header += f' {"n":>10}'
    out_lines.append(header)
    out_lines.append('-' * 70)
    for from_state in ab_states:
        row = wxab_trans.get(from_state, {})
        row_total = sum(row.values())
        if row_total == 0:
            continue
        line = f'{from_state:<8}'
        for to_state in ab_states:
            cnt = row.get(to_state, 0)
            pct = cnt / row_total * 100 if row_total else 0
            line += f' {pct:>7.1f}%'
        line += f' {row_total:>10,}'
        out_lines.append(line)

    # ---- 4. WXAB×WXCD 重合 ----
    out_lines.append('\n' + '=' * 80)
    out_lines.append('四、WXAB × WXCD 重合情况（周类，高波池）')
    out_lines.append('=' * 80)
    total_overlap = sum(overlap_count.values())
    out_lines.append(f'总样本数: {total_overlap:,}')
    out_lines.append('\n' + f'{"WXAB/WXCD":<8}')
    for cd in cd_states:
        out_lines[-1] += f' {cd:>8}'
    out_lines[-1] += f' {"合计":>10}'
    out_lines.append('-' * 70)
    for ab in ab_states:
        row_total = sum(overlap_count.get((ab, cd), 0) for cd in cd_states)
        if row_total == 0:
            continue
        line = f'{ab:<8}'
        for cd in cd_states:
            cnt = overlap_count.get((ab, cd), 0)
            pct = cnt / row_total * 100 if row_total else 0
            line += f' {pct:>7.1f}%'
        line += f' {row_total:>10,}'
        out_lines.append(line)
    line = f'{"合计":<8}'
    for cd in cd_states:
        col_total = sum(overlap_count.get((ab, cd), 0) for ab in ab_states)
        pct = col_total / total_overlap * 100 if total_overlap else 0
        line += f' {pct:>7.1f}%'
    line += f' {total_overlap:>10,}'
    out_lines.append(line)

    # 每行WXAB状态内，WXCD状态分布（行百分比）
    out_lines.append(f'\n--- 每行 WXAB 状态内 WXCD 分布（行百分比）---')
    for ab in ab_states:
        row_total = sum(overlap_count.get((ab, cd), 0) for cd in cd_states)
        if row_total == 0:
            continue
        dist = {cd: overlap_count.get((ab, cd), 0) / row_total * 100 for cd in cd_states}
        top = sorted(dist.items(), key=lambda x: -x[1])
        out_lines.append(f'  {ab}: ' + '  '.join(f'{cd}={pct:.1f}%' for cd, pct in top))

    # 每列WXCD状态内，WXAB状态分布（列百分比）
    out_lines.append(f'\n--- 每列 WXCD 状态内 WXAB 分布（列百分比）---')
    for cd in cd_states:
        col_total = sum(overlap_count.get((ab, cd), 0) for ab in ab_states)
        if col_total == 0:
            continue
        dist = {ab: overlap_count.get((ab, cd), 0) / col_total * 100 for ab in ab_states}
        top = sorted(dist.items(), key=lambda x: -x[1])
        out_lines.append(f'  {cd}: ' + '  '.join(f'{ab}={pct:.1f}%' for ab, pct in top))

    # ---- 5. 先行指标 ----
    out_lines.append('\n' + '=' * 80)
    out_lines.append('五、WXAB 是否为 WXCD 先行指标')
    out_lines.append('=' * 80)

    # 5a. 基线
    out_lines.append('\n--- 基线（无条件概率）---')
    for name, s in baseline.items():
        if s[0] > 0:
            out_lines.append(f'  {name}: {s[1]/s[0]*100:.2f}%  (n={s[0]:,})')

    # 5b. AB转正(CD<0) → CD转正
    out_lines.append('\n--- WXAB 转正（且 CD<0）→ WXCD 后续转正概率 ---')
    s = lead_ab_up_cd_down['n']
    if s[0] > 0:
        n = s[0]
        out_lines.append(f'  事件数: {n:,}')
        out_lines.append(f'  1周内 CD转正: {s[1]/n*100:.2f}%')
        out_lines.append(f'  2周内 CD转正: {s[2]/n*100:.2f}%')
        out_lines.append(f'  3周内 CD转正: {s[3]/n*100:.2f}%')
        out_lines.append(f'  5周内 CD转正: {s[4]/n*100:.2f}%')
        out_lines.append(f'  10周内 CD转正: {s[5]/n*100:.2f}%')
        if lead_weeks_ab_up:
            avg_lead = np.mean(lead_weeks_ab_up)
            med_lead = np.median(lead_weeks_ab_up)
            out_lines.append(f'  平均领先周数: {avg_lead:.2f}周  中位: {med_lead:.0f}周')

    # 5c. AB转负(CD>0) → CD转负
    out_lines.append('\n--- WXAB 转负（且 CD>0）→ WXCD 后续转负概率 ---')
    s = lead_ab_down_cd_up['n']
    if s[0] > 0:
        n = s[0]
        out_lines.append(f'  事件数: {n:,}')
        out_lines.append(f'  1周内 CD转负: {s[1]/n*100:.2f}%')
        out_lines.append(f'  2周内 CD转负: {s[2]/n*100:.2f}%')
        out_lines.append(f'  3周内 CD转负: {s[3]/n*100:.2f}%')
        out_lines.append(f'  5周内 CD转负: {s[4]/n*100:.2f}%')
        out_lines.append(f'  10周内 CD转负: {s[5]/n*100:.2f}%')
        if lead_weeks_ab_down:
            avg_lead = np.mean(lead_weeks_ab_down)
            med_lead = np.median(lead_weeks_ab_down)
            out_lines.append(f'  平均领先周数: {avg_lead:.2f}周  中位: {med_lead:.0f}周')

    # 5d. CD转正(AB<0) → AB转正（反向）
    out_lines.append('\n--- WXCD 转正（且 AB<0）→ WXAB 后续转正概率（反向）---')
    s = lead_cd_up_ab_down['n']
    if s[0] > 0:
        n = s[0]
        out_lines.append(f'  事件数: {n:,}')
        out_lines.append(f'  1周内 AB转正: {s[1]/n*100:.2f}%')
        out_lines.append(f'  2周内 AB转正: {s[2]/n*100:.2f}%')
        out_lines.append(f'  3周内 AB转正: {s[3]/n*100:.2f}%')
        out_lines.append(f'  5周内 AB转正: {s[4]/n*100:.2f}%')
        out_lines.append(f'  10周内 AB转正: {s[5]/n*100:.2f}%')
        if lead_weeks_cd_up:
            avg_lead = np.mean(lead_weeks_cd_up)
            med_lead = np.median(lead_weeks_cd_up)
            out_lines.append(f'  平均领先周数: {avg_lead:.2f}周  中位: {med_lead:.0f}周')

    # 5e. CD转负(AB>0) → AB转负（反向）
    out_lines.append('\n--- WXCD 转负（且 AB>0）→ WXAB 后续转负概率（反向）---')
    s = lead_cd_down_ab_up['n']
    if s[0] > 0:
        n = s[0]
        out_lines.append(f'  事件数: {n:,}')
        out_lines.append(f'  1周内 AB转负: {s[1]/n*100:.2f}%')
        out_lines.append(f'  2周内 AB转负: {s[2]/n*100:.2f}%')
        out_lines.append(f'  3周内 AB转负: {s[3]/n*100:.2f}%')
        out_lines.append(f'  5周内 AB转负: {s[4]/n*100:.2f}%')
        out_lines.append(f'  10周内 AB转负: {s[5]/n*100:.2f}%')
        if lead_weeks_cd_down:
            avg_lead = np.mean(lead_weeks_cd_down)
            med_lead = np.median(lead_weeks_cd_down)
            out_lines.append(f'  平均领先周数: {avg_lead:.2f}周  中位: {med_lead:.0f}周')

    # 5f. 对比总结
    out_lines.append('\n' + '=' * 80)
    out_lines.append('六、先行指标对比总结')
    out_lines.append('=' * 80)

    # 5g. 无条件基线
    out_lines.append('\n--- 无条件基线（每周转正/转负概率）---')
    for name, s in [('CD转正(前周CD≤0)', baseline_cd_up['n']),
                     ('CD转负(前周CD≥0)', baseline_cd_down['n']),
                     ('AB转正(前周AB≤0)', baseline_ab_up['n']),
                     ('AB转负(前周AB≥0)', baseline_ab_down['n'])]:
        if s[0] > 0:
            out_lines.append(f'  {name}: {s[1]/s[0]*100:.2f}%  (n={s[0]:,})')

    # 5h. CD 转正/转负时 AB 状态分布
    out_lines.append('\n--- WXCD 转正时，WXAB 状态分布 ---')
    total_cd_up = sum(v[0] for v in cd_up_ab_state.values())
    if total_cd_up > 0:
        for state in ['AB>0', 'AB=0', 'AB<0']:
            cnt = cd_up_ab_state.get(state, [0])[0]
            out_lines.append(f'  {state}: {cnt/total_cd_up*100:.2f}%  (n={cnt:,})')

    out_lines.append('\n--- WXCD 转负时，WXAB 状态分布 ---')
    total_cd_down = sum(v[0] for v in cd_down_ab_state.values())
    if total_cd_down > 0:
        for state in ['AB<0', 'AB=0', 'AB>0']:
            cnt = cd_down_ab_state.get(state, [0])[0]
            out_lines.append(f'  {state}: {cnt/total_cd_down*100:.2f}%  (n={cnt:,})')

    # 5i. AB 转正/转负时 CD 状态分布
    out_lines.append('\n--- WXAB 转正时，WXCD 状态分布 ---')
    total_ab_up = sum(v[0] for v in ab_up_cd_state.values())
    if total_ab_up > 0:
        for state in ['CD>0', 'CD=0', 'CD<0']:
            cnt = ab_up_cd_state.get(state, [0])[0]
            out_lines.append(f'  {state}: {cnt/total_ab_up*100:.2f}%  (n={cnt:,})')

    out_lines.append('\n--- WXAB 转负时，WXCD 状态分布 ---')
    total_ab_down = sum(v[0] for v in ab_down_cd_state.values())
    if total_ab_down > 0:
        for state in ['CD<0', 'CD=0', 'CD>0']:
            cnt = ab_down_cd_state.get(state, [0])[0]
            out_lines.append(f'  {state}: {cnt/total_ab_down*100:.2f}%  (n={cnt:,})')

    out_lines.append('''
WXAB 与 WXCD 的关系（基于交叉天数符号）：
  WXAB = JA vs JB 交叉（短期均线，WJA vs WJB）
  WXCD = JC vs JD 交叉（中期均线，WJC vs WJD）
  WXZC = 价格 vs WJC 交叉

先行性判断：
  若 AB 转正后 CD 转正概率显著高于基线，且 AB 转正时 CD 多为负，
  则 AB 是 CD 的先行指标。
  反之，若 CD 转正后 AB 转正概率更高，则 CD 是 AB 的先行指标。
''')

    # 输出到终端
    for line in out_lines:
        print(line)

    # 写 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\n'.join(out_lines))
    print(f'\n结果已写入: {OUT_CSV}')


if __name__ == '__main__':
    main()