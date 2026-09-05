# -*- coding: utf-8 -*-
"""把 C6 的"七、微观指标综合运用"整块剪切，移到"六、按形态探索"之前，重命名为第五章。"""
import io, re

path = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.3_C6研究日类微观形态.md'
with io.open(path, encoding='utf-8') as f:
    content = f.read()

# 定位"七、微观指标综合运用"开头
ch7_start = content.find('## 七、微观指标综合运用')
assert ch7_start != -1, '未找到 七、微观指标综合运用'
# 定位附录开头（七章之后是附录）
appendix_start = content.find('## 附录：DXZA全周期分类')
assert appendix_start != -1, '未找到 附录'
# 定位 六、按形态探索 开头
ch6_start = content.find('## 六、按形态探索')
assert ch6_start != -1, '未找到 六、按形态探索'

# 剪切第七章块（从 ch7_start 到附录之前，含前面可能的 --- 分隔）
ch7_block = content[ch7_start:appendix_start]
# 去掉块尾部多余的 --- 和空行
ch7_block = ch7_block.rstrip() + '\n'
# 重命名 七、 -> 五、
ch7_block = ch7_block.replace('## 七、微观指标综合运用', '## 五、微观指标综合运用')
ch7_block = ch7_block.replace('### 7.0', '### 5.0')
ch7_block = ch7_block.replace('#### 7.1', '#### 5.1')
ch7_block = ch7_block.replace('#### 7.2', '#### 5.2')
ch7_block = ch7_block.replace('#### 7.3', '#### 5.3')

# 从原位置删除第七章块（ch7_start 到 appendix_start）
content = content[:ch7_start] + content[appendix_start:]

# 在第六章开头之前插入第五章块（加 --- 分隔）
content = content[:ch6_start] + ch7_block + '\n---\n\n' + content[ch6_start:]

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('完成：七章已剪切并重命名为第五章，移到第六章之前')
