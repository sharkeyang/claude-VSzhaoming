# -*- coding: utf-8 -*-
"""C2第四章数据验证脚本：融合后范围/范围×等级/G级特例/初始介入回测
用法: python c2_ch4_validate.py [文件数]  (默认全量)
输出: ____temp/c2_ch4_validate_result.txt
"""
import io, sys, glob, os

# 输出重定向到文件（UTF-8）
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_ch4_validate_result.txt')
out_f = io.open(OUT_FILE, 'w', encoding='utf-8')
sys.stdout = out_f

# 参数
N_FILES = int(sys.argv[1]) if len(sys.argv) > 1 else 7460
DATA_DIR = r'd:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'

files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:N_FILES]
print(f'处理 {len(files)} 个文件')

# 统计容器: {key: {'n':样本数, 'hr3':次日冲高>=3%次数, 'sum_hr':次日冲高总和}}
def new_stat():
    return {'n': 0, 'hr3': 0, 'sum_hr': 0.0}

stats = {
    'baseline': new_stat(),          # 基线：所有样本
    'range': new_stat(),             # 融合后范围：ZC>0 + CD上/忐 + 乙(ZA>0)/甲
    'range_grade': {},               # 范围×等级：range内按DXEF分级
    'g_special': new_stat(),         # G级特例：CD<0 + ZC>0
    'init': new_stat(),              # 初始介入：ZC>0 + CD甲乙己戊 + AB甲乙己
    'single_zc': new_stat(),         # 单维：仅ZC>0
    'single_cd': new_stat(),         # 单维：仅CD上/忐
    'single_ab': new_stat(),         # 单维：仅乙(ZA>0)/甲
}

# DXEF 六值
DXEF_ORDER = ['金', '银', '唏', '嘘', '尿', '屎']

for fname in files:
    with open(fname, 'rb') as f:
        f.readline()  # 表头
        prev = None  # (cd, ab, zc, ze, ef)
        for raw in f:
            row = raw.decode('gbk').strip().split(',')
            if len(row) < 51:
                continue
            cd = row[8]
            ab = row[9]
            try:
                zc = int(row[14])
            except:
                zc = 0
            try:
                ze = int(row[15])
            except:
                ze = 0
            ef = row[50][1] if len(row[50]) > 1 else '?'
            try:
                high = float(row[6])  # 当日高幅
            except:
                high = 0.0

            # 次日冲高 = 当前行高幅（对上一行而言）
            if prev is not None:
                p_cd, p_ab, p_zc, p_ze, p_ef = prev
                # 过滤异常高幅（停牌/异常）
                if high < -50 or high > 50:
                    prev = (cd, ab, zc, ze, ef)
                    continue
                hr3 = 1 if high >= 3 else 0

                # 基线
                stats['baseline']['n'] += 1
                stats['baseline']['hr3'] += hr3
                stats['baseline']['sum_hr'] += high

                # 单维
                if p_zc > 0:
                    stats['single_zc']['n'] += 1
                    stats['single_zc']['hr3'] += hr3
                    stats['single_zc']['sum_hr'] += high
                if p_cd in ('上', '忐'):
                    stats['single_cd']['n'] += 1
                    stats['single_cd']['hr3'] += hr3
                    stats['single_cd']['sum_hr'] += high
                if p_ab.startswith('a') or p_ab.startswith('b'):
                    stats['single_ab']['n'] += 1
                    stats['single_ab']['hr3'] += hr3
                    stats['single_ab']['sum_hr'] += high

                # 融合后范围：ZC>0 + CD上/忐 + 乙(ZA>0)/甲
                ab_ok = p_ab.startswith('a') or p_ab.startswith('b')
                cd_ok = p_cd in ('上', '忐')
                if p_zc > 0 and cd_ok and ab_ok:
                    stats['range']['n'] += 1
                    stats['range']['hr3'] += hr3
                    stats['range']['sum_hr'] += high
                    # 范围×等级
                    if p_ef not in stats['range_grade']:
                        stats['range_grade'][p_ef] = new_stat()
                    stats['range_grade'][p_ef]['n'] += 1
                    stats['range_grade'][p_ef]['hr3'] += hr3
                    stats['range_grade'][p_ef]['sum_hr'] += high

                # G级特例：CD=忠（BTCD≤0 但 ZC>0，即"CD<0+ZC>0"）+ DXEF嘘尿屎
                # 注：CD护级与ZC完全共线（上/忐/忠→ZC>0，中/下/忑→ZC≤0），
                #     "CD<0+ZC>0" = CD=忠（BTCD≤0但BTZC>0）
                if p_cd == '忠' and p_ef in ('嘘', '尿', '屎'):
                    stats['g_special']['n'] += 1
                    stats['g_special']['hr3'] += hr3
                    stats['g_special']['sum_hr'] += high

                # 初始介入：ZC>0 + CD甲乙己戊 + AB甲乙己
                cd_ok2 = p_cd in ('上', '中', '下', '忐', '忠', '忑')  # CD甲乙己戊(所有CD)
                ab_ok2 = p_ab.startswith('a') or p_ab.startswith('b') or p_ab.startswith('r')  # 甲乙己
                if p_zc > 0 and cd_ok2 and ab_ok2:
                    stats['init']['n'] += 1
                    stats['init']['hr3'] += hr3
                    stats['init']['sum_hr'] += high

            prev = (cd, ab, zc, ze, ef)

# 输出
print('\n========== 验证结果 ==========')
def show(name, s):
    if s['n'] > 0:
        print(f'{name}: n={s["n"]}, 次日冲高>=3%={s["hr3"]/s["n"]*100:.2f}%, 平均次日高幅={s["sum_hr"]/s["n"]:.2f}%')
    else:
        print(f'{name}: n=0')

print('\n--- 1. 融合后范围验证 ---')
show('基线(所有样本)', stats['baseline'])
show('融合后范围(ZC>0+CD上/忐+乙甲)', stats['range'])

print('\n--- 2. 范围×等级联合验证 ---')
show('  单维: 仅ZC>0', stats['single_zc'])
show('  单维: 仅CD上/忐', stats['single_cd'])
show('  单维: 仅乙(ZA>0)/甲', stats['single_ab'])
print('  范围内按DXEF分级:')
for ef in DXEF_ORDER:
    if ef in stats['range_grade']:
        show(f'    {ef}', stats['range_grade'][ef])

print('\n--- 3. G级特例验证 (CD<0 + ZC>0) ---')
show('G级特例', stats['g_special'])

print('\n--- 4. 初始介入回测 ---')
show('初始介入(ZC>0+CD甲乙己戊+AB甲乙己)', stats['init'])