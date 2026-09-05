# -*- coding: utf-8 -*-
"""执念范围对比：DXZC<0 时，DXCD=中 vs 下 vs 忑 的探索
分析各CD的DXEF+DXZE分级，看是否有新发现。
用法: python c2_zhinian_compare.py [文件数]
输出: ____temp/c2_zhinian_compare_result.txt
"""
import io, sys, glob, os

OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_zhinian_compare_result.txt')
out_f = io.open(OUT_FILE, 'w', encoding='utf-8')
sys.stdout = out_f

N_FILES = int(sys.argv[1]) if len(sys.argv) > 1 else 7460
DATA_DIR = r'd:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'

files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:N_FILES]
print(f'处理 {len(files)} 个文件')

def new_stat():
    return {'n': 0, 'hr3': 0, 'sum_hr': 0.0}

# 对每个 CD(中/下/忑) 统计
stats = {
    'baseline': new_stat(),
    'by_cd': {},        # cd -> {'all':stat, 'by_ef':{}, 'by_ze':{}}
}

CDS = ['中', '下', '忑']
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

                stats['baseline']['n'] += 1
                stats['baseline']['hr3'] += hr3
                stats['baseline']['sum_hr'] += high

                # DXZC<0 时各 CD
                if p_zc <= 0 and p_cd in CDS:
                    if p_cd not in stats['by_cd']:
                        stats['by_cd'][p_cd] = {'all': new_stat(), 'by_ef': {}, 'by_ze': {}}
                    d = stats['by_cd'][p_cd]
                    d['all']['n'] += 1
                    d['all']['hr3'] += hr3
                    d['all']['sum_hr'] += high
                    if p_ef not in d['by_ef']:
                        d['by_ef'][p_ef] = new_stat()
                    d['by_ef'][p_ef]['n'] += 1
                    d['by_ef'][p_ef]['hr3'] += hr3
                    d['by_ef'][p_ef]['sum_hr'] += high
                    ze_key = 'ZE>0' if p_ze > 0 else 'ZE<=0'
                    if ze_key not in d['by_ze']:
                        d['by_ze'][ze_key] = new_stat()
                    d['by_ze'][ze_key]['n'] += 1
                    d['by_ze'][ze_key]['hr3'] += hr3
                    d['by_ze'][ze_key]['sum_hr'] += high

            prev = (cd, ab, zc, ze, ef)

print('\n========== DXZC<0 各CD探索结果 ==========')
def show(name, s):
    if s['n'] > 0:
        print(f'{name}: n={s["n"]}, 次日冲高>=3%={s["hr3"]/s["n"]*100:.2f}%, 平均高幅={s["sum_hr"]/s["n"]:.2f}%')
    else:
        print(f'{name}: n=0')

show('基线(所有样本)', stats['baseline'])

for cd in CDS:
    if cd in stats['by_cd']:
        d = stats['by_cd'][cd]
        print(f'\n--- DXZC<0 + DXCD={cd} ---')
        show(f'  {cd} 全部', d['all'])
        print(f'  按DXEF分级:')
        for ef in DXEF_ORDER:
            if ef in d['by_ef']:
                show(f'    {ef}', d['by_ef'][ef])
        print(f'  按DXZE分级:')
        for ze_key in ['ZE>0', 'ZE<=0']:
            if ze_key in d['by_ze']:
                show(f'    {ze_key}', d['by_ze'][ze_key])

out_f.close()
