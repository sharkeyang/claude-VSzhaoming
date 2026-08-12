# -*- coding: utf-8 -*-
"""DXZA持续时长分析：按金银唏嘘尿屎六类细分"""
import csv, os, io
from collections import defaultdict, Counter

out = io.open('____temp/_dxza_duration_result2.txt', 'w', encoding='utf-8')

def outln(s=''):
    out.write(s + '\n')

CD_POS = {'上', '中', '下'}
CD_NEG = {'忐', '忠', '忑'}

def classify_dxef(cd, zc, ze):
    """金银唏嘘尿屎分类（从 DXCD/日ZC/日ZE 推导）"""
    cd_pos = cd in CD_POS
    zc_pos = zc > 0
    ze_pos = ze > 0
    if cd_pos and zc_pos:
        return '金'
    elif not cd_pos and zc_pos and ze_pos:
        return '银'
    elif not cd_pos and zc_pos and not ze_pos:
        return '唏'
    elif cd_pos and not zc_pos and ze_pos:
        return '嘘'
    elif cd_pos and not zc_pos and not ze_pos:
        return '尿'
    else:  # not cd_pos and not zc_pos
        return '屎'

# 累加器：按 (DXEF, DXCD, DXAB, DXZC>0) 统计 ZA>0 和 ZA<0 运行
pos_runs = defaultdict(list)
neg_runs = defaultdict(list)

files_done = 0
total_runs = 0

for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            run_sign = None
            run_len = 0
            run_start_ef = None
            run_start_cd = None
            run_start_ab = None
            run_start_zc = None

            for row in r:
                if len(row) < 16: continue
                cd_raw = row[8].strip()
                dxab_raw = row[9].strip()
                zc_raw = row[14].strip()
                ze_raw = row[15].strip()
                za_raw = row[13].strip()

                if len(dxab_raw) < 2: continue
                try: za = float(za_raw)
                except: continue
                try: zc = float(zc_raw)
                except: zc = 0
                try: ze = float(ze_raw)
                except: ze = 0

                dxab = dxab_raw[:2]

                cur_sign = 1 if za > 0 else (-1 if za < 0 else 0)

                if cur_sign == 0:
                    if run_sign is not None and run_len >= 1:
                        key = (run_start_ef, run_start_cd, run_start_ab, run_start_zc > 0)
                        if run_sign == 1:
                            pos_runs[key].append(run_len)
                        else:
                            neg_runs[key].append(run_len)
                        total_runs += 1
                    run_sign = None
                    run_len = 0
                elif cur_sign == run_sign:
                    run_len += 1
                else:
                    if run_sign is not None and run_len >= 1:
                        key = (run_start_ef, run_start_cd, run_start_ab, run_start_zc > 0)
                        if run_sign == 1:
                            pos_runs[key].append(run_len)
                        else:
                            neg_runs[key].append(run_len)
                        total_runs += 1
                    run_sign = cur_sign
                    run_len = 1
                    run_start_ef = classify_dxef(cd_raw, zc, ze)
                    run_start_cd = cd_raw
                    run_start_ab = dxab
                    run_start_zc = zc

            if run_sign is not None and run_len >= 1:
                key = (run_start_ef, run_start_cd, run_start_ab, run_start_zc > 0)
                if run_sign == 1:
                    pos_runs[key].append(run_len)
                else:
                    neg_runs[key].append(run_len)
                total_runs += 1
    except Exception:
        pass
    files_done += 1
    if files_done % 1000 == 0:
        outln(f'## Progress: {files_done} files, {total_runs} runs')

outln(f'## Summary')
outln(f'Files: {files_done}, Total runs: {total_runs}')
outln('')

def median(lst):
    s = sorted(lst); n = len(s)
    if n == 0: return 0
    if n % 2 == 1: return s[n//2]
    return (s[n//2-1] + s[n//2]) / 2

def mean(lst):
    if not lst: return 0
    return sum(lst) / len(lst)

def p90(lst):
    s = sorted(lst)
    return s[int(len(s)*0.9)]

# 按金银唏嘘尿屎汇总
def print_by_ef(runs_dict, sign_label):
    outln(f'=== {sign_label} 持续时间（按金银唏嘘尿屎六类） ===')
    outln(f'{"DXEF":>4s} {"运行数":>8s} {"均值(天)":>10s} {"中位数":>8s} {"P90":>8s} {"最多":>8s}')
    outln('-'*55)

    ef_groups = defaultdict(list)
    for (ef, cd, ab, zc_pos), lengths in runs_dict.items():
        ef_groups[ef].extend(lengths)

    for ef in ['金', '银', '唏', '嘘', '尿', '屎']:
        lst = ef_groups.get(ef, [])
        if lst:
            outln(f'{ef:>4s} {len(lst):>8d}  {mean(lst):>10.2f}  {median(lst):>8.1f}  {p90(lst):>8.1f}  {max(lst):>8d}')
        else:
            outln(f'{ef:>4s} {"-":>8s}')
    outln('')

    # 按DXEF+DXAB交叉
    outln(f'  --- 按DXEF×DXAB交叉 ---')
    outln(f'{"DXEF":>4s} {"DXAB":>6s} {"运行数":>8s} {"均值(天)":>10s} {"中位数":>8s} {"P90":>8s} {"最多":>8s}')
    outln('-'*65)
    for ef in ['金', '银', '唏', '嘘', '尿', '屎']:
        ef_ab = defaultdict(list)
        for (e, cd, ab, zc_pos), lengths in runs_dict.items():
            if e == ef:
                ef_ab[ab].extend(lengths)
        for ab in ['a甲', 'b乙', 'c丙', 'r己', 'y戊', 'z丁']:
            lst = ef_ab.get(ab, [])
            if lst:
                outln(f'{ef:>4s} {ab:>6s} {len(lst):>8d}  {mean(lst):>10.2f}  {median(lst):>8.1f}  {p90(lst):>8.1f}  {max(lst):>8d}')
        outln('')

    # 按DXEF+DXZC交叉
    outln(f'  --- 按DXEF×DXZC交叉 ---')
    outln(f'{"DXEF":>4s} {"ZC":>4s} {"运行数":>8s} {"均值(天)":>10s} {"中位数":>8s} {"P90":>8s} {"最多":>8s}')
    outln('-'*65)
    for ef in ['金', '银', '唏', '嘘', '尿', '屎']:
        for zc_lbl in ['ZC>0', 'ZC≤0']:
            lst = []
            for (e, cd, ab, zc_pos), lengths in runs_dict.items():
                zc_match = (zc_lbl == 'ZC>0' and zc_pos) or (zc_lbl == 'ZC≤0' and not zc_pos)
                if e == ef and zc_match:
                    lst.extend(lengths)
            if lst:
                outln(f'{ef:>4s} {zc_lbl:>4s} {len(lst):>8d}  {mean(lst):>10.2f}  {median(lst):>8.1f}  {p90(lst):>8.1f}  {max(lst):>8d}')
    outln('')

print_by_ef(pos_runs, 'ZA>0')
print_by_ef(neg_runs, 'ZA<0')

# 关键对比：金银唏嘘尿屎 好/差 分组
outln('=== 金银唏嘘尿屎 好/差 分组对比 ===')
outln('')
outln('好组：金（最强势）')
outln('差组：屎（最弱势）')
outln('')

for sign_label, runs_dict in [('ZA>0', pos_runs), ('ZA<0', neg_runs)]:
    outln(f'--- {sign_label} ---')
    gold = []; shit = []
    for (ef, cd, ab, zc_pos), lengths in runs_dict.items():
        if ef == '金': gold.extend(lengths)
        elif ef == '屎': shit.extend(lengths)
    if gold:
        outln(f'  金: n={len(gold):>8d}  mean={mean(gold):>7.2f}  med={median(gold):>6.1f}  p90={p90(gold):>6.1f}')
    if shit:
        outln(f'  屎: n={len(shit):>8d}  mean={mean(shit):>7.2f}  med={median(shit):>6.1f}  p90={p90(shit):>6.1f}')
    if gold and shit:
        outln(f'  金/屎 均值比 = {mean(gold)/mean(shit):.2f}x')
    outln('')

out.close()
print('Done')