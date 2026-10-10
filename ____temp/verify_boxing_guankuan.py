# -*- coding: utf-8 -*-
"""验证"波型×窄管"交叉：波型备选（龙扩/龙震/龙头/武）叠加窄管（管宽≤5）过滤
数据：谕组周 CSV（GBK，53列旧版）
列：[3]HR [5]波型 [14]ZA周 [15]ZB周 [16]ZC周 [20]AB周 [43]宽哼JA周
"""
import os, glob, sys
from collections import defaultdict

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组周"
C_HR, C_波型, C_ZA, C_ZB, C_ZC, C_AB, C_宽哼 = 3,5,14,15,16,20,43

def classify_boxing(bx):
    """按波型编码关键词分类（旧编码，按扩/震/头/武）"""
    if '武' in bx:
        return '武'
    if '扩' in bx or '猪' in bx or '栅' in bx or '杂' in bx:
        return '龙扩'
    if '震' in bx:
        return '龙震'
    if '头' in bx:
        return '龙头'
    if '虎' in bx:
        return '虎'
    if '雀' in bx:
        return '雀'
    return '其他'

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 统计：波型 × 窄管/宽管 的 下周HR>=3% 率
    # key = (波型, 窄管/宽管)
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
                    gk = int(parts[C_宽哼]) if parts[C_宽哼] else 0
                    za = int(parts[C_ZA]); zb = int(parts[C_ZB]); zc = int(parts[C_ZC])
                    ab = int(parts[C_AB]) if parts[C_AB] else 0
                except:
                    continue
                # 只在主升区（四态龙：AB>0 且 ZB>0）分析
                if not (ab > 0 and zb > 0):
                    continue
                bx_class = classify_boxing(bx)
                # 窄管/宽管
                guan = '窄管' if gk <= 5 else '宽管'
                key = (bx_class, guan)
                stats[key]['n'] += 1
                if hr >= 3:
                    stats[key]['hr3'] += 1

    print("=" * 70)
    print(f"波型×窄管 交叉验证（{limit_files or '全量'}文件，主升区四态龙内）")
    print("=" * 70)
    print(f"{'波型':<8} {'管宽':<6} {'n':<10} {'下周HR>=3%':<12}")
    print("-" * 70)
    # 按波型排序输出
    for bx_class in ['龙扩', '龙震', '龙头', '武', '龙', '虎', '雀', '其他']:
        for guan in ['宽管', '窄管']:
            key = (bx_class, guan)
            if key in stats and stats[key]['n'] > 0:
                s = stats[key]
                rate = s['hr3']/s['n']*100 if s['n'] else 0
                print(f"{bx_class:<8} {guan:<6} {s['n']:<10} {rate:.2f}%")

    print()
    print("=" * 70)
    print("窄管 vs 宽管 对比（各波型）")
    print("=" * 70)
    for bx_class in ['龙扩', '龙震', '龙头', '武']:
        k_wide = (bx_class, '宽管')
        k_narrow = (bx_class, '窄管')
        if k_wide in stats and k_narrow in stats:
            w = stats[k_wide]; n = stats[k_narrow]
            w_rate = w['hr3']/w['n']*100 if w['n'] else 0
            n_rate = n['hr3']/n['n']*100 if n['n'] else 0
            print(f"{bx_class}: 宽管 {w_rate:.2f}% (n={w['n']}) vs 窄管 {n_rate:.2f}% (n={n['n']}), 差 {w_rate-n_rate:.2f}pp")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()