# -*- coding: utf-8 -*-
"""
全文扫描：为长引用块（> 开头）在语义边界处插入 <br>\n 换行。
规则来源：memory doc-long-block-br-rule
- 只处理单层引用块（> 后跟普通文本，非 > > 嵌套、非 > [! 特殊块）
- 在语义边界（句号/分号/问号/破折号）插入 <br>
- 已含 <br> 的行跳过
- 保证内容不丢失：只插入 <br>，不改动任何原文
- 保留原文件行尾（CRLF/LF 不变）
"""
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else r"_主文档\MC3.3.5_甲乙己日等型交叉分析报告.md"

# 语义边界：在以下位置之后断开（lookbehind 保留分隔符在前段）
BOUNDARY = re.compile(
    r'(?<=[。；？])'
    r'|(?<=——)'
)

def is_processable(line):
    """是否是可处理的单层引用块长行。line 不含行尾换行符。"""
    if not line.startswith('> '):
        return False
    if '<br>' in line:
        return False
    if len(line) <= 100:
        return False
    content = line[2:]
    # 跳过嵌套引用（> > 或 > ** 开头）和特殊块
    if content.startswith('>') or content.startswith('**'):
        return False
    return True

def process_line(line):
    """line 不含行尾换行符。返回处理后的多行（不含行尾换行符，用 \n 分隔）。"""
    content = line[2:]
    positions = [m.end() for m in BOUNDARY.finditer(content)]
    if not positions:
        return None
    segments = []
    last = 0
    for pos in positions:
        segments.append(content[last:pos])
        last = pos
    segments.append(content[last:])
    # 合并悬空的 '**' 片段到前一段
    merged = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if merged and seg == '**':
            merged[-1] = merged[-1] + seg
        else:
            merged.append(seg)
    if len(merged) <= 1:
        return None
    out = ['> ' + s for s in merged]
    return '<br>\n'.join(out)

def main():
    # 读取并保留原行尾（newline='' 使 \r\n 保留在行字符串中）
    with open(SRC, 'r', encoding='utf-8', newline='') as f:
        raw = f.read()
    # 检测行尾符
    if '\r\n' in raw:
        EOL = '\r\n'
    else:
        EOL = '\n'
    lines = raw.split(EOL)

    new_lines = []
    changed = 0
    for line in lines:
        if is_processable(line):
            processed = process_line(line)
            if processed is not None:
                changed += 1
                # 用 <br> + EOL 连接
                processed = processed.replace('\n', EOL)
                new_lines.append(processed)
                continue
        new_lines.append(line)

    with open(SRC, 'w', encoding='utf-8', newline='') as f:
        f.write(EOL.join(new_lines))

    print(f"done, changed {changed} lines, EOL={repr(EOL)}")

if __name__ == '__main__':
    main()