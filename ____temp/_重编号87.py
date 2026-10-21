# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
content = open(path, encoding='utf-8').read()

# 用占位符避免冲突: 8.7->X4, 8.9->X5, 8.10->X6, 8.11->X7
# 先替换所有 8.11 -> X7, 8.10 -> X6, 8.9 -> X5, 8.7 -> X4
# 注意: 8.11 要先于 8.1 处理(避免 8.11 被 8.1 误匹配)
# 用正则精确匹配 8.11/8.10/8.9/8.7 (后面跟 . 或 空格 或 结束)

def renum(content, old, new):
    # 匹配 8.11 后跟 .数字 或 空格 或 非数字
    # 用负向断言避免 8.11 匹配 8.1
    pattern = re.compile(r'(?<!\d)' + re.escape(old) + r'(?=[.\s]|$)')
    return pattern.sub(new, content)

# 先占位
content = renum(content, '8.11', 'XX7')
content = renum(content, '8.10', 'XX6')
content = renum(content, '8.9', 'XX5')
content = renum(content, '8.7', 'XX4')
# 再替换占位
content = content.replace('XX7', '8.7')
content = content.replace('XX6', '8.6')
content = content.replace('XX5', '8.5')
content = content.replace('XX4', '8.4')

open(path, 'w', encoding='utf-8').write(content)
print('重新编号完成')
