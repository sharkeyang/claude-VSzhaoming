# -*- coding: utf-8 -*-
"""验证用户关于忠分类的提议"""
import csv

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
data = {}
for r in rows:
    data[(r['DXEF'], r['DXCD'], r['DXAB'])] = {'ze': float(r['→ZE>0']), 'zc': float(r['→ZE>0+ZC>0']), 'n': int(r['样本'])}

def get(ef, cd, ab):
    return data.get((ef, cd, ab))

# 嘘尿屎 + 忠 + 全部AB
print('='*70)
print('嘘尿屎+忠+全部AB (用户说应全部归F级)')
print('='*70)
print(f'{"EF":>4} {"CD":>4} {"AB":>4} {"AB好?":>6} {"→ZE>0":>8} {"→ZE+ZC":>8} {"样本":>10}')
print('-'*55)
for ef in ['嘘','尿','屎']:
    for ab in ['上','中','下','忐','忠','快']:
        pass
for ef in ['嘘','尿','屎']:
    for ab in ['上','中','下','忐','忠']:
        d = get(ef, '忠', ab)
        if d:
            ab_good = '是' if ab in ['上','中','忐'] else '否'
            print(f'{ef:>4} {"忠":>4} {ab:>4} {ab_good:>6} {d["ze"]:>7.1f}% {d["zc"]:>7.1f}% {d["n"]:>10,}')
    d = get(ef, '忠', chr(0x5FD1))
    if d:
        print(f'{ef:>4} {"忠":>4} {"忑":>4} {"否":>6} {d["ze"]:>7.1f}% {d["zc"]:>7.1f}% {d["n"]:>10,}')

# 嘘尿屎 + 下/忑 + AB好
print()
print('='*70)
print('嘘尿屎+下/忑+AB好 (用户说应归F级)')
print('='*70)
print(f'{"EF":>4} {"CD":>4} {"AB":>4} {"→ZE>0":>8} {"→ZE+ZC":>8} {"样本":>10}')
print('-'*55)
for ef in ['嘘','尿','屎']:
    for cd in ['下',chr(0x5FD1)]:
        for ab in ['上','中','忐']:
            d = get(ef, cd, ab)
            if d:
                print(f'{ef:>4} {cd:>4} {ab:>4} {d["ze"]:>7.1f}% {d["zc"]:>7.1f}% {d["n"]:>10,}')

# 嘘尿屎 + 下/忑 + AB差 (G级)
print()
print('='*70)
print('嘘尿屎+下/忑+AB差 (用户说应归G级禁止)')
print('='*70)
print(f'{"EF":>4} {"CD":>4} {"AB":>4} {"→ZE>0":>8} {"→ZE+ZC":>8} {"样本":>10}')
print('-'*55)
for ef in ['嘘','尿','屎']:
    for cd in ['下',chr(0x5FD1)]:
        for ab in ['下','忠',chr(0x5FD1)]:
            d = get(ef, cd, ab)
            if d:
                print(f'{ef:>4} {cd:>4} {ab:>4} {d["ze"]:>7.1f}% {d["zc"]:>7.1f}% {d["n"]:>10,}')

# 总结
print()
print('='*70)
print('结论')
print('='*70)
print()
print('1. 嘘/忠+全部AB: →ZE>0=8.6~49.7%, 跨度大')
print('   AB好(上/中/忐)平均: (35.4+13.5+49.7)/3=32.9%')
print('   AB差(下/忠/忑)平均: (8.6+25.1+12.8)/3=15.5%')
print('   差距17.4pp, AB好明显优于AB差')
print()
print('2. 尿/忠+全部AB: →ZE>0=1.6~14.9%, 全部<15%')
print('   所有AB值都很低, 归F级或G级无实质区别')
print()
print('3. 屎/忠+全部AB: →ZE>0=0.9~5.4%, 全部<5.4%')
print('   所有AB值极低, 归F级或G级无实质区别')
print()
print('→ 嘘/忠的情况有争议: AB好(32.9%) vs AB差(15.5%)')
print('→ 尿/忠和屎/忠无争议: 全部<15%')
print('→ 用户说\"DXZC>0时DXAB六种都可取\"在理论上是正确的')
print('→ 但实际数据中, 嘘/忠/中(13.5%)和嘘/忠/下(8.6%)仍然很低')
print('→ 建议: 嘘/忠归F级(AB好差不分), 尿/忠/屎/忠归G级')