# -*- coding: utf-8 -*-
"""查找四域定义需要更新的位置"""
import os

files = [
    '_主文档/昭明计划大局观体系.md',
    '_主文档/全局_C昭明路线图.md',
    '_主文档/全局_B交易体系.md',
    '昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas',
    '_主文档/MC3.3_研究日冲策略.md',
]

keywords = ['多长', '多被', '空看', '空长', '四域']

with open('____temp/四域分析.txt', 'w', encoding='utf-8') as out:
    for f in files:
        if not os.path.exists(f):
            out.write(f'{f}: 文件不存在\n')
            continue
        text = open(f, encoding='utf-8').read()
        found = False
        for i, line in enumerate(text.split('\n'), 1):
            for kw in keywords:
                if kw in line:
                    found = True
                    out.write(f'{f}:L{i}: {line.strip()[:100]}\n')
                    break
        if not found:
            out.write(f'{f}: 无相关引用\n')

print('Done')