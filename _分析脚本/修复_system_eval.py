with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Find and replace the broken system evaluation section
# From '**系统化评估流程：**' to just before '**操盘计划模板：**'
start = c.find('**系统化评估流程：**\n```\nStep 1：')
end = c.find('**操盘计划模板：**', start)

if start >= 0 and end >= 0:
    new_section = '''**系统化评估流程：**
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">
<tr><td>

```
Step 1：采集全部指标（WXCD/柱排/BTZ/DJE位置/DSHA/冲高提示/诱多标记）
  ※ 此时标的已通过 M4 硬条件过滤（WXCD=金/银, 前周WXZC>0, 今日DXZE>0）
    评分表不再重复否决，仅对已准入的候选做多维度打分。
```

**Step 2：多维度加权评分（满分100）**

| 评分维度 | 权重 |
|:---------|:---:|
| 周仓出章（原仓月，出章模式，最强预测因子） | 25分 |
| 大局（市场状态） | 20分 |
| 护型（趋势方向） | 20分 |
| 动量（短期延续/反转） | 10分 |
| 周仓出节（原仓周，出节模式，周级持仓信号） | 10分 |
| 漏提示（模式识别） | 10分 |
| 日历效应 | 5分 |
| **合计** | **100分** |

**Step 3：决策映射**

| 条件 | 操作 |
|:-----|:----:|
| score >= 70 | 买入 |
| 50 <= score < 70 | 持有 |
| 30 <= score < 50 | 减仓 |
| score < 30 | 卖出 |
| WXCD=屎/尿 + 周仓出章以C/Z开头 | 禁入 |

```
Step 4：生成操盘计划（含上涨/下跌/震荡三种预案）
Step 5：人执行计划（不修改、不犹豫、不临场变卦）
```

</td></tr>
</table>

'''

    c = c[:start] + new_section + c[end:]
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Done')
else:
    print(f'start={start}, end={end}')
