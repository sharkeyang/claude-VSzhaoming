'''
180格全覆盖概率表生成器（含贝叶斯收缩）
=======================
输入：昭明算展/谕组日/ 下所有CSV文件（7462只股票）
输出：DXEF_DXCD_DXAB_完整概率表2.csv

对每个(DXEF, DXCD, DXAB)分支，统计：
  →ZE>0, →ZE>0+ZC>0, →ZE>0+ZC>0+ZA>0
  下日DSHA>0, 下日DSHA>1, 下日DSHA>2

贝叶斯收缩：小样本(<100)分支向父级(DXEF×DXCD)借力
'''

import os, csv, sys, glob, re
from collections import defaultdict

# ===== 配置 =====
PROJ = r'd:\@VSwork\VS昭明计划VBA优化'
DATA_DIR = os.path.join(PROJ, '昭明算展', '谕组日_备份_20260804')
OUTPUT = os.path.join(PROJ, '____temp', 'DXEF_DXCD_DXAB_完整概率表2.csv')

# 贝叶斯收缩参数
SHRINK_K = 100       # 收缩强度：k越大，小样本越偏向父级
SHRINK_THRESHOLD = 100  # 样本<此值时触发收缩

# 列索引（从CSV header确认）
COL_DATE = 0
COL_HR = 6       # 今日高幅
COL_DXEF = 7     # 第一字=金/银/嘘/唏/屎/尿
COL_DXCD = 8     # 上/中/下/忐/忠/忑
COL_DXAB = 9     # 第四字=上/中/下/忐/忠/忑
COL_ZA = 13      # 日ZA
COL_ZC = 14      # 日ZC
COL_ZE = 15      # 日ZE
COL_BSHA = 19    # BSHA
COL_HR_NEXT = 26 # 次日高幅

DXEF_ORDER = ['金', '银', '嘘', '唏', '屎', '尿']
DXCD_ORDER = ['上', '中', '下', '忐', '忠', '忑']
DXAB_ORDER = ['上', '中', '下', '忐', '忠', '忑']

# 6个评分指标
METRICS = ['ze>0', 'zc>0', 'za>0', 'dsha>0', 'dsha>1', 'dsha>2']


def parse_dxef(val):
    '''DXEF第一字 = 金/银/嘘/唏/屎/尿'''
    if not val or len(val) < 1:
        return None
    first = val[0]
    if first in DXEF_ORDER:
        return first
    return None


def parse_dxcd(val):
    '''DXCD = 上/中/下/忐/忠/忑'''
    if not val or len(val) < 1:
        return None
    if val in DXCD_ORDER:
        return val
    return None


def parse_dxab(val):
    '''DXAB第四字 = 上/中/下/忐/忠/忑'''
    if not val or len(val) < 4:
        return None
    fourth = val[3]
    if fourth in DXAB_ORDER:
        return fourth
    return None


def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_gt(val, threshold=0):
    return val is not None and val > threshold


def safe_ge(val, threshold):
    return val is not None and val >= threshold


def calc_rate(numerator, denominator):
    '''计算百分比，分母为0返回0'''
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def calc_avg(vals):
    '''计算均值'''
    if not vals:
        return ''
    return round(sum(vals) / len(vals), 2)


def calc_med(vals):
    '''计算中位数'''
    if not vals:
        return ''
    sv = sorted(vals)
    return round(sv[len(sv) // 2], 2)


def bayesian_shrink(n_raw, n_success, n_parent, n_success_parent, k=SHRINK_K):
    '''
    贝叶斯收缩：小样本向父级借力
    p_shrink = (n_raw * p_raw + k * p_parent) / (n_raw + k)
    '''
    if n_parent == 0:
        return calc_rate(n_success, n_raw)
    p_parent = n_success_parent / n_parent
    p_shrink = (n_raw * (n_success / n_raw if n_raw > 0 else 0) + k * p_parent) / (n_raw + k)
    return round(p_shrink * 100, 1)


def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
    print(f'找到 {len(files)} 个日线谕组CSV文件')

    # 三级统计：(dxef, dxcd, dxab) → 计数
    stats = defaultdict(lambda: {
        'N': 0, 'N_ze>0': 0, 'N_zc>0': 0, 'N_za>0': 0,
        'N_dsha>0': 0, 'N_dsha>1': 0, 'N_dsha>2': 0,
        'hrs': []
    })
    # 二级统计：(dxef, dxcd) → 计数（用于贝叶斯父级）
    parent_stats = defaultdict(lambda: {
        'N': 0, 'N_ze>0': 0, 'N_zc>0': 0, 'N_za>0': 0,
        'N_dsha>0': 0, 'N_dsha>1': 0, 'N_dsha>2': 0,
        'hrs': []
    })

    total_rows = 0
    skipped = 0
    file_count = 0

    for fpath in files:
        file_count += 1
        if file_count % 500 == 0:
            print(f'  处理中: {file_count}/{len(files)} 文件, {total_rows} 行')

        try:
            with open(fpath, 'r', encoding='gb18030') as f:
                reader = csv.reader(f)
                header = next(reader)  # 跳过表头
                rows = [r for r in reader]
        except Exception as e:
            print(f'  跳过 {os.path.basename(fpath)}: {e}')
            skipped += 1
            continue

        if len(rows) < 2:
            skipped += 1
            continue

        # 对每行（除最后一行），取下一行作为次日数据
        for i in range(len(rows) - 1):
            cur = rows[i]
            nxt = rows[i + 1]

            # 解析当前行
            dxef = parse_dxef(cur[COL_DXEF])
            dxcd = parse_dxcd(cur[COL_DXCD])
            dxab = parse_dxab(cur[COL_DXAB])
            if not dxef or not dxcd or not dxab:
                continue

            # 解析次日数据
            ze_next = parse_float(nxt[COL_ZE])
            zc_next = parse_float(nxt[COL_ZC])
            za_next = parse_float(nxt[COL_ZA])
            dsha_next = parse_float(nxt[COL_HR])    # 下一行高幅 = 下日简单冲高
            hr_next = parse_float(nxt[COL_HR])

            if ze_next is None:
                continue

            # 三级统计
            key3 = (dxef, dxcd, dxab)
            s3 = stats[key3]
            s3['N'] += 1
            total_rows += 1

            if safe_gt(ze_next):
                s3['N_ze>0'] += 1
                if safe_gt(zc_next):
                    s3['N_zc>0'] += 1
                    if safe_gt(za_next):
                        s3['N_za>0'] += 1

            if dsha_next is not None:
                if safe_gt(dsha_next, 0):
                    s3['N_dsha>0'] += 1
                if safe_ge(dsha_next, 1):
                    s3['N_dsha>1'] += 1
                if safe_ge(dsha_next, 2):
                    s3['N_dsha>2'] += 1

            if hr_next is not None:
                s3['hrs'].append(hr_next)

            # 二级统计（父级）
            key2 = (dxef, dxcd)
            s2 = parent_stats[key2]
            s2['N'] += 1
            if safe_gt(ze_next):
                s2['N_ze>0'] += 1
                if safe_gt(zc_next):
                    s2['N_zc>0'] += 1
                    if safe_gt(za_next):
                        s2['N_za>0'] += 1
            if dsha_next is not None:
                if safe_gt(dsha_next, 0):
                    s2['N_dsha>0'] += 1
                if safe_ge(dsha_next, 1):
                    s2['N_dsha>1'] += 1
                if safe_ge(dsha_next, 2):
                    s2['N_dsha>2'] += 1
            if hr_next is not None:
                s2['hrs'].append(hr_next)

    print(f'\n处理完成: {total_rows} 行, {skipped} 文件跳过')

    # ===== 贝叶斯收缩 + 输出CSV =====
    with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([
            'DXEF', 'DXCD', 'DXAB',
            '样本', '→ZE>0', '→ZE>0+ZC>0', '→ZE>0+ZC>0+ZA>0',
            '下日DSHA>0', '下日DSHA>1', '下日DSHA>2',
            '均HR', '中位HR',
            '父级样本', '收缩标记'
        ])

        shrink_count = 0
        written = 0

        for dxef in DXEF_ORDER:
            for dxcd in DXCD_ORDER:
                for dxab in DXAB_ORDER:
                    key3 = (dxef, dxcd, dxab)
                    key2 = (dxef, dxcd)
                    s3 = stats.get(key3)
                    s2 = parent_stats.get(key2)

                    if not s3 or s3['N'] == 0:
                        w.writerow([dxef, dxcd, dxab] + [''] * 11)
                        continue

                    n = s3['N']
                    parent_n = s2['N'] if s2 else 0

                    # 是否需要收缩
                    is_shrunk = n < SHRINK_THRESHOLD
                    if is_shrunk:
                        shrink_count += 1
                        shrink_tag = f'贝叶斯(k={SHRINK_K})'
                    else:
                        shrink_tag = ''

                    # 对6个指标各自计算（小样本时收缩）
                    def calc_metric(metric):
                        n_success = s3[f'N_{metric}']
                        if is_shrunk and s2:
                            n_success_parent = s2[f'N_{metric}']
                            return bayesian_shrink(n, n_success, parent_n, n_success_parent)
                        else:
                            return calc_rate(n_success, n)

                    p_ze = calc_metric('ze>0')
                    p_zc = calc_metric('zc>0')
                    p_za = calc_metric('za>0')
                    p_dsha0 = calc_metric('dsha>0')
                    p_dsha1 = calc_metric('dsha>1')
                    p_dsha3 = calc_metric('dsha>2')

                    hrs = s3['hrs']
                    avg_hr = calc_avg(hrs) if not is_shrunk else ''
                    med_hr = calc_med(hrs) if not is_shrunk else ''

                    w.writerow([
                        dxef, dxcd, dxab, n,
                        p_ze, p_zc, p_za,
                        p_dsha0, p_dsha1, p_dsha3,
                        avg_hr, med_hr,
                        parent_n, shrink_tag
                    ])
                    written += 1

    print(f'输出: {OUTPUT}')
    print(f'共 {written} 个分支')
    print(f'贝叶斯收缩处理: {shrink_count} 个小样本分支（阈值<{SHRINK_THRESHOLD}）')


if __name__ == '__main__':
    main()