with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

target = '（人性）            （体系）                 （施工）\n```'
idx = c.rfind(target)
if idx >= 0:
    new_section = '''（人性）            （体系）                 （施工）
```

## 附录二 启动资产基线

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

    c = c[:idx] + target + '\n\n' + new_section.split('```\n\n', 1)[1]
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Restored')
else:
    print('Not found')