# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
fp = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with io.open(fp, encoding='utf-8') as f:
    txt = f.read()
lines = txt.split(chr(10))

# 按章节范围修正加粗子节标题编号
boundaries = []
for i,l in enumerate(lines):
    m = re.match(r'^## ([一二三四五六七八])、', l)
    if m:
        boundaries.append((i, m.group(1)))

def get_ch(i):
    ch = None
    for bi, name in boundaries:
        if bi <= i:
            ch = name
        else:
            break
    return ch

result = []
for i,l in enumerate(lines):
    ch = get_ch(i)
    m = re.match(r'^\*\*(\d+)\.(\d+)(\.\d+)*\s', l)
    if m and ch:
        if ch == '二':  # 护型分析
            if l.startswith('**3.3.1.3 '):
                l = l.replace('**3.3.1.3 ', '**2.9.3 ', 1)
        elif ch == '三':  # 等型分析
            if l.startswith('**2.4.2.11.1 '): l = l.replace('**2.4.2.11.1 ', '**3.3.2.11.1 ', 1)
            elif l.startswith('**2.4.2.11.3 '): l = l.replace('**2.4.2.11.3 ', '**3.3.2.11.3 ', 1)
            elif l.startswith('**2.4.2.11 '): l = l.replace('**2.4.2.11 ', '**3.3.2.11 ', 1)
            elif l.startswith('**2.4.2.1 '): l = l.replace('**2.4.2.1 ', '**3.3.2.1 ', 1)
            elif l.startswith('**2.4.2.2 '): l = l.replace('**2.4.2.2 ', '**3.3.2.2 ', 1)
            elif l.startswith('**2.4.2.3 '): l = l.replace('**2.4.2.3 ', '**3.3.2.3 ', 1)
            elif l.startswith('**2.4.2.4 '): l = l.replace('**2.4.2.4 ', '**3.3.2.4 ', 1)
            elif l.startswith('**2.4.2.5 '): l = l.replace('**2.4.2.5 ', '**3.3.2.5 ', 1)
            elif l.startswith('**2.4.2.6 '): l = l.replace('**2.4.2.6 ', '**3.3.2.6 ', 1)
            elif l.startswith('**2.4.2.7 '): l = l.replace('**2.4.2.7 ', '**3.3.2.7 ', 1)
            elif l.startswith('**2.4.2.8 '): l = l.replace('**2.4.2.8 ', '**3.3.2.8 ', 1)
            elif l.startswith('**2.4.3.1 '): l = l.replace('**2.4.3.1 ', '**3.3.3.1 ', 1)
            elif l.startswith('**2.4.3.2 '): l = l.replace('**2.4.3.2 ', '**3.3.3.2 ', 1)
            elif l.startswith('**2.4.3.3 '): l = l.replace('**2.4.3.3 ', '**3.3.3.3 ', 1)
            elif l.startswith('**2.4.3.4 '): l = l.replace('**2.4.3.4 ', '**3.3.3.4 ', 1)
            elif l.startswith('**2.7.2 '): l = l.replace('**2.7.2 ', '**3.6.2 ', 1)
        elif ch == '四':  # DXAB正交动力学
            if l.startswith('**3.2.1 '): l = l.replace('**3.2.1 ', '**4.2.1 ', 1)
            elif l.startswith('**3.4.3.1 '): l = l.replace('**3.4.3.1 ', '**4.4.3.1 ', 1)
            elif l.startswith('**3.4.1 '): l = l.replace('**3.4.1 ', '**4.4.1 ', 1)
            elif l.startswith('**3.4.2 '): l = l.replace('**3.4.2 ', '**4.4.2 ', 1)
            elif l.startswith('**3.4.3 '): l = l.replace('**3.4.3 ', '**4.4.3 ', 1)
            elif l.startswith('**3.4.4 '): l = l.replace('**3.4.4 ', '**4.4.4 ', 1)
            elif l.startswith('**3.4.5 '): l = l.replace('**3.4.5 ', '**4.4.5 ', 1)
            elif l.startswith('**3.4.6 '): l = l.replace('**3.4.6 ', '**4.4.6 ', 1)
            elif l.startswith('**3.5.1 '): l = l.replace('**3.5.1 ', '**4.5.1 ', 1)
            elif l.startswith('**3.5.2 '): l = l.replace('**3.5.2 ', '**4.5.2 ', 1)
            elif l.startswith('**3.5.3 '): l = l.replace('**3.5.3 ', '**4.5.3 ', 1)
            elif l.startswith('**3.5.4 '): l = l.replace('**3.5.4 ', '**4.5.4 ', 1)
            elif l.startswith('**3.5.5 '): l = l.replace('**3.5.5 ', '**4.5.5 ', 1)
            elif l.startswith('**3.6.1 '): l = l.replace('**3.6.1 ', '**4.6.1 ', 1)
            elif l.startswith('**3.6.2 '): l = l.replace('**3.6.2 ', '**4.6.2 ', 1)
            elif l.startswith('**3.6.3 '): l = l.replace('**3.6.3 ', '**4.6.3 ', 1)
            elif l.startswith('**3.6.4 '): l = l.replace('**3.6.4 ', '**4.6.4 ', 1)
            elif l.startswith('**3.6.5 '): l = l.replace('**3.6.5 ', '**4.6.5 ', 1)
            elif l.startswith('**3.7.2.1 '): l = l.replace('**3.7.2.1 ', '**4.7.2.1 ', 1)
            elif l.startswith('**3.7.2.2 '): l = l.replace('**3.7.2.2 ', '**4.7.2.2 ', 1)
            elif l.startswith('**3.7.2.3 '): l = l.replace('**3.7.2.3 ', '**4.7.2.3 ', 1)
            elif l.startswith('**3.7.1 '): l = l.replace('**3.7.1 ', '**4.7.1 ', 1)
            elif l.startswith('**3.7.2 '): l = l.replace('**3.7.2 ', '**4.7.2 ', 1)
            elif l.startswith('**3.7.3 '): l = l.replace('**3.7.3 ', '**4.7.3 ', 1)
            elif l.startswith('**3.7.4 '): l = l.replace('**3.7.4 ', '**4.7.4 ', 1)
        elif ch == '五':  # 柱与DJA三态理论
            if l.startswith('**2.9.2.1 '): l = l.replace('**2.9.2.1 ', '**5.1.2.1 ', 1)
            elif l.startswith('**2.9.4.1 '): l = l.replace('**2.9.4.1 ', '**5.1.4.1 ', 1)
            elif l.startswith('**2.9.4.2 '): l = l.replace('**2.9.4.2 ', '**5.1.4.2 ', 1)
            elif l.startswith('**2.10.7.1 '): l = l.replace('**2.10.7.1 ', '**5.2.7.1 ', 1)
            elif l.startswith('**2.10.7.2 '): l = l.replace('**2.10.7.2 ', '**5.2.7.2 ', 1)
            elif l.startswith('**2.10.8.1 '): l = l.replace('**2.10.8.1 ', '**5.2.8.1 ', 1)
            elif l.startswith('**2.10.8.2 '): l = l.replace('**2.10.8.2 ', '**5.2.8.2 ', 1)
            elif l.startswith('**2.10.8.3 '): l = l.replace('**2.10.8.3 ', '**5.2.8.3 ', 1)
            elif l.startswith('**2.10.8.4 '): l = l.replace('**2.10.8.4 ', '**5.2.8.4 ', 1)
            elif l.startswith('**2.10.8.5 '): l = l.replace('**2.10.8.5 ', '**5.2.8.5 ', 1)
            elif l.startswith('**2.10.8.6 '): l = l.replace('**2.10.8.6 ', '**5.2.8.6 ', 1)
        elif ch == '六':  # 操盘计划
            if l.startswith('**4.7.9.1 '): l = l.replace('**4.7.9.1 ', '**6.7.9.1 ', 1)
            elif l.startswith('**4.7.9.2 '): l = l.replace('**4.7.9.2 ', '**6.7.9.2 ', 1)
            elif l.startswith('**4.7.9.3 '): l = l.replace('**4.7.9.3 ', '**6.7.9.3 ', 1)
            elif l.startswith('**4.7.9.4 '): l = l.replace('**4.7.9.4 ', '**6.7.9.4 ', 1)
            elif l.startswith('**4.7.9.5 '): l = l.replace('**4.7.9.5 ', '**6.7.9.5 ', 1)
            elif l.startswith('**4.7.9 '): l = l.replace('**4.7.9 ', '**6.7.9 ', 1)
            elif l.startswith('**4.7.8.1 '): l = l.replace('**4.7.8.1 ', '**6.7.8.1 ', 1)
            elif l.startswith('**4.7.8.2 '): l = l.replace('**4.7.8.2 ', '**6.7.8.2 ', 1)
            elif l.startswith('**4.7.8.3 '): l = l.replace('**4.7.8.3 ', '**6.7.8.3 ', 1)
            elif l.startswith('**4.7.8.4 '): l = l.replace('**4.7.8.4 ', '**6.7.8.4 ', 1)
            elif l.startswith('**4.7.8 '): l = l.replace('**4.7.8 ', '**6.7.8 ', 1)
            elif l.startswith('**4.7.1 '): l = l.replace('**4.7.1 ', '**6.7.1 ', 1)
            elif l.startswith('**4.7.2 '): l = l.replace('**4.7.2 ', '**6.7.2 ', 1)
            elif l.startswith('**4.7.3 '): l = l.replace('**4.7.3 ', '**6.7.3 ', 1)
            elif l.startswith('**4.7.4 '): l = l.replace('**4.7.4 ', '**6.7.4 ', 1)
            elif l.startswith('**4.7.5 '): l = l.replace('**4.7.5 ', '**6.7.5 ', 1)
            elif l.startswith('**4.7.6 '): l = l.replace('**4.7.6 ', '**6.7.6 ', 1)
            elif l.startswith('**4.7.7 '): l = l.replace('**4.7.7 ', '**6.7.7 ', 1)
        elif ch == '七':  # 周级别+微观指标
            if l.startswith('**4.9.2.1 '): l = l.replace('**4.9.2.1 ', '**7.1.2.1 ', 1)
            elif l.startswith('**4.9.2.2 '): l = l.replace('**4.9.2.2 ', '**7.1.2.2 ', 1)
            elif l.startswith('**4.9.2.3 '): l = l.replace('**4.9.2.3 ', '**7.1.2.3 ', 1)
            elif l.startswith('**4.9.2.4 '): l = l.replace('**4.9.2.4 ', '**7.1.2.4 ', 1)
            elif l.startswith('**4.9.2 '): l = l.replace('**4.9.2 ', '**7.1.2 ', 1)
            elif l.startswith('**4.9.1.1 '): l = l.replace('**4.9.1.1 ', '**7.1.1.1 ', 1)
            elif l.startswith('**4.9.1.2 '): l = l.replace('**4.9.1.2 ', '**7.1.1.2 ', 1)
            elif l.startswith('**4.9.1 '): l = l.replace('**4.9.1 ', '**7.1.1 ', 1)
            elif l.startswith('**4.10.4.1 '): l = l.replace('**4.10.4.1 ', '**7.2.4.1 ', 1)
            elif l.startswith('**4.10.4.2 '): l = l.replace('**4.10.4.2 ', '**7.2.4.2 ', 1)
            elif l.startswith('**4.10.4.3 '): l = l.replace('**4.10.4.3 ', '**7.2.4.3 ', 1)
            elif l.startswith('**4.10.4.4 '): l = l.replace('**4.10.4.4 ', '**7.2.4.4 ', 1)
            elif l.startswith('**4.10.4 '): l = l.replace('**4.10.4 ', '**7.2.4 ', 1)
            elif l.startswith('**4.10.3.1 '): l = l.replace('**4.10.3.1 ', '**7.2.3.1 ', 1)
            elif l.startswith('**4.10.3.2 '): l = l.replace('**4.10.3.2 ', '**7.2.3.2 ', 1)
            elif l.startswith('**4.10.3.3 '): l = l.replace('**4.10.3.3 ', '**7.2.3.3 ', 1)
            elif l.startswith('**4.10.3 '): l = l.replace('**4.10.3 ', '**7.2.3 ', 1)
            elif l.startswith('**4.10.1.1 '): l = l.replace('**4.10.1.1 ', '**7.2.1.1 ', 1)
            elif l.startswith('**4.10.1.2 '): l = l.replace('**4.10.1.2 ', '**7.2.1.2 ', 1)
            elif l.startswith('**4.10.1.3 '): l = l.replace('**4.10.1.3 ', '**7.2.1.3 ', 1)
            elif l.startswith('**4.10.1 '): l = l.replace('**4.10.1 ', '**7.2.1 ', 1)
            elif l.startswith('**4.10.2 '): l = l.replace('**4.10.2 ', '**7.2.2 ', 1)
            elif l.startswith('**4.10.5 '): l = l.replace('**4.10.5 ', '**7.2.5 ', 1)
            elif l.startswith('**4.10.6 '): l = l.replace('**4.10.6 ', '**7.2.6 ', 1)
            elif l.startswith('**4.10.7 '): l = l.replace('**4.10.7 ', '**7.2.7 ', 1)
    result.append(l)

with io.open(fp, 'w', encoding='utf-8') as f:
    f.write('\n'.join(result))
print('所有加粗子节标题编号修正完成')
