---
name: vba-import
description: Import VBA text files back into 昭明计划VS优化.xlsm
---

# Import VBA 模块

将 `昭明计划VS优化_vba/` 中的 .bas 文件批量导回 xlsm。需要 Excel COM。

## 前置条件

- `pip install pywin32`
- Excel → 信任中心 → 勾选「信任对 VBA 工程对象模型的访问」

## 执行步骤

依次执行以下命令：

```bash
taskkill /F /IM EXCEL.EXE
```

```bash
cp 昭明计划VS优化.xlsm /tmp/昭明计划VS优化.xlsm
```

```bash
cp -r 昭明计划VS优化_vba /tmp/昭明计划VS优化_vba
```

```bash
python "VBA宏操作_导入_Python版.py" /tmp/昭明计划VS优化.xlsm -s /tmp/昭明计划VS优化_vba -m -c NONE
```

```bash
cp /tmp/昭明计划VS优化.xlsm 昭明计划VS优化.xlsm
```

```bash
rm -rf /tmp/昭明计划VS优化.xlsm /tmp/昭明计划VS优化.xlsm.backup /tmp/昭明计划VS优化_vba
```
