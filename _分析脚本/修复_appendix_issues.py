with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove orphaned duplicate (lines 1342-1396)
# Find the orphaned content
orphan_start = c.find('\n\n 三文件分工与偏差检查')
orphan_end = c.find('\n## 附录一', orphan_start)
if orphan_start >= 0:
    c = c[:orphan_start] + c[orphan_end:]
    print('Removed orphan')

# 2. Fix 附录二 table with complete content
old_app2 = '''## 附录二 启动资产基线

本路线图启动前已存在的系统资产（M0=基础设施，M1=策略文档）：

| 步骤 | 事项 | 状态 | 完成时间 |
|:----:|:-----|:----:|:--------:|
| M0 | Excel 指标引擎：1090列日线数据（BTZ/WXCD/柱排/冲高提示等全指标） | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA数据引擎：IQQQ跨码全息/神谕/格程 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA筛选系统：P展撑1筛选（周护型/周大局/地型分类） | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA图形化：P展撑7瓜页 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | 池管理：池金(Z1<周浮仓>)/池银(Z2长期甲)/池铜(Z3长期乙)/池黑(Zn) | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | 仓位管理：底仓5000+浮仓20000（规则已定义，未完全自动化） | <nobr>⚠️</nobr> | <nobr>—</nobr> |
| M0 | 回测系统：RAP算展1引擎+ZAL算比0调程，已有乱宙回测数据 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | 策略文档已整合为三文件体系：A盯盘警示卡 / B交易体系 / C昭明路线图 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |'''

new_app2 = '''## 附录二 启动资产基线

本路线图启动前已存在的系统资产（M0=基础设施，M1=策略文档）：

| 步骤 | 事项 | 状态 | 完成时间 |
|:----:|:-----|:----:|:--------:|
| M0 | Excel 指标引擎：1090列日线数据（BTZ/WXCD/柱排/冲高提示等全指标） | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA数据引擎：IQQQ跨码全息/神谕/格程 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA筛选系统：P展擎1筛选（周护型/周大局/地型分类） | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | VBA图形化：P展擎7瓜页 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | 池管理：池金(Z1<周浮仓>)/池银(Z2长期甲)/池铜(Z3长期乙)/池黑(Zn) | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | 仓位管理：底仓5000+浮仓20000（规则已定义，未完全自动化） | <nobr>⚠️</nobr> | <nobr>—</nobr> |
| M0 | 回测系统：RAP算展1引擎+ZAL算比0调程，已有乾坤回测数据 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | **策略文档已整合为三文件体系：** A盯盘警示卡 / B交易体系 / C昭明路线图 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M0 | <周浮仓>子系统：位谕of周层猪操作 下柱冲高提示已有660+条信号，但未单独回测 | <nobr>⚠️</nobr> | <nobr>—</nobr> |
| M0 | **照明思维PPT核心思想已融入B：** 三大公理、有容乃大、镜面对称、单向二戒、舍的功效、必赢战法 | <nobr>✅</nobr> | <nobr>2026-06-28</nobr> |
| M1 | 策略→指标映射文档 | <nobr>✅</nobr> | <nobr>2026-06-29</nobr> |
| M1 | 三层策略伪代码 | <nobr>✅</nobr> | <nobr>2026-06-29</nobr> |
| M1 | 柱排→买卖信号量化 | <nobr>✅</nobr> | <nobr>2026-06-29</nobr> |
| M3 | <周浮仓>/<日浮仓>独立回测 | <nobr>⏳ 待启动</nobr> | <nobr>—</nobr> |
| M4 | 每日AI选股引擎（M4.1）+ CLI入口（M4.3） | <nobr>✅ 已完成</nobr> | <nobr>2026-06-29</nobr> |
| M5 | VBA持仓操作提示自动化 | <nobr>❌</nobr> | <nobr>—</nobr> |
| M7 | 交割单审计 | <nobr>❌</nobr> | <nobr>—</nobr> |
| M8 | 资讯爬虫 | <nobr>❌</nobr> | <nobr>—</nobr> |
| M9 | 全链路自动流水线 | <nobr>❌</nobr> | <nobr>—</nobr> |'''

c = c.replace(old_app2, new_app2)

# 3. Rename headings
c = c.replace('### 13. VBA2python迁移进度记录', '### 5.1 任务13进度记录（VBA2python迁移）')
c = c.replace('### 14. 行程卡→小传转化', '### 5.2 任务14 行程卡→小传转化')
c = c.replace('### 17. 期货板块轮动框架', '### 5.3 任务17 期货板块轮动框架')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')