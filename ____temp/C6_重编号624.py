# -*- coding: utf-8 -*-
"""重编号 6.2.4/6.2.5/6.2.6 -> 6.2.3/6.2.4/6.2.5（一次性替换，避免连锁）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
mapping = {'4':'3','5':'4','6':'5'}
def renum(line):
    if 'A.6' in line: return line
    # 标题/正文编号 6.2.x（x=4/5/6）
    def sub(m):
        x = m.group(1)
        return f'6.2.{mapping.get(x,x)}'
    line = re.sub(r'(?<!\d)6\.2\.([456])(?!\d)', sub, line)
    # TOC锚点 #624- #625- #626-
    def sub_a(m):
        x = m.group(1)
        return f'#62{mapping.get(x,x)}'
    line = re.sub(r'#62([456])(?!\d)', sub_a, line)
    return line
out=[]
for line in lines:
    if re.match(r'^#{2,4} 6\.2\.', line) or re.match(r'^\s*- \[6\.2\.', line):
        line = renum(line)
    out.append(line)
with open(path,'w',encoding='utf-8') as f:
    f.writelines(out)
print('完成')
