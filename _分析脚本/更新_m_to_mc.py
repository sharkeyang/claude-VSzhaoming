with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace all old M labels with new MC/MP labels
# Order matters: do more specific replacements first

# M1.x tables → MC5.x (keep as "已有资产" reference but update labels)
reps = [
    ('| M1.1 策略→列映射表 |', '| MC5.1 策略→列映射表 |'),
    ('| M1.2 柱排量化规则 |', '| MC5.2 柱排量化规则 |'),
    ('| M1.3 三层策略伪代码 |', '| MC5.3 三层策略伪代码 |'),
    ('| M1.1 | `_产出物', '| MC5.1 | `_产出物'),
    ('| M1.2 | `_产出物', '| MC5.2 | `_产出物'),
    ('| M1.3 | `_产出物', '| MC5.3 | `_产出物'),

    # M2.x → MC2.x
    ('| M2.1 数据提取层 |', '| MC2.1 数据提取层 |'),
    ('| M2.2 策略引擎层 |', '| MC2.2 策略引擎层 |'),
    ('| M2.3 评价指标层 |', '| MC2.3 评价指标层 |'),
    ('| M2.4 运行入口 |', '| MC2.4 运行入口 |'),
    ('| M2.5 VBA引擎Python化 |', '| MC2.5 VBA引擎Python化 |'),
    ('| M2.1 | `_产出物', '| MC2.1 | `_产出物'),
    ('| M2.2 | `_产出物', '| MC2.2 | `_产出物'),
    ('| M2.3 | `_产出物', '| MC2.3 | `_产出物'),
    ('| M2.4 | `_产出物', '| MC2.4 | `_产出物'),
    ('| M2.5 | `_产出物', '| MC2.5 | `_产出物'),

    # M3.x → MC3.x (回测验证)
    ('| M3.1 基仓回测 |', '| MC3.1 基仓回测 |'),
    ('| M3.2 <周浮仓>回测 |', '| MC3.2 <周浮仓>回测 |'),
    ('| M3.3 <日浮仓>回测 |', '| MC3.3 <日浮仓>回测 |'),
    ('| M3.4 三层叠加 |', '| MC3.4 三层叠加 |'),
    ('| M3.1 | 满足', '| MC3.1 | 满足'),
    ('| M3.2 | <周浮仓>回测', '| MC3.2 | <周浮仓>回测'),
    ('| M3.3 | <日浮仓>回测', '| MC3.3 | <日浮仓>回测'),
    ('| M3.4 | 三层叠加', '| MC3.4 | 三层叠加'),

    # M4.x → MC3.x (选股引擎)
    ('| M4.1 | `_产出物', '| MC3.1 | `_产出物'),
    ('| M4.3 | `_产出物', '| MC3.3 | `_产出物'),

    # M7-M9 in status tables → map to new tasks
    ('| M7 | 交割单审计 |', '| MO3 | 交割单审计 |'),
    ('| M8 | 资讯爬虫 |', '| — | 资讯爬虫（已删除） |'),
    ('| M9 | 全链路自动流水线 |', '| MO4 | 全链路自动流水线 |'),

    # M7-M9 in Appendix 2 status table
    ('| M7 | 交割单审计 | <nobr>❌</nobr>', '| MO3 | 交割单审计 | <nobr>❌</nobr>'),
    ('| M8 | 资讯爬虫 | <nobr>❌</nobr>', '| — | 资讯爬虫（已删除） | <nobr>❌</nobr>'),
    ('| M9 | 全链路自动流水线 | <nobr>❌</nobr>', '| MO4 | 全链路自动流水线 | <nobr>❌</nobr>'),

    # Prose references
    ('M1.3 三层策略伪代码 → 扩展为四域伪代码', 'MC5.3 三层策略伪代码 → 扩展为四域伪代码'),
    ('M2.1-M2.5 回测框架', 'MC2.1-MC2.5 回测框架'),
    ('M1.3三层策略伪代码基础上', 'MC5.3三层策略伪代码基础上'),
    ('原M1.3覆盖三层策略入场', '原MC5.3覆盖三层策略入场'),
]

for old, new in reps:
    c = c.replace(old, new)

# Handle M4 in milestone table headers (keep as is since it's a milestone name)
# Handle M9 in prose (line 155, 161 - these are references to automated workflows)
# These are conceptual references, not file names, OK to keep

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')