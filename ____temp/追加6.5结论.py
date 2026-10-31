# -*- coding: utf-8 -*-
"""在6.5方法日J漏"为何能赢"核心结论后追加本次验证结论。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到"核心：方法日J漏不是逆势抄底"行
target = None
for i, line in enumerate(lines):
    if '核心：方法日J漏不是逆势抄底' in line:
        target = i
        break

if target is not None:
    new_content = [
        '>\n',
        '> 🔴 **6.5 是"6.0 - 6.2"（DJA 之下介入），在 DXCD=上 前提下获利，但上破 DJA/DJC 略优（2026-10-28 全量验证）：**\n',
        '> - **6.5 是"6.0（无限制网）- 6.2（DJA 网）"**——只在 DJA 之下（DXZA<0）介入，正好是 6.2（DJA 之上）的补集。两个网相减仍是网。\n',
        '> - **在 DXCD=上（多头排列）前提下，下破 DJA 低吸是获利的**（持有10日 +0.72%）——主升区域跌破 DJA 会被拉回（C7 §6.1.5.5：跌破 DJA 后 5日 95% 拉回），这是 6.5 能赢的关键。\n',
        '> - **但上破 DJA 略优于下破 DJA**（持有10日 +0.79% vs +0.72%）、**上破 DJC 也获利**（+0.68%）——**即使要捡漏，也应选择即将上破 DJA 或即将上破 DJC（如 DXAB 己），而不是在下破 DJA 时介入**。\n',
        '> - **🔴 核心**：6.5 不是"错掉 DJA 丘"就亏损——在 DXCD=上 前提下，下破 DJA 低吸仍获利（主升浅回调被拉回）。但**上破 DJA/DJC 略优**，捡漏应优先选择即将上破的介入点。\n',
    ]
    lines = lines[:target+1] + new_content + lines[target+1:]
    with io.open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'已在行{target+1}后追加内容')
else:
    print('未找到目标行')