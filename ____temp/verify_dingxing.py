# -*- coding: utf-8 -*-
"""验证用户贴的"日顶型操作细则"假设（修正版）
数据：谕组日 CSV（GBK，66列旧版）
列：[8]DXCD [9]DXAB [10]柱排 [13]日ZA [14]日ZC [26]次日高幅 [27]柱型 [30]上符串 [43]顶型 [44]等型 [52]t顶 [55]日龟顶触
"""
import os, glob, sys

DATA_DIR = r"d:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组1001\谕组日"
C_收, C_开, C_CD, C_AB, C_柱排, C_ZA, C_ZC, C_HR, C_柱型, C_上符, C_顶型, C_等型, C_t顶 = 1,2,8,9,10,13,14,26,27,30,43,44,52
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def hx(ab):
    c = ab[0] if ab else ''
    return HX_MAP.get(c, c)

def is_yang(rec):
    try:
        return rec['收'] > rec['开']
    except:
        return None

def is_chuding(sf):
    return sf and sf[-1] == 'A'

def parse_td(td):
    """解析 t顶：G83→83, _1→-1, _0→0"""
    if not td:
        return 0
    if td.startswith('_'):
        try:
            return -int(td[1:])
        except:
            return 0
    if td.startswith('G'):
        try:
            return int(td[1:])
        except:
            return 0
    try:
        return int(td)
    except:
        return 0

def main(limit_files=None):
    files = glob.glob(os.path.join(DATA_DIR, "谕组日_*.csv"))
    if limit_files:
        files = files[:limit_files]

    # 基线：主升区触顶 次日继续触顶
    base_chuding_n = 0; base_chuding_next = 0
    # 龙a 连续触顶
    longa_n = 0; longa_next_chuding = 0
    # 龙a+跌吞 次日触顶
    longa_dietun_n = 0; longa_dietun_next = 0
    # 龙a+冲高（柱型含冲）次日触顶
    longa_chong_n = 0; longa_chong_next = 0
    # 龙b 次日触顶（prev 是龙b，当前触顶）
    longb_n = 0; longb_next_chuding = 0
    # t顶<=-3 次日高幅
    tneg3_n = 0; tneg3_hr3 = 0

    prev = None
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
                if len(parts) < 66:
                    prev = None
                    continue
                try:
                    rec = {
                        '收': float(parts[C_收]), '开': float(parts[C_开]),
                        'cd': parts[C_CD], 'ab': parts[C_AB], 'zp': parts[C_柱排],
                        'za': int(parts[C_ZA]), 'zc': int(parts[C_ZC]),
                        'hr': float(parts[C_HR]) if parts[C_HR] else 0.0,
                        'zx': parts[C_柱型], 'sf': parts[C_上符], 'dx': parts[C_顶型],
                        'deng': parts[C_等型], 'td': parse_td(parts[C_t顶]),
                    }
                except:
                    prev = None
                    continue
                h = hx(rec['ab'])
                cur_chuding = is_chuding(rec['sf'])

                # 主升区
                if rec['cd'] in ('上', '忐') and rec['zc'] > 0:
                    # 基线：触顶 次日继续触顶（当前触顶 且 prev 触顶 → prev 次日触顶）
                    if cur_chuding:
                        base_chuding_n += 1
                        if prev is not None and is_chuding(prev['sf']):
                            base_chuding_next += 1

                    # 龙a 连续触顶
                    if 'a龙' in rec['dx']:
                        longa_n += 1
                        if cur_chuding and prev is not None and is_chuding(prev['sf']):
                            longa_next_chuding += 1
                        # 龙a+跌吞
                        if rec['zp'].startswith('跌') and '吞' in rec['zp']:
                            longa_dietun_n += 1
                            if cur_chuding and prev is not None and is_chuding(prev['sf']):
                                longa_dietun_next += 1
                        # 龙a+冲高（柱型含冲）
                        if '冲' in rec['zx']:
                            longa_chong_n += 1
                            if cur_chuding and prev is not None and is_chuding(prev['sf']):
                                longa_chong_next += 1

                    # 龙b 次日触顶（prev 是龙b，当前触顶）
                    if prev is not None and 'b龙' in prev['dx']:
                        longb_n += 1
                        if cur_chuding:
                            longb_next_chuding += 1

                    # t顶<=-3 次日高幅
                    if rec['td'] <= -3:
                        tneg3_n += 1
                        if rec['hr'] >= 3:
                            tneg3_hr3 += 1

                prev = rec

    print("=" * 70)
    print(f"验证：日顶型操作细则（{limit_files or '全量'}文件）")
    print("=" * 70)
    if base_chuding_n:
        print(f"基线（主升区触顶）: n={base_chuding_n}, 次日继续触顶: {base_chuding_next}, 率: {base_chuding_next/base_chuding_n*100:.2f}%")
    print()
    if longa_n:
        print(f"触顶龙a: n={longa_n}, 次日继续触顶: {longa_next_chuding}, 率: {longa_next_chuding/longa_n*100:.2f}%")
    if longa_dietun_n:
        print(f"  龙a+跌吞: n={longa_dietun_n}, 次日继续触顶: {longa_dietun_next}, 率: {longa_dietun_next/longa_dietun_n*100:.2f}%")
    if longa_chong_n:
        print(f"  龙a+冲高(柱型含冲): n={longa_chong_n}, 次日继续触顶: {longa_chong_next}, 率: {longa_chong_next/longa_chong_n*100:.2f}%")
    print()
    if longb_n:
        print(f"触顶龙b: n={longb_n}, 次日触顶: {longb_next_chuding}, 率: {longb_next_chuding/longb_n*100:.2f}%")
    print()
    if tneg3_n:
        print(f"t顶<=-3: n={tneg3_n}, 次日高幅>=3%: {tneg3_hr3/tneg3_n*100:.2f}%")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(limit_files=int(sys.argv[1]))
    else:
        main()