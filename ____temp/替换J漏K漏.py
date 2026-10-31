# -*- coding: utf-8 -*-
"""批量替换正文中的方法日J漏→方法日N漏、方法日K漏→方法日M漏。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 用占位符避免冲突
content = content.replace('方法日J漏', '方法日XJ漏')
content = content.replace('方法日K漏', '方法日XK漏')
# 占位符替换回目标
content = content.replace('方法日XJ漏', '方法日N漏')
content = content.replace('方法日XK漏', '方法日M漏')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('替换完成')