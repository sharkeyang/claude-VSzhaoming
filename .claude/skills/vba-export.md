---
name: vba-export
description: Export VBA standard modules from 昭明计划VS优化.xlsm to text files
---

# Export VBA 模块

导出所有标准模块 (.bas) 到 `昭明计划VS优化_vba/`。自动处理 OneDrive 文件锁定。

## 执行步骤

依次执行以下命令：

```bash
cp 昭明计划VS优化.xlsm /tmp/昭明计划VS优化.xlsm
```

```bash
python "VBA宏操作_导出_Python版.py" /tmp/昭明计划VS优化.xlsm -m -c NONE
```

```bash
cp -r /tmp/昭明计划VS优化_vba 昭明计划VS优化_vba
```

```bash
rm -rf /tmp/昭明计划VS优化.xlsm /tmp/昭明计划VS优化_vba
```
