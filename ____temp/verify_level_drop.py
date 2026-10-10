# -*- coding: utf-8 -*-
"""逐级缩小：列出每一级保留 vs 被过滤掉的指标
数据：谕组周 CSV（GBK，53列旧版）
列：[3]HR [5]波型 [14]ZA周 [15]ZB周 [16]ZC周 [20]AB周
"""
import os, glob, sys
from collections import defaultdict

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组周"
C_HR, C_波型, C_ZA, C_ZB, C_ZC, C_AB = 3,5,14,15,16,20

def is_excluded(bx):
    """是否被剔除（龙扩根/龙震根/龙头返）"""
    if '根' in bx and ('扩' in bx or '震' in bx):
        return True
    if '头' in bx and '返' in bx:
        return True
    return False

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 各级别统计
    stats = defaultdict(lambda: {'n': 0, 'hr3': 0})

    for fp in files:
        try:
            f = open(fp, encoding='gbk', errors='ignore')
        except Exception as e:
            print(f"SKIP {fp}: {e}", file=sys.stderr)
            continue
        with f:
            f.readline()
            for line in f:
                parts = line.rstrip('\n').split(',')
                if len(parts) < 53:
                    continue
                try:
                    hr = float(parts[C_HR]) if parts[C_HR] else 0.0
                    bx = parts[C_波型]
                    ab = int(parts[C_AB]) if parts[C_AB] else 0
                    zb = int(parts[C_ZB]) if parts[C_ZB] else 0
                except:
                    continue
                # 全部样本
                stats['全部样本']['n'] += 1
                if hr >= 3:
                    stats['全部样本']['hr3'] += 1
                # 判断是否龙+武
                is_longwu = (ab > 0 and zb > 0) or (ab < 0 and zb > 0)
                if is_longwu:
                    stats['龙+武']['n'] += 1
                    if hr >= 3:
                        stats['龙+武']['hr3'] += 1
                    # 策略内
                    if not is_excluded(bx):
                        stats['策略内']['n'] += 1
                        if hr >= 3:
                            stats['策略内']['hr3'] += 1
                    else:
                        stats['第2级过滤(龙扩根/龙震根/龙头返)']['n'] += 1
                        if hr >= 3:
                            stats['第2级过滤(龙扩根/龙震根/龙头返)']['hr3'] += 1
                else:
                    stats['第1级过滤(虎+雀)']['n'] += 1
                    if hr >= 3:
                        stats['第1级过滤(虎+雀)']['hr3'] += 1

    print("=" * 75)
    print(f"逐级缩小：保留 vs 被过滤掉的指标（{limit_files or '全量'}文件）")
    print("=" * 75)
    print(f"{'级别':<28} {'n':<12} {'占比':<10} {'下周HR>=3%':<12}")
    print("-" * 75)
    base_n = stats['全部样本']['n']
    for lv in ['全部样本', '龙+武', '第1级过滤(虎+雀)', '策略内', '第2级过滤(龙扩根/龙震根/龙头返)']:
        s = stats[lv]
        rate = s['hr3']/s['n']*100 if s['n'] else 0
        pct = s['n']/base_n*100 if base_n else 0
        print(f"{lv:<28} {s['n']:<12} {pct:<10.2f}% {rate:<12.2f}%")

    print()
    print("=" * 75)
    print("过滤功效分析")
    print("=" * 75)
    # 第1级
    keep1 = stats['龙+武']; drop1 = stats['第1级过滤(虎+雀)']
    k1 = keep1['hr3']/keep1['n']*100 if keep1['n'] else 0
    d1 = drop1['hr3']/drop1['n']*100 if drop1['n'] else 0
    print(f"第1级缩小：保留(龙+武) {k1:.2f}% vs 过滤(虎+雀) {d1:.2f}%，差 {k1-d1:.2f}pp")
    print(f"  过滤掉 {drop1['n']/base_n*100:.2f}% 的范围（虎+雀，下周HR>=3% 仅 {d1:.2f}%）")
    # 第2级
    keep2 = stats['策略内']; drop2 = stats['第2级过滤(龙扩根/龙震根/龙头返)']
    k2 = keep2['hr3']/keep2['n']*100 if keep2['n'] else 0
    d2 = drop2['hr3']/drop2['n']*100 if drop2['n'] else 0
    print(f"第2级缩小：保留(策略内) {k2:.2f}% vs 过滤(龙扩根/龙震根/龙头返) {d2:.2f}%，差 {k2-d2:.2f}pp")
    print(f"  过滤掉 {drop2['n']/base_n*100:.2f}% 的范围（龙扩根/龙震根/龙头返，下周HR>=3% 仅 {d2:.2f}%）")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()