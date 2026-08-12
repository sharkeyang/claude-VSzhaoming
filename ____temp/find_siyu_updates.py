# -*- coding: utf-8 -*-
"""查找所有需要更新的四域定义"""
import os

docs = [
    '_主文档/MC3.1_研究月基策略.md',
    '_主文档/全局_B交易体系.md',
    '_主文档/全局_C昭明路线图.md',
    '_主文档/MC3.3_研究日冲策略.md',
    '昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas',
]

with open('____temp/四域更新清单.txt', 'w', encoding='utf-8') as out:
    for doc in docs:
        if not os.path.exists(doc):
            out.write(f'{doc}: 文件不存在\n')
            continue
        text = open(doc, encoding='utf-8').read()
        lines = text.split('\n')
        out.write(f'\n{doc}:\n')
        for i, line in enumerate(lines, 1):
            # 四域定义表
            if '多长' in line and ('ZC' in line or 'WXZC' in line or '>0' in line):
                if '多长' in line and '多被' not in line:
                    out.write(f'  L{i}: {line.strip()[:100]}\n')
            # 多被(唏) 缺失检查
            if '多被' in line and '唏' not in line and '金' in line:
                out.write(f'  L{i}(可能缺唏): {line.strip()[:100]}\n')
            # 旧核心规则
            if 'WXZC' in line and 'WXAB' in line and '核心' not in line:
                out.write(f'  L{i}(规则): {line.strip()[:100]}\n')
            # 空看空长定义
            if '空看' in line and ('ZC' in line or '条件' in line):
                out.write(f'  L{i}: {line.strip()[:100]}\n')

print('Done')