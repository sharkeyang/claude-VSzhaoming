# -*- coding: utf-8 -*-
"""验证用户贴的"护型日机"假设（全量，稳健读取）
数据：谕组日 CSV（GBK，66列旧版）
列：[8]DXCD [9]DXAB [10]柱排 [13]日ZA [14]日ZC [26]次日高幅 [44]日等型 [64]DTAB
"""
import os, glob, sys

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组日"
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def hx(ab):
    c = ab[0] if ab else ''
    return HX_MAP.get(c, c)

def is_yang(rec):
    try:
        return rec['收'] > rec['开']
    except:
        return None

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组日_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 统计
    base_n = 0; base_hr3 = 0
    jia_yin_total = 0; jia_yin_zy = 0
    other_yin_total = 0; other_yin_zy = 0
    deng3_n = 0; deng3_hr3 = 0
    deng3_dieyun_n = 0; deng3_dieyun_hr3 = 0
    deng3_dietun_n = 0; deng3_dietun_hr3 = 0
    yi_za1_n = 0; yi_za1_hr3 = 0
    other_za1_n = 0; other_za1_hr3 = 0
    ji_n = 0; ji_zhuanjia = 0

    prev = None
    for fp in files:
        try:
            f = open(fp, encoding='gbk', errors='ignore')
        except Exception as e:
            print(f"SKIP {fp}: {e}", file=sys.stderr)
            continue
        with f:
            f.readline()  # 表头
            for line in f:
                parts = line.rstrip('\n').split(',')
                if len(parts) < 66:
                    prev = None
                    continue
                # 解析当前行
                try:
                    rec = {
                        '收': float(parts[1]), '开': float(parts[2]),
                        'cd': parts[8], 'ab': parts[9], 'zp': parts[10],
                        'za': int(parts[13]), 'zc': int(parts[14]),
                        'hr': float(parts[26]) if parts[26] else 0.0,
                        'deng': parts[44], 'dtab': int(parts[64]) if parts[64] else 0,
                    }
                except:
                    prev = None
                    continue
                h = hx(rec['ab'])
                yang = is_yang(rec)

                # 基线
                base_n += 1
                if rec['hr'] >= 3:
                    base_hr3 += 1

                # 主升区
                if rec['cd'] in ('上', '忐') and rec['zc'] > 0:
                    # 甲阴柱后转阳 vs 其他
                    if yang is False:
                        if h == '甲':
                            jia_yin_total += 1
                        else:
                            other_yin_total += 1
                    if yang is True and prev is not None and is_yang(prev) is False:
                        if hx(prev['ab']) == '甲':
                            jia_yin_zy += 1
                        else:
                            other_yin_zy += 1

                    # 等3
                    if rec['deng'] == '等3' and h in ('甲', '乙', '己'):
                        deng3_n += 1
                        if rec['hr'] >= 3:
                            deng3_hr3 += 1
                        if rec['zp'].startswith('跌') and '反孕' in rec['zp']:
                            deng3_dieyun_n += 1
                            if rec['hr'] >= 3:
                                deng3_dieyun_hr3 += 1
                        if rec['zp'].startswith('跌') and '吞' in rec['zp']:
                            deng3_dietun_n += 1
                            if rec['hr'] >= 3:
                                deng3_dietun_hr3 += 1

                    # 乙日ZA=1 vs 其他
                    if rec['za'] == 1:
                        if h == '乙':
                            yi_za1_n += 1
                            if rec['hr'] >= 3:
                                yi_za1_hr3 += 1
                        else:
                            other_za1_n += 1
                            if rec['hr'] >= 3:
                                other_za1_hr3 += 1

                    # 己转甲
                    if h == '己':
                        ji_n += 1
                    if h == '甲' and prev is not None and hx(prev['ab']) == '己':
                        ji_zhuanjia += 1

                prev = rec

    print("=" * 70)
    print(f"基线：全样本 次日高幅>=3% 率（{limit_files or '全量'}文件）")
    print("=" * 70)
    print(f"全样本: n={base_n}, >=3%: {base_hr3/base_n*100:.2f}%" if base_n else "n=0")

    print()
    print("=" * 70)
    print("验证组1：甲阴柱后转阳特权")
    print("=" * 70)
    if jia_yin_total:
        print(f"甲阴柱: n={jia_yin_total}, 后转阳: {jia_yin_zy}, 转阳率: {jia_yin_zy/jia_yin_total*100:.2f}%")
    if other_yin_total:
        print(f"其他护型阴柱: n={other_yin_total}, 后转阳: {other_yin_zy}, 转阳率: {other_yin_zy/other_yin_total*100:.2f}%")

    print()
    print("=" * 70)
    print("验证组：等3跌孕/跌吞 vs 等3整体")
    print("=" * 70)
    if deng3_n:
        print(f"等3整体: n={deng3_n}, >=3%: {deng3_hr3/deng3_n*100:.2f}%")
    if deng3_dieyun_n:
        print(f"等3跌孕: n={deng3_dieyun_n}, >=3%: {deng3_dieyun_hr3/deng3_dieyun_n*100:.2f}%")
    if deng3_dietun_n:
        print(f"等3跌吞: n={deng3_dietun_n}, >=3%: {deng3_dietun_hr3/deng3_dietun_n*100:.2f}%")

    print()
    print("=" * 70)
    print("验证组2：乙日ZA=1（刚上破DJA）vs 其他护型")
    print("=" * 70)
    if yi_za1_n:
        print(f"乙日ZA=1: n={yi_za1_n}, >=3%: {yi_za1_hr3/yi_za1_n*100:.2f}%")
    if other_za1_n:
        print(f"其他护型日ZA=1: n={other_za1_n}, >=3%: {other_za1_hr3/other_za1_n*100:.2f}%")

    print()
    print("=" * 70)
    print("验证组3：己转甲")
    print("=" * 70)
    if ji_n:
        print(f"己总数: n={ji_n}, 次日转甲: {ji_zhuanjia}, 转甲率: {ji_zhuanjia/ji_n*100:.2f}%")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()