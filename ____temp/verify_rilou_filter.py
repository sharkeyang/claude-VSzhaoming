# -*- coding: utf-8 -*-
"""验证日漏提示过滤：策略内（龙+武剔除差的）中，鼎/连阳/跌孕 vs 其他 的下周HR>=3%
数据：谕组周 CSV（GBK，53列旧版）
列：[3]HR [5]波型 [15]ZB周 [20]AB周 [47]BT鼎 [49]并符串
"""
import os, glob, sys
from collections import defaultdict

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组周"
C_HR, C_波型, C_ZB, C_AB, C_BT鼎, C_并符 = 3,5,15,20,47,49

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

    # 策略内（龙+武剔除差的）中，按日漏提示分类
    stats = defaultdict(lambda: {'n': 0, 'hr3': 0})
    total_strategy = {'n': 0, 'hr3': 0}

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
                    btding = parts[C_BT鼎]
                    bingfu = parts[C_并符]
                except:
                    continue
                # 策略内：龙+武（四态龙 AB>0且ZB>0，或武 AB<0且ZB>0）剔除差的
                is_longwu = (ab > 0 and zb > 0) or (ab < 0 and zb > 0)
                if not is_longwu or is_excluded(bx):
                    continue
                total_strategy['n'] += 1
                if hr >= 3:
                    total_strategy['hr3'] += 1
                # 日漏提示分类
                if btding == '1':
                    k = '鼎'
                elif bingfu and bingfu[-1] == 'Q':
                    k = '连阳'
                elif bingfu and bingfu[-1] == 'v':
                    k = '跌孕'
                else:
                    k = '其他(被过滤)'
                stats[k]['n'] += 1
                if hr >= 3:
                    stats[k]['hr3'] += 1

    print("=" * 70)
    print(f"日漏提示过滤验证（{limit_files or '全量'}文件，策略内）")
    print("=" * 70)
    ts = total_strategy
    print(f"策略内整体: n={ts['n']}, 下周HR>=3%: {ts['hr3']/ts['n']*100:.2f}%" if ts['n'] else "n=0")
    print()
    print(f"{'分类':<14} {'n':<10} {'占比':<8} {'下周HR>=3%':<12}")
    print("-" * 70)
    for k in ['鼎', '连阳', '跌孕', '其他(被过滤)']:
        s = stats[k]
        rate = s['hr3']/s['n']*100 if s['n'] else 0
        pct = s['n']/ts['n']*100 if ts['n'] else 0
        print(f"{k:<14} {s['n']:<10} {pct:<8.2f}% {rate:.2f}%")

    print()
    print("=" * 70)
    print("关键对比：日漏提示识别 vs 其他(被过滤)")
    print("=" * 70)
    recog_n = sum(stats[k]['n'] for k in ['鼎', '连阳', '跌孕'])
    recog_hr3 = sum(stats[k]['hr3'] for k in ['鼎', '连阳', '跌孕'])
    other = stats['其他(被过滤)']
    if recog_n and other['n']:
        r_rate = recog_hr3/recog_n*100
        o_rate = other['hr3']/other['n']*100
        print(f"日漏提示识别(鼎/连阳/跌孕): n={recog_n}, 下周HR>=3%: {r_rate:.2f}%")
        print(f"其他(被过滤): n={other['n']}, 下周HR>=3%: {o_rate:.2f}%")
        print(f"差: {r_rate-o_rate:.2f}pp")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()