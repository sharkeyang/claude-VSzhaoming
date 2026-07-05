import re

# ===== C文件 =====
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# ===== 1. Fix 系统化评估流程 (line 717-755) =====
# Find the section from '**系统化评估流程：**' to '**操盘计划模板：**'
old_sys_start = '**系统化评估流程：**\n```\nStep 1：采集全部指标（WXCD/柱排/BTZ/DJE位置/DSHA/冲高提示/诱多标记）\n  ※ 此时标的已通过 M4 硬条件过滤（WXCD=金/银, 前周WXZC>0, 今日DXZE>0）\n    评分表不再重复否决，仅对已准入的候选做多维度打分。\n```\n\nStep 2：多维度加权评分（满分100）\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n**Step 3：决策映射**\n\n</td></tr>\n</table>\n\n| 评分维度 | 权重 |\n|:---------|:---:|\n| 周仓出章（原仓月，出章模式，最强预测因子） | 25分 |\n| 大局（市场状态） | 20分 |\n| 护型（趋势方向） | 20分 |\n| 动量（短期延续/反转） | 10分 |\n| 周仓出节（原仓周，出节模式，周级持仓信号） | 10分 |\n| 漏提示（模式识别） | 10分 |\n| 日历效应 | 5分 |\n| **合计** | **100分** |\n\n| 条件 | 操作 |\n|:-----|:----:|\n| score >= 70 | 买入 |\n| 50 <= score < 70 | 持有 |\n| 30 <= score < 50 | 减仓 |\n| score < 30 | 卖出 |\n| WXCD=屎/尿 + 周仓出章以C/Z开头 | 禁入 |\n\n```\nStep 4：生成操盘计划（含上涨/下跌/震荡三种预案）\nStep 5：人执行计划（不修改、不犹豫、不临场变卦）\n```'

new_sys = '**系统化评估流程：**\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n```\nStep 1：采集全部指标（WXCD/柱排/BTZ/DJE位置/DSHA/冲高提示/诱多标记）\n  ※ 此时标的已通过 M4 硬条件过滤（WXCD=金/银, 前周WXZC>0, 今日DXZE>0）\n    评分表不再重复否决，仅对已准入的候选做多维度打分。\n```\n\n**Step 2：多维度加权评分（满分100）**\n\n| 评分维度 | 权重 |\n|:---------|:---:|\n| 周仓出章（原仓月，出章模式，最强预测因子） | 25分 |\n| 大局（市场状态） | 20分 |\n| 护型（趋势方向） | 20分 |\n| 动量（短期延续/反转） | 10分 |\n| 周仓出节（原仓周，出节模式，周级持仓信号） | 10分 |\n| 漏提示（模式识别） | 10分 |\n| 日历效应 | 5分 |\n| **合计** | **100分** |\n\n**Step 3：决策映射**\n\n| 条件 | 操作 |\n|:-----|:----:|\n| score >= 70 | 买入 |\n| 50 <= score < 70 | 持有 |\n| 30 <= score < 50 | 减仓 |\n| score < 30 | 卖出 |\n| WXCD=屎/尿 + 周仓出章以C/Z开头 | 禁入 |\n\n```\nStep 4：生成操盘计划（含上涨/下跌/震荡三种预案）\nStep 5：人执行计划（不修改、不犹豫、不临场变卦）\n```\n\n</td></tr>\n</table>'

if old_sys_start in c:
    c = c.replace(old_sys_start, new_sys)
    print('系统化评估流程: wrapped')
else:
    print('系统化评估流程: NOT FOUND - checking...')
    # Try the exact content from the file
    idx = c.find('**系统化评估流程：**\n```\nStep 1')
    if idx >= 0:
        print(f'Found at index {idx}')
        print(repr(c[idx:idx+300]))

# ===== 2. Fix 操盘计划模板 =====
# Find it and wrap
old_template_start = '**操盘计划模板：**\n```\n【今日操盘计划】日期：202X-XX-XX\n\n── 已有持仓 ──\n标的A（基仓）：\n  综合评分：85/100\n  当前状态：DJEDCB区间，满足 _多长\n  ├── 如果上涨 → 持有，不提前止盈\n  ├── 如果下跌 → 观察是否破DJE，不破则持有\n  └── 如果跌破DJE → 全部清仓（强制）\n\n标的B（浮仓）：\n  综合评分：72/100（诱多风险+8）\n  当前状态：日柱排=升开头，但诱多规则②命中\n  ├── 如果上涨 → 观望不追，确认非诱多后再入\n  ├── 如果下跌 → 观察DJA支撑\n  └── 如果破DJA → 平浮仓，回归基仓\n\n── 候选推荐 ──\n标的C（<周浮仓>）：\n  综合评分：91/100\n  推荐仓位：基仓5000+<周浮仓>仓2000\n  ├── 如果上涨达标 → 止盈平仓\n  ├── 如果上涨不达标 → 周五平仓\n  └── 如果下跌 → 下破DJB止损\n```'

new_template = '**操盘计划模板：**\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n```\n【今日操盘计划】日期：202X-XX-XX\n\n── 已有持仓 ──\n标的A（基仓）：\n  综合评分：85/100\n  当前状态：DJEDCB区间，满足 _多长\n  ├── 如果上涨 → 持有，不提前止盈\n  ├── 如果下跌 → 观察是否破DJE，不破则持有\n  └── 如果跌破DJE → 全部清仓（强制）\n\n标的B（浮仓）：\n  综合评分：72/100（诱多风险+8）\n  当前状态：日柱排=升开头，但诱多规则②命中\n  ├── 如果上涨 → 观望不追，确认非诱多后再入\n  ├── 如果下跌 → 观察DJA支撑\n  └── 如果破DJA → 平浮仓，回归基仓\n\n── 候选推荐 ──\n标的C（<周浮仓>）：\n  综合评分：91/100\n  推荐仓位：基仓5000+<周浮仓>仓2000\n  ├── 如果上涨达标 → 止盈平仓\n  ├── 如果上涨不达标 → 周五平仓\n  └── 如果下跌 → 下破DJB止损\n```\n\n</td></tr>\n</table>'

if old_template_start in c:
    c = c.replace(old_template_start, new_template)
    print('操盘计划模板: wrapped')
else:
    print('操盘计划模板: NOT FOUND')

# ===== 3. Fix 流水线 section =====
# Find 流水线 section and make sure it's properly wrapped
old_pipeline = '**流水线：**\n```\n收盘后 → 数据更新 → AI选股 → 小传撰写 → 系统化评估打分\n       → 生成操盘计划（含上涨/下跌/震荡预案）\n       → 写入Excel → VBA提示生成\n开盘前 → 候选清单确认 → 装订预警监控\n尾盘 → 触发买入信号（如有，按计划执行）\n盘中 → 止损监控 + 资讯预警\n月末 → 交割单审计\n```'

new_pipeline = '**流水线：**\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n```\n收盘后 → 数据更新 → AI选股 → 小传撰写 → 系统化评估打分\n       → 生成操盘计划（含上涨/下跌/震荡预案）\n       → 写入Excel → VBA提示生成\n开盘前 → 候选清单确认 → 装订预警监控\n尾盘 → 触发买入信号（如有，按计划执行）\n盘中 → 止损监控 + 资讯预警\n月末 → 交割单审计\n```\n\n</td></tr>\n</table>'

if old_pipeline in c:
    c = c.replace(old_pipeline, new_pipeline)
    print('流水线: wrapped')
else:
    print('流水线: NOT FOUND')

# ===== 4. Add table of contents to C file =====
# Insert after the frontmatter
toc = '''\n\n**目录：**\n- [一、使命与目标](#一使命与目标)\n- [二、做成什么样：工程目标与产出物原型](#二做成什么样工程目标与产出物原型)\n- [三、什么时候做：实施步骤](#三什么时候做实施步骤)\n  - [M1：策略→指标全映射文档](#m1策略指标全映射文档)\n  - [M2：Python回测框架](#m2python回测框架)\n  - [M3：三类策略回测验证](#m3三类策略回测验证)\n- [四、专题讨论](#附录五-专题讨论)\n- [附录一：三文件分工与偏差检查](#附录一-三文件分工与偏差检查)\n- [附录二：启动资产基线](#附录二-启动资产基线)\n- [附录三：后续衍生工作](#附录三-后续衍生工作)\n- [附录四：待完成零碎工作](#附录四-待完成零碎工作)\n- [附录五：专题讨论](#附录五-专题讨论)\n\n---\n\n'''

# Insert after frontmatter (after the second ---)
# Find the third --- (after name/description/metadata)
count = 0
for i, ch in enumerate(c):
    if ch == '-' and i+2 < len(c) and c[i:i+3] == '---':
        count += 1
        if count == 2:  # after the second --- (end of frontmatter)
            # Insert TOC after the next newline
            insert_at = c.find('\n', i) + 1
            c = c[:insert_at] + toc + c[insert_at:]
            print(f'目录: inserted at position {insert_at}')
            break

# ===== 5. Fix style for font size (五号 = 10.5pt) =====
style = '''<style>
body { font-size: 10.5pt; line-height: 1.5; }
table { font-size: 10pt; }
code { font-size: 9.5pt; }
pre { font-size: 9.5pt; }
h1 { font-size: 16pt; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }
h4 { font-size: 11pt; }
</style>
'''

# Replace existing style or add new one
if '<style>' in c:
    c = re.sub(r'<style>.*?</style>', style.strip(), c, flags=re.DOTALL)
    print('样式: updated')
else:
    c = style + c
    print('样式: added')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('C文件 done')

# ===== Same style for B and A files =====
for fname in ['全局_B交易体系.md', '全局_A盯盘警示卡.md']:
    filepath = f'd:/@VSwork/VS昭明计划VBA优化/_规则文档/{fname}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<style>' in content:
        content = re.sub(r'<style>.*?</style>', style.strip(), content, flags=re.DOTALL)
    else:
        content = style + content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{fname}: style updated')

print('ALL DONE')