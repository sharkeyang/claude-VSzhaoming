with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

old_start = '### 2.2 专题二：浮仓冲高策略的讨论（2026-06-30）'
old_end = '### 2.3 专题三：'

start_idx = c.find(old_start)
end_idx = c.find(old_end, start_idx + 1)

if start_idx >= 0 and end_idx >= 0:
    new_section = '''### 2.2 DXZE>0 区域的完整划分（待研究）

需要对 DXZE>0 区域通过纯理论分析或历史遍历，分类并归纳各种走势的后续概率。

**公理：** 所有浮仓的操作区域（入仓、持仓），都在 DJEDC 之上。

> **注一：** 下破 DJC 应将浮仓退出；当处于 DJC 之下且 DJE 之上，只可能是 `_多长` 基仓。DXCD<0 属于周级别 WXAB<0，当未上破 DJD 时不应介入，应选择即将导致 DXCD 正交的情况。

**重点分类依据：**
- DXCD（日级核心框架方向）
- DXBC（日级BC交叉状态）
- DXAB（日级护型正交状态）
- DJA之上柱排（升/跌/人）

'''
    c = c[:start_idx] + new_section + c[end_idx:]
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Done')
else:
    print(f'start={start_idx}, end={end_idx}')