# -*- coding: utf-8 -*-
"""补充验证（修正版）：①己+前WTZB>0+跌孕 转甲率；②周类镜面对称（丙乙WXZA<0反弹向上）
数据：谕组周 CSV（GBK，53列旧版）
列：[3]HR [4]WXAB护型 [6]柱排周 [14]WXZA [15]WXZB [16]WXZC [20]WXAB交叉
"""
import os, glob, sys

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组周"
C_HR, C_AB, C_柱排, C_ZA, C_ZB, C_ZC, C_ABx = 3,4,6,14,15,16,20
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def hx(ab):
    c = ab[0] if ab else ''
    return HX_MAP.get(c, c)

def is_dieyun(zp):
    return zp.startswith('跌') and '反孕' in zp

def is_dietun(zp):
    return zp.startswith('跌') and '吞' in zp

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 验证1：己+前WTZB>0+跌孕 转甲（用 prevprev 判断前周WXZB）
    ji_qzb_n = 0; ji_qzb_zhuanjia = 0
    ji_qzb_dieyun_n = 0; ji_qzb_dieyun_zhuanjia = 0
    ji_qzb_dietun_n = 0; ji_qzb_dietun_zhuanjia = 0
    # 验证2：丙/乙(WXZA<0) 反弹向上，按 WXZC 正负分
    bing_yi_za_neg_n = 0; bing_yi_za_neg_hr3 = 0
    bing_yi_zc_neg_n = 0; bing_yi_zc_neg_hr3 = 0   # WXZC<0（风险区）
    bing_yi_zc_pos_n = 0; bing_yi_zc_pos_hr3 = 0   # WXZC>0（机会区）

    prev = None
    prevprev = None
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
                    prev = None; prevprev = None
                    continue
                try:
                    rec = {
                        'hr': float(parts[C_HR]) if parts[C_HR] else 0.0,
                        'ab': parts[C_AB], 'zp': parts[C_柱排],
                        'za': int(parts[C_ZA]), 'zb': int(parts[C_ZB]),
                        'zc': int(parts[C_ZC]), 'abx': int(parts[C_ABx]) if parts[C_ABx] else 0,
                    }
                except:
                    prev = None; prevprev = None
                    continue
                h = hx(rec['ab'])

                # 验证1：己+前WTZB>0+跌孕 转甲
                # 当前是甲 且 prev 是己 且 prevprev 的 WXZB>0 → prev 己转甲
                if h == '甲' and prev is not None and hx(prev['ab']) == '己' and prevprev is not None and prevprev['zb'] > 0:
                    ji_qzb_zhuanjia += 1
                    if is_dieyun(prev['zp']):
                        ji_qzb_dieyun_zhuanjia += 1
                    if is_dietun(prev['zp']):
                        ji_qzb_dietun_zhuanjia += 1
                # 当前是己 且 prev（己的前一周）的 WXZB>0 → 己+前WTZB>0
                if h == '己' and prev is not None and prev['zb'] > 0:
                    ji_qzb_n += 1
                    if is_dieyun(rec['zp']):
                        ji_qzb_dieyun_n += 1
                    if is_dietun(rec['zp']):
                        ji_qzb_dietun_n += 1

                # 验证2：丙/乙(WXZA<0) 反弹向上
                if h in ('丙', '乙') and rec['za'] < 0:
                    bing_yi_za_neg_n += 1
                    if rec['hr'] >= 3:
                        bing_yi_za_neg_hr3 += 1
                    if rec['zc'] < 0:
                        bing_yi_zc_neg_n += 1
                        if rec['hr'] >= 3:
                            bing_yi_zc_neg_hr3 += 1
                    else:
                        bing_yi_zc_pos_n += 1
                        if rec['hr'] >= 3:
                            bing_yi_zc_pos_hr3 += 1

                prevprev = prev
                prev = rec

    print("=" * 70)
    print(f"补充验证（{limit_files or '全量'}文件）")
    print("=" * 70)
    print("验证1：己+前WTZB>0+跌孕 转甲")
    print("-" * 70)
    if ji_qzb_n:
        print(f"己+前WTZB>0: n={ji_qzb_n}, 转甲: {ji_qzb_zhuanjia}, 率: {ji_qzb_zhuanjia/ji_qzb_n*100:.2f}%")
    if ji_qzb_dieyun_n:
        print(f"  其中跌孕: n={ji_qzb_dieyun_n}, 转甲: {ji_qzb_dieyun_zhuanjia}, 率: {ji_qzb_dieyun_zhuanjia/ji_qzb_dieyun_n*100:.2f}%")
    if ji_qzb_dietun_n:
        print(f"  其中跌吞: n={ji_qzb_dietun_n}, 转甲: {ji_qzb_dietun_zhuanjia}, 率: {ji_qzb_dietun_zhuanjia/ji_qzb_dietun_n*100:.2f}%")

    print()
    print("验证2：丙/乙(WXZA<0) 反弹向上（镜面对称）")
    print("-" * 70)
    if bing_yi_za_neg_n:
        print(f"丙/乙(WXZA<0) 整体: n={bing_yi_za_neg_n}, 下周HR>=3%: {bing_yi_za_neg_hr3/bing_yi_za_neg_n*100:.2f}%")
    if bing_yi_zc_neg_n:
        print(f"  WXZC<0(风险区): n={bing_yi_zc_neg_n}, 下周HR>=3%: {bing_yi_zc_neg_hr3/bing_yi_zc_neg_n*100:.2f}%")
    if bing_yi_zc_pos_n:
        print(f"  WXZC>0(机会区): n={bing_yi_zc_pos_n}, 下周HR>=3%: {bing_yi_zc_pos_hr3/bing_yi_zc_pos_n*100:.2f}%")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()