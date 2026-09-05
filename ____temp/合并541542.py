# -*- coding: utf-8 -*-
import re
f = '_主文档/MC3.3_C6研究日类微观形态.md'
lines = open(f, encoding='utf-8').read().split('\n')

# 定位 5.4 主题、5.4.1、5.4.2、5.8 标题行
i54 = next(i for i,l in enumerate(lines) if re.match(r'^### 5\.4 ', l))
i541 = next(i for i,l in enumerate(lines) if re.match(r'^#### 5\.4\.1 ', l))
i542 = next(i for i,l in enumerate(lines) if re.match(r'^#### 5\.4\.2 ', l))
i58 = next(i for i,l in enumerate(lines) if re.match(r'^### 5\.8 ', l))

# 提取 5.4.1 正文（不含标题行，不含尾部---）
def body(start, end):
    b = lines[start+1:end]
    while b and (b[-1].strip()=='' or b[-1].strip()=='---'):
        b.pop()
    return b

b541 = body(i541, i542)   # 5.4.1 正文
b542 = body(i542, i58)    # 5.4.2 正文

# 5.4.2 中需要保留的独有内容：①触顶vs非触顶、⑥BSHA增强、⑦最强信号、⑧单股vs多股差异
# 去掉重复的 ②ZC、③合顶、④护型、⑤护型×合顶、⑨触顶持续性
# 提取 5.4.2 中 ①⑥⑦⑧ 部分
# 按 "**① " "**⑥ " "**⑦ " "**⑧ " 分割
def split_items(b):
    items = []
    cur = []
    cur_key = None
    for l in b:
        m = re.match(r'^\*\*([①-⑨])\s', l)
        if m:
            if cur_key: items.append((cur_key, cur))
            cur_key = m.group(1)
            cur = [l]
        else:
            cur.append(l)
    if cur_key: items.append((cur_key, cur))
    return items

items542 = split_items(b542)
# 保留 ①⑥⑦⑧
keep_keys = {'①','⑥','⑦','⑧'}
keep_blocks = [blk for k, blk in items542 if k in keep_keys]

# 构造新 5.4 节
new_block = []
new_block.append('### 5.4 触顶信号验证体系（高波池全量）')
new_block.append('')
new_block.append('> **主题：** 触顶/合顶/护型 对次日冲高的预测，基于**高波池全量（Qic+Qim+Qit，3451 只，约 1109 万样本）**。下设一个节，含触顶信号的全部结论（上符串符号/ZC前提/合顶天数/护型排序/护型×合顶/动态转移/触顶持续性/BSHA增强/最强信号/单股vs多股差异）。')
new_block.append('')
new_block.extend(b541)
new_block.append('')
new_block.append('---')
new_block.append('')
# 追加 5.4.2 独有内容（①⑥⑦⑧）
for blk in keep_blocks:
    new_block.extend(blk)
    new_block.append('')
    new_block.append('---')
    new_block.append('')

# 替换 5.4 主题到 5.8 之前
result = lines[:i54] + new_block + lines[i58:]
open(f, 'w', encoding='utf-8').write('\n'.join(result))
print('合并完成')
print('新5.4节行数:', len(new_block))
