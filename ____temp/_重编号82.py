# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 8.2 原有子节编号 8.3.x -> 8.2.x
# 8.3.1->8.2.1, 8.3.2->8.2.2, 8.3.3->8.2.3, 8.3.4->8.2.4, 8.3.5->8.2.5
# 8.3.5.1->8.2.5.1, 8.3.5.2->8.2.5.2, 8.3.6->8.2.6(冲突!), 8.3.7->8.2.7(冲突!), 8.3.8->8.2.8(冲突!)
# 冲突: 8.3.6/8.3.7/8.3.8 与 8.2.6/8.2.7/8.2.8(马尔可夫)冲突
# 方案: 8.3.1-8.3.5 -> 8.2.1-8.2.5, 8.3.6-8.3.8 -> 8.2.14-8.2.16(追加到马尔可夫之后)

# 先处理 8.3.5.1/8.3.5.2 (最具体)
content = content.replace('##### 8.3.5.1', '##### 8.2.5.1')
content = content.replace('##### 8.3.5.2', '##### 8.2.5.2')
# 8.3.1-8.3.5
content = content.replace('##### 8.3.1 ', '##### 8.2.1 ')
content = content.replace('##### 8.3.2 ', '##### 8.2.2 ')
content = content.replace('##### 8.3.3 ', '##### 8.2.3 ')
content = content.replace('##### 8.3.4 ', '##### 8.2.4 ')
content = content.replace('##### 8.3.5 ', '##### 8.2.5 ')
# 8.3.6-8.3.8 -> 8.2.14-8.2.16
content = content.replace('##### 8.3.6 ', '##### 8.2.14 ')
content = content.replace('##### 8.3.7 ', '##### 8.2.15 ')
content = content.replace('##### 8.3.8 ', '##### 8.2.16 ')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('重编号完成')
