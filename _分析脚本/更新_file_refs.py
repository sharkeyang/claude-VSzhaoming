for fname in ['全局_A盯盘警示卡.md', '全局_B交易体系.md', '全局_C昭明路线图.md']:
    filepath = f'd:/@VSwork/VS昭明计划VBA优化/_规则文档/{fname}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0
    replacements = {
        '_回测框架/M2_1_数据加载.py': '_产出物/MC2_1_数据加载.py',
        '_回测框架/M2_2_策略引擎.py': '_产出物/MC2_2_策略引擎.py',
        '_回测框架/M2_3_评价指标.py': '_产出物/MC2_3_评价指标.py',
        '_回测框架/M2_4_运行回测.py': '_产出物/MC2_4_运行回测.py',
        '_回测框架/迁移VBA_': '_产出物/MC2_5_迁移VBA_',
        '_回测框架/M4_1_选股引擎.py': '_产出物/MC3_1_选股引擎.py',
        '_回测框架/M4_3_每日选股.py': '_产出物/MC3_3_每日选股.py',
        '_回测框架/M3_回测验证.py': '_产出物/MC3_4_回测验证.py',
        '_规则文档/M1.1_策略_指标映射表.md': '_产出物/MC5_1_策略_指标映射表.md',
        '_规则文档/M1.2_柱排量化规则.md': '_产出物/MC5_2_柱排量化规则.md',
        '_规则文档/M1.3_三层策略伪代码.md': '_产出物/MC5_3_三层策略伪代码.md',
        '_规则文档/M5.1_下周冲高模式归纳.md': '_产出物/MC5_4_冲高模式归纳.md',
        '`小传.py`': '`_产出物/MC4_小传生成器.py`',
    }

    for old, new in replacements.items():
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            changes += count

    # Update generic folder refs
    content = content.replace('`_回测框架/', '`_产出物/')

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{fname}: {changes} references updated')
    else:
        print(f'{fname}: no changes')