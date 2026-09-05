# -*- coding: utf-8 -*-
"""执念范围探索：DXZC<0 + DXCD=中 的日类操作范围
分析 DXEF+DXZE 分级，看什么等级可用，是否必须在主升浪。
用法: python c2_zhinian_validate.py [文件数]
输出: ____temp/c2_zhinian_validate_result.txt
"""
import io, sys, glob, os

# 输出重定向到文件（UTF-8）
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_zhinian_validate_result.txt')
out_f = io.open(OUT_FILE, 'w', encoding='utf-8')
sys.stdout = out_f

N_FILES = int(sys.argv[1]) if len(sys.argv) > 1 else 7460
DATA_DIR = r'd:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'

files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:N_FILES]
print(f'处理 {len(files)} 个文件')

def new_stat():
    return {'n': 0, 'hr3': 0, 'sum_hr': 0.0}

# 执念范围：DXZC<0 + DXCD=中
stats = {
    'zhinian_all': new_stat(),      # 执念范围全部
    'zhinian_by_ef': {},            # 执念范围按 DXEF 分级
    'zhinian_by_ze': {},            # 执念范围按 DXZE 分级
    'baseline': new_stat(),         # 基线
    'zhinian_ab_good': new_stat(),  # 执念范围 + AB甲乙己
}

DXEF_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

for fname in files:
    with open(fname, 'rb') as f:
        f.readline()
        prev = None
        for raw in f:
            row = raw.decode('gbk').strip().split(',')
            if len(row) < 51: continue
            cd = row[8]
            ab = row[9]
            try: zc = int(row[14])
            except: zc = 0
            try: ze = int(row[15])
            except: ze = 0
            ef = row[50][1] if len(row[50]) > 1 else '?'
            try: high = float(row[6])
            except: high = 0.0

            if prev is not None:
                p_cd, p_ab, p_zc, p_ze, p_ef = prev
                if high < -50 or high > 50:
                    prev = (cd, ab, zc, ze, ef); continue
                hr3 = 1 if high >= 3 else 0

                # 基线
                stats['baseline']['n'] += 1
                stats['baseline']['hr3'] += hr3
                stats['baseline']['sum_hr'] += high

                # 执念范围：DXZC<0 + DXCD=中
                if p_zc <= 0 and p_cd == '中':
                    stats['zhinian_all']['n'] += 1
                    stats['zhinian_all']['hr3'] += hr3
                    stats['zhinian_all']['sum_hr'] += high
                    # 按 DXEF 分级
                    if p_ef not in stats['zhinian_by_ef']:
                        stats['zhinian_by_ef'][p_ef] = new_stat()
                    stats['zhinian_by_ef'][p_ef]['n'] += 1
                    stats['zhinian_by_ef'][p_ef]['hr3'] += hr3
                    stats['zhinian_by_ef'][p_ef]['sum_hr'] += high
                    # 按 DXZE 分级
                    ze_key = 'ZE>0' if p_ze > 0 else 'ZE<=0'
                    if ze_key not in stats['zhinian_by_ze']:
                        stats['zhinian_by_ze'][ze_key] = new_stat()
                    stats['zhinian_by_ze'][ze_key]['n'] += 1
                    stats['zhinian_by_ze'][ze_key]['hr3'] += hr3
                    stats['zhinian_by_ze'][ze_key]['sum_hr'] += high
                    # 执念范围 + AB甲乙己
                    if p_ab.startswith('a') or p_ab.startswith('b') or p_ab.startswith('r'):
                        stats['zhinian_ab_good']['n'] += 1
                        stats['zhinian_ab_good']['hr3'] += hr3
                        stats['zhinian_ab_good']['sum_hr'] += high

            prev = (cd, ab, zc, ze, ef)

print('\n========== 执念范围探索结果 ==========')
def show(name, s):
    if s['n'] > 0:
        print(f'{name}: n={s["n"]}, 次日冲高>=3%={s["hr3"]/s["n"]*100:.2f}%, 平均次日高幅={s["sum_hr"]/s["n"]:.2f}%')
    else:
        print(f'{name}: n=0')

print('\n--- 基线 ---')
show('基线(所有样本)', stats['baseline'])

print('\n--- 执念范围 (DXZC<0 + DXCD=中) ---')
show('执念范围全部', stats['zhinian_all'])
show('执念范围 + AB甲乙己', stats['zhinian_ab_good'])

print('\n--- 执念范围按 DXEF 分级 ---')
for ef in DXEF_ORDER:
    if ef in stats['zhinian_by_ef']:
        show(f'  {ef}', stats['zhinian_by_ef'][ef])

print('\n--- 执念范围按 DXZE 分级 ---')
for ze_key in ['ZE>0', 'ZE<=0']:
    if ze_key in stats['zhinian_by_ze']:
        show(f'  {ze_key}', stats['zhinian_by_ze'][ze_key])