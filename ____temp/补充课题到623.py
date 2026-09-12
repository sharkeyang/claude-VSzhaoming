# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. 在6.2.3开头补充课题
old1 = '''#### 6.2.3 甲的特权与乙的差异（已验证，见 6.2.4）

> **甲的特权（观察）：**'''
new1 = '''#### 6.2.3 甲的特权与乙的差异（已验证，见 6.2.4）

> **课题（用户提出，2026-09-06）：** 针对甲（DXAB 刚正交），是否具有特权——0<DXAB≤4 内出现阴柱基本转为阳柱、优选连阳后第一个阴柱（vV）、第一次回踩 DJA 后一般反弹？**用数据验证。** 针对乙（只是再次突破 DXZA，无甲由负转正的特权），是否必须形成突破回踩、启动结构才能再次推高顶拉升？**用数据验证。**

> **甲的特权（观察）：**'''
if old1 in content:
    content = content.replace(old1, new1)
    print('已在6.2.3开头补充课题')
else:
    print('未找到6.2.3开头')

# 2. 在6.2.4开头补充课题（乙DXZA<0不要一下破DJA就跑）
old2 = '''#### 6.2.4 综合结论（高波池全量验证，2026-09-05）

**① 广义正交护型覆盖上涨区域 ✓（最重要发现）**'''
new2 = '''#### 6.2.4 综合结论（高波池全量验证，2026-09-05）

> **课题（用户提出，2026-09-06）：** 验证乙（DXZA<0）——**不要一下破 DJA 就想跑，很多都是机会**。用数据验证。

**① 广义正交护型覆盖上涨区域 ✓（最重要发现）**'''
if old2 in content:
    content = content.replace(old2, new2)
    print('已在6.2.4开头补充课题')
else:
    print('未找到6.2.4开头')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('完成')
