# -*- coding: utf-8 -*-
"""验证 8.7.3 周级波型备选策略表：策略内占比 + 策略内 vs 策略外 上涨率
数据：谕组周 CSV（GBK，53列旧版）
列：[3]HR [5]波型 [14]ZA周 [15]ZB周 [16]ZC周 [20]AB周 [43]宽哼JA周
"""
import os, glob, sys
from collections import defaultdict

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组周"
C_HR, C_波型, C_ZA, C_ZB, C_ZC, C_AB, C_宽哼 = 3,5,14,15,16,20,43

def strategy(bx):
    """按波型编码关键词分类，映射到 8.7.3 策略（内/外/其他）
    编码：震正=龙震(内)，震负=虎震(外)，头正=龙头(内)，头负=虎头(外)"""
    # 内（首选+可做）
    if '武' in bx:
        return '内_武'
    if '猪' in bx:
        return '内_龙扩猪'
    if '栅' in bx:
        return '内_龙扩栅'
    if '杂' in bx:
        return '内_龙扩杂'
    if '震正' in bx:
        if '〇' in bx:
            return '内_龙震〇'
        if '芽' in bx:
            return '内_龙震芽'
        if '根' in bx:
            return '外_龙震根'
        return '内_龙震'
    if '头正' in bx:
        if '交' in bx:
            return '内_龙头交'
        if '返' in bx:
            return '外_龙头返'
        return '内_龙头'
    if '扩' in bx:
        if '根' in bx:
            return '外_龙扩根'
        return '内_龙扩'
    # 外（排除）
    if '震负' in bx:
        return '外_虎震'
    if '头负' in bx:
        return '外_虎头'
    if '虎' in bx:
        return '外_虎'
    if '雀' in bx:
        return '外_雀'
    return '外_其他'

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 统计：策略分类 的 n 和 hr3
    stats = defaultdict(lambda: {'n': 0, 'hr3': 0})
    total_n = 0; total_hr3 = 0

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
                total_n += 1
                if hr >= 3:
                    total_hr3 += 1
                # 只在四态龙（AB>0且ZB>0）内判断策略，非四态龙归为外
                if not (ab > 0 and zb > 0):
                    st = '外_非四态龙'
                else:
                    st = strategy(bx)
                stats[st]['n'] += 1
                if hr >= 3:
                    stats[st]['hr3'] += 1

    print("=" * 70)
    print(f"8.7.3 周级波型备选策略表 验证（{limit_files or '全量'}文件）")
    print("=" * 70)
    print(f"全样本: n={total_n}, 下周HR>=3%: {total_hr3/total_n*100:.2f}%" if total_n else "n=0")
    print()

    # 策略内 vs 策略外
    inner_n = 0; inner_hr3 = 0
    outer_n = 0; outer_hr3 = 0
    print(f"{'策略分类':<12} {'n':<10} {'占比':<8} {'下周HR>=3%':<12}")
    print("-" * 70)
    for st in sorted(stats.keys()):
        s = stats[st]
        rate = s['hr3']/s['n']*100 if s['n'] else 0
        pct = s['n']/total_n*100 if total_n else 0
        print(f"{st:<12} {s['n']:<10} {pct:<8.2f}% {rate:.2f}%")
        if st.startswith('内_'):
            inner_n += s['n']; inner_hr3 += s['hr3']
        else:
            outer_n += s['n']; outer_hr3 += s['hr3']

    print()
    print("=" * 70)
    print("策略内 vs 策略外 汇总")
    print("=" * 70)
    if inner_n:
        print(f"策略内（首选+可做）: n={inner_n}, 占比 {inner_n/total_n*100:.2f}%, 下周HR>=3%: {inner_hr3/inner_n*100:.2f}%")
    if outer_n:
        print(f"策略外（排除+其他）: n={outer_n}, 占比 {outer_n/total_n*100:.2f}%, 下周HR>=3%: {outer_hr3/outer_n*100:.2f}%")
    if inner_n and outer_n:
        print(f"差: {inner_hr3/inner_n*100 - outer_hr3/outer_n*100:.2f}pp")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()