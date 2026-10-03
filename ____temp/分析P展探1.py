# -*- coding: utf-8 -*-
import os, io

# 找到 P展探1 文件
target = None
for f in os.listdir('昭明计划VS优化_vba'):
    if 'P展探1' in f:
        target = f
        break

if target is None:
    print('未找到 P展探1 文件')
else:
    print('找到文件:', target)
    path = os.path.join('昭明计划VS优化_vba', target)
    with io.open(path, encoding='utf-8') as fh:
        lines = fh.readlines()
    # 找 Sub 定义
    for i, l in enumerate(lines):
        if 'Sub ' in l and '展探1' in l:
            print(f'Sub定义 @{i+1}: {l.strip()}')
            for j in range(i, min(i+12, len(lines))):
                print(f'  {lines[j].rstrip()}')
            break
    print()
    print('=== 出节模式 变量定义 ===')
    for i, l in enumerate(lines):
        if '出节模式' in l and ('Dim ' in l or 'ByVal ' in l or 'ByRef ' in l or 'As String' in l or 'As Variant' in l):
            print(f'@{i+1}: {l.strip()}')
