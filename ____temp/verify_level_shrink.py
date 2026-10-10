# -*- coding: utf-8 -*-
"""验证逐级缩小效率：全部样本 → 龙+武 → 策略内（剔除龙扩根/龙震根/龙头返）
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
        return True  # 龙扩根/龙震根
    if '头' in bx and '返' in bx:
        return True  # 龙头返
    return False

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 三级统计
    levels = {
        '全部样本': {'n': 0, 'hr3': 0},
        '龙+武': {'n': 0, 'hr3': 0},
        '策略内': {'n': 0, 'hr3': 0},
    }

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
                levels['全部样本']['n'] += 1
                if hr >= 3:
                    levels['全部样本']['hr3'] += 1
                # 龙+武（四态龙 AB>0且ZB>0，或 武 AB<0且ZB>0）
                if (ab > 0 and zb > 0) or (ab < 0 and zb > 0):
                    levels['龙+武']['n'] += 1
                    if hr >= 3:
                        levels['龙+武']['hr3'] += 1
                    # 策略内（龙+武 剔除 龙扩根/龙震根/龙头返）
                    if not is_excluded(bx):
                        levels['策略内']['n'] += 1
                        if hr >= 3:
                            levels['策略内']['hr3'] += 1

    print("=" * 70)
    print(f"逐级缩小效率验证（{limit_files or '全量'}文件）")
    print("=" * 70)
    print(f"{'级别':<10} {'n':<12} {'占比':<10} {'下周HR>=3%':<12} {'相对上一级提升':<12}")
    print("-" * 70)
    prev_rate = None
    for lv in ['全部样本', '龙+武', '策略内']:
        s = levels[lv]
        rate = s['hr3']/s['n']*100 if s['n'] else 0
        pct = s['n']/levels['全部样本']['n']*100 if levels['全部样本']['n'] else 0
        boost = ''
        if prev_rate is not None:
            boost = f"{rate-prev_rate:+.2f}pp"
        print(f"{lv:<10} {s['n']:<12} {pct:<10.2f}% {rate:<12.2f}% {boost}")
        prev_rate = rate

    print()
    print("=" * 70)
    print("缩小范围分析")
    print("=" * 70)
    base_n = levels['全部样本']['n']
    for lv in ['龙+武', '策略内']:
        s = levels[lv]
        pct = s['n']/base_n*100 if base_n else 0
        print(f"{lv}: 占全部 {pct:.2f}%，缩小了 {100-pct:.2f}% 的范围")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()