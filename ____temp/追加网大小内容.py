# -*- coding: utf-8 -*-
"""在"网越大...6.1是平衡"行后追加"其他网"和"不要中间介入"内容。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到"网越大"行
target = None
for i, line in enumerate(lines):
    if '网越大' in line and '6.1 是平衡' in line:
        target = i
        break

if target is not None:
    # 在 target 行后插入新内容
    new_content = [
        '> - **其他网**：网可以是 6.0（不限制日类）、6.1（DJC丘）、6.2（DJA，不实际使用）或其他——**DJE丘、DJD丘、DJD&DJC丘、DJE&DJD&DJC丘**。\n',
        '>\n',
        '> 🔴🔴 **一定要记住：不要中间介入，中间介入是导致亏损的根源** 🔴🔴\n',
        '> - **不要中间介入**：选定"网"（如 DJC 丘）后，**只在网的边界介入/退出**（站上介入、跌破退出），**不要在网内中途介入**（如 DJC 丘内 DXZA 波动时频繁进出）。\n',
        '> - **中间介入是导致亏损的根源**：网内中途介入（如 DJA 之上频繁进出）面临 DXZA 劫（65.9% 恢复，摩擦成本）和诱多（44.8% 跌破，追高必套）——**这是亏损的根源**。\n',
        '> - **正确做法**：选定网后，**用较大的网抓确定的机会**（如 DJC 丘），**不要中途介入**，只在边界进出。\n',
    ]
    # 在 target 行后插入
    lines = lines[:target+1] + new_content + lines[target+1:]
    with io.open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'已在行{target+1}后追加内容')
else:
    print('未找到目标行')