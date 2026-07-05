with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# First fix the double-prefix issue
c = c.replace('MC2_5_MC2_5_', 'MC2_5_')

# Fix M1.x references with paths
c = c.replace('`M1.1_策略_指标映射表.md`', '`_产出物/MC5_1_策略_指标映射表.md`')
c = c.replace('`M1.2_柱排量化规则.md`', '`_产出物/MC5_2_柱排量化规则.md`')
c = c.replace('`M1.3_三层策略伪代码.md`', '`_产出物/MC5_3_三层策略伪代码.md`')

# Fix M4.x old references
c = c.replace('`M4.1_选股引擎.py`', '`_产出物/MC3_1_选股引擎.py`')
c = c.replace('`M4.3_每日选股.py`', '`_产出物/MC3_3_每日选股.py`')
c = c.replace('- `M4.1_选股引擎.py`', '- `_产出物/MC3_1_选股引擎.py`')
c = c.replace('- `M4.3_每日选股.py`', '- `_产出物/MC3_3_每日选股.py`')

# Fix M4 milestone table entries (keep M4.1/M4.3 as milestone names but update paths)
c = c.replace('M4.1）+ CLI入口（M4.3）', 'MC3.1）+ CLI入口（MC3.3）')

# Fix description text about M1.3
c = c.replace('在M1.3三层策略伪代码基础上', '在MC5.3三层策略伪代码基础上')
c = c.replace('原M1.3覆盖三层策略入场/出场逻辑', '原MC5.3覆盖三层策略入场/出场逻辑')

# Fix M4 in 已有资产 references
c = c.replace('- `M4.1_选股引擎.py`', '- `_产出物/MC3_1_选股引擎.py`')
c = c.replace('- `M4.3_每日选股.py`', '- `_产出物/MC3_3_每日选股.py`')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
