# -*- coding: utf-8 -*-
"""重建被 fix_toc 损坏的 C2 文档 (v2, 修正重复目录 bug)。
基底 = git HEAD 完整 C2 (第二三章未改动 + 第四章4.1/4.2)，跳过原目录区，
拼接保留尾部 (4.3.2-4.4.3 用户重构)，重建 4.3 节头 + 4.3.1，统一改名，重建目录。
"""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "____temp/c2_head_full.md"
TAIL = "____temp/c2_preserved_tail.md"
OUT  = "_主文档/MC3.3_C2日DXZC+DXAB全维度分析.md"

def read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

base = read(BASE).split('\n')
tail = read(TAIL).rstrip('\n').split('\n')

# ============ HEAD 结构 (1-indexed): ============
#   1:    # MC3.3_C2 ...
#   2:    (blank)
#   3:    ## 第二章：日类基本模型验证：DXZC+DXAB
#   4-12: metadata blockquote
#   13:   ---
#   14-114: TOC (原始, 需跳过)
#   116:  ---
#   117:  ### 2.1 核心准则  <-- 真实正文开始
#   3079: ## 第四章
#   3091: ### 4.1
#   3114: ### 4.2

# front = 行 1..13 (标题 + ## 第二章 头 + 元信息 + ---)   [index 0..12]
front = base[:13]

# body_ch23 = 行 117..3113 (真实第二三章正文 + 第四章 4.1 整段)  [index 116..3112]
body_ch23 = base[116:3113]

# HEAD 4.2 段 (行 3114..3147, index 3113..3146): 保留到 "**综合基础范围表" 前
h42 = base[3113:3147]
cut_idx = None
for i, l in enumerate(h42):
    if l.startswith('**综合基础范围表'):
        cut_idx = i
        break
h42_keep = h42[:cut_idx] if cut_idx is not None else h42

# 重建 4.3 节头 + 4.3.1
sec43 = [
    '### 4.3 第二阶段：日类操作范围（范围 vs 等级，四维参数分工）',
    '',
    '> **两段式：范围 vs 等级。** 四维均线（DXEF/DXZE/DXCD/DXZC）不是都用来"圈范围"——分成两层职责：',
    '> - **范围（能不能做）——DXCD + DXZC + DXAB**：DXZC>0 总开关 + CD 上/忐 可做 + 护型乙(ZA>0)/甲。注：**DXCD 与 DXZC 完全共线**——上/忐/忠 → DXZC>0，中/下/忑 → DXZC≤0',
    '> - **等级（做得多好）——DXEF（与 DXZE 共线）**：金银唏 为 DJE 之上（ZE>0）高等级，嘘尿屎 为 DJE 之下（ZE≤0）低等级',
    '> - **范围外**：丁/戊(ZA≤0)/丙 回避/退出',
    '',
    '#### 4.3.1 两段式分工：范围 vs 等级',
    '',
    '> 四维均线职责分工：**范围（能不能做）由 DXCD/DXZC/DXAB 判定，等级（做得多好）由 DXEF/DXZE 判定**。DJE 之下**不排除范围外，只是等级低、轻仓严止损**。完整参数分工与全量数据见 §4.3.2。',
    '',
]

# ============ 正文 = front(元信息区) + body_ch23 + h42_keep + sec43 + tail ============
body = front + body_ch23 + h42_keep + sec43 + tail

# ============ 统一改名 ============
body = [l.replace('周级别分析框架', '周级别决策树框架')
          .replace('日级别分析框架', '日级别决策树框架')
          .replace('日类分析框架', '日类决策树框架')
          .replace('分析框架决策树', '决策树框架')
        for l in body]

# ============ 生成 TOC (从正文所有标题) ============
def gfm_anchor(text):
    a = re.sub(r'(\d+)\.(\d+)', r'\1\2', text)
    a = re.sub(r'[（(]', '', a); a = re.sub(r'[）)]', '', a)
    a = a.lower(); a = re.sub(r'[^\w一-鿿\s-]', '', a)
    a = re.sub(r'\s+', '-', a.strip()); a = re.sub(r'-+', '-', a)
    return a

headings = []
for l in body:
    m = re.match(r'^(#{2,5})\s+(.+)$', l)
    if m:
        level = len(m.group(1)); text = m.group(2).strip()
        headings.append((level, text, gfm_anchor(text)))

toc_lines = ['**目录：**', '']
for level, text, anchor in headings:
    indent = '' if level == 2 else '    ' * (level - 2)
    toc_lines.append(f'{indent}- [{text}](#{anchor})')
toc_block = '\n'.join(toc_lines)

# ============ 组装最终文件 ============
# 结构: front(含 ## 第二章头+元信息+---) + TOC + --- + 真实正文(### 2.1 ...)
front_text = '\n'.join(front)          # 含末尾 '---'
real_body = '\n'.join(body[len(front):])  # 从 ### 2.1 开始 (去掉 front 部分)
# 但 body = front + 其余, 所以 real_body = body 去掉 front 前部
# 计算 front 在 body 中的长度
front_len = len(front)
real_body = '\n'.join(body[front_len:])

final = front_text + '\n\n' + toc_block + '\n\n---\n\n' + real_body + '\n'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(final)

print(f"重建完成: {OUT} ({len(final.splitlines())} 行)")
print(f"标题数: {len(headings)}")
print("\n=== 第四章标题 ===")
for l in final.split('\n'):
    if re.match(r'^#{2,5}\s*(4\.\d|第四章)', l):
        print(l)
