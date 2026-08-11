import re

with open(r'_主文档/MC3.1_研究月基策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Extract all sections
# ============================================================

# §2.1 raw content
m_21 = re.search(r'^### 2\.1 V1 月基命分（几何均值）\n\n(.*?)(?=\n^### 2\.2 V2 月基策分)', content, re.MULTILINE | re.DOTALL)
sec_21_raw = m_21.group(1)

# Chapter 4 raw content
m_ch4 = re.search(r'^## 第四章：月基命分详解（选股）\n\n(.*?)(?=\n^## 第五章)', content, re.MULTILINE | re.DOTALL)
sec_ch4_raw = m_ch4.group(1)

# §2.2 raw content
m_22 = re.search(r'^### 2\.2 V2 月基策分（5周维持）\n\n(.*?)(?=\n^### 2\.3 V3 月基带向)', content, re.MULTILINE | re.DOTALL)
sec_22_raw = m_22.group(1)

# §2.3 raw content
m_23 = re.search(r'^### 2\.3 V3 月基带向（双向带动\+）\n\n(.*?)(?=\n^### 2\.4 三变量联合决策)', content, re.MULTILINE | re.DOTALL)
sec_23_raw = m_23.group(1)

# §2.4 raw content
m_24 = re.search(r'^### 2\.4 三变量联合决策\n\n(.*?)(?=\n^## 第三章)', content, re.MULTILINE | re.DOTALL)
sec_24_raw = m_24.group(1)

# ============================================================
# 2. Extract sub-sections from §2.1 raw
# ============================================================

# Variable table
m_var = re.search(r'^(\| 项目 .*?)\n\n', sec_21_raw, re.DOTALL)
var_table = m_var.group(1).strip() if m_var else ''

# 设计理念 paragraph
design_idea = ''
if '**设计理念：**' in sec_21_raw:
    design_idea = '**设计理念：** 金升介入->持有->WXZC<0退出，每次交易独立。命分回答"平均每次能赚多少"。几何均值自然惩罚波动（亏一次会拉低整体），过滤假信号。'

# Distribution table
dist_table = ''
dist_match = re.search(r'(\*\*全量7463只分布：\*\*.*?)(?=\n\n\*\*仁慈级)', sec_21_raw, re.DOTALL)
if dist_match:
    dist_table = dist_match.group(1).strip()

# ============================================================
# 3. Extract sub-sections from Chapter 4
# ============================================================

# 4.1 设计初衷
m_41 = re.search(r'^### 4\.1 设计初衷：从股性到命分\n\n(.*?)(?=\n^### 4\.2 设计原理)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_41 = m_41.group(1).strip() if m_41 else ''

# 4.2 设计原理
m_42 = re.search(r'^### 4\.2 设计原理\n\n(.*?)(?=\n^### 4\.3 评分原则)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_42 = m_42.group(1).strip() if m_42 else ''

# 4.3 评分原则
m_43 = re.search(r'^### 4\.3 评分原则\n\n(.*?)(?=\n^### 4\.4 条件筛选意义解释)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_43 = m_43.group(1).strip() if m_43 else ''

# 4.4 条件筛选意义解释
m_44 = re.search(r'^### 4\.4 条件筛选意义解释\n\n(.*?)(?=\n^### 4\.5 与周冲策分卡的关系)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_44 = m_44.group(1).strip() if m_44 else ''

# 4.5 与周冲策分卡的关系
m_45 = re.search(r'^### 4\.5 与周冲策分卡的关系\n\n(.*?)(?=\n^### 4\.6 仁慈级股票列表)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_45 = m_45.group(1).strip() if m_45 else ''

# 4.6 仁慈级股票列表
m_46 = re.search(r'^### 4\.6 仁慈级股票列表\n\n(.*)', sec_ch4_raw, re.MULTILINE | re.DOTALL)
sec_46 = m_46.group(1).strip() if m_46 else ''

print(f"§2.1 var_table: {len(var_table)} chars")
print(f"§2.1 dist_table: {len(dist_table)} chars")
print(f"Ch4 sec_41: {len(sec_41)} chars")
print(f"Ch4 sec_42: {len(sec_42)} chars")
print(f"Ch4 sec_43: {len(sec_43)} chars")
print(f"Ch4 sec_44: {len(sec_44)} chars")
print(f"Ch4 sec_45: {len(sec_45)} chars")
print(f"Ch4 sec_46: {len(sec_46)} chars")

# ============================================================
# 4. Build merged §2.1
# ============================================================

new_21 = f"""#### 2.1.1 变量定义

{var_table}

#### 2.1.2 设计初衷：从股性到命分

**股性的本质：** 一只股票在四域操盘法下的持仓收益特征。具体做法：金升介入 -> 下破WXZC退出 -> 统计该段累计收益 -> 跑遍该股所有时段 -> 得到全生命周期累计收益。

**命分 = 几何均值 = (prod(1+每次收益))^(1/交易次数) - 1**

{design_idea}

#### 2.1.3 设计原理

{sec_42}

#### 2.1.4 全量7463只分布

{dist_table}

#### 2.1.5 评分原则

{sec_43}

#### 2.1.6 条件筛选意义解释

{sec_44}

#### 2.1.7 与周冲策分卡的关系

{sec_45}

#### 2.1.8 仁慈级股票列表

{sec_46}

> 仁慈庄家特征：金升期间柱排方向稳定、震仓频率低、最大收益高。

---

"""

# ============================================================
# 5. Parse §2.2 into sub-sections
# ============================================================

# 2.2.1 变量定义
m_221 = re.search(r'^(\| 项目 .*?)\n\n', sec_22_raw, re.DOTALL)
sec_221 = m_221.group(1).strip() if m_221 else ''

# 2.2.2 评分模型
m_222 = re.search(r'(\*\*评分模型：\*\*.*?)(?=\n\n\*\*基础分表)', sec_22_raw, re.DOTALL)
sec_222 = m_222.group(1).strip() if m_222 else ''

# 2.2.3 基础分表
m_223 = re.search(r'(\*\*基础分表.*?)(?=\n\n\*\*调节分)', sec_22_raw, re.DOTALL)
sec_223 = m_223.group(1).strip() if m_223 else ''

# 2.2.4 调节分
m_224 = re.search(r'(\*\*调节分：\*\*.*?)(?=\n\n\*\*全量验证结果)', sec_22_raw, re.DOTALL)
sec_224 = m_224.group(1).strip() if m_224 else ''

# 2.2.5 全量验证结果
m_225 = re.search(r'(\*\*全量验证结果.*?)(?=\n\n\*\*使用建议)', sec_22_raw, re.DOTALL)
sec_225 = m_225.group(1).strip() if m_225 else ''

# 2.2.6 使用建议
m_226 = re.search(r'(\*\*使用建议：\*\*.*?)(?=\n\n\*\*修正版)', sec_22_raw, re.DOTALL)
sec_226 = m_226.group(1).strip() if m_226 else ''

# 2.2.7 修正版 vs 旧版对比
m_227 = re.search(r'(\*\*修正版.*)', sec_22_raw, re.DOTALL)
sec_227 = m_227.group(1).strip() if m_227 else ''

# Clean up: strip bold headers from sub-section content
def strip_header(text, prefix):
    """Remove bold header prefix if present."""
    if text.startswith(prefix):
        rest = text[len(prefix):]
        if rest.startswith('\n'):
            rest = rest[1:]
        return rest.strip()
    return text

# 评分模型 - extract code block
sec_222_clean = sec_222
if sec_222.startswith('**评分模型：**'):
    body = sec_222[len('**评分模型：**\n'):].strip()
    # Check if it already has a code block
    if not body.startswith('```'):
        body = '```\n' + body + '\n```'
    sec_222_clean = body

# 调节分 - strip header
sec_224_clean = strip_header(sec_224, '**调节分：**')
sec_226_clean = strip_header(sec_226, '**使用建议：**')

# 基础分表 - strip header
sec_223_clean = strip_header(sec_223, '**基础分表（波型×柱排->续持率取整）：**')

# 全量验证结果 - strip header
sec_225_clean = sec_225
for prefix in ['**全量验证结果（7463只×121万周，只认金升）：**', '**全量验证结果']:
    if sec_225.startswith(prefix):
        sec_225_clean = strip_header(sec_225, prefix)
        break

# 修正版对比 - strip header
sec_227_clean = strip_header(sec_227, '**修正版 vs 旧版（含银升）对比：**')
# Remove trailing ---
if sec_227_clean.endswith('---'):
    sec_227_clean = sec_227_clean[:-3].strip()

new_22 = f"""#### 2.2.1 变量定义

{sec_221}

#### 2.2.2 评分模型

{sec_222_clean}

#### 2.2.3 基础分表（波型×柱排->续持率取整）

{sec_223_clean}

#### 2.2.4 调节分

{sec_224_clean}

#### 2.2.5 全量验证结果（7463只×121万周，只认金升）

{sec_225_clean}

#### 2.2.6 使用建议

{sec_226_clean}

#### 2.2.7 修正版 vs 旧版（含银升）对比

{sec_227_clean}

---

"""

# ============================================================
# 6. §2.3 - remove ①②③④⑤ decorative numbering within 2.3.2
# ============================================================

sec_23_clean = sec_23_raw
replacements = [
    ('**① WXAB > 0 — 月基策略的生效前提**\n\n', ''),
    ('**② WXAB各等级质量排名**\n\n', ''),
    ('**③ WXAB引领WXCD（全量200,534次跟随事件，双向）**\n\n', ''),
    ('**④ 对月基策略的修正建议**\n\n', ''),
    ('**⑤ WXAB > 0 作为全局前置条件分析**\n\n', ''),
]
for old, new in replacements:
    sec_23_clean = sec_23_clean.replace(old, new)

# ============================================================
# 7. Build new Chapter 4 pointer
# ============================================================

new_ch4 = """## 第四章：月基命分详解（选股）

> 本章内容已合并至 [第二章 §2.1 V1 月基命分（几何均值）](#21-v1-月基命分几何均值)。
>
> 月基命分（几何均值）是月基策略的核心选股维度，详细内容包括：
> - [2.1.1 变量定义](#211-变量定义)
> - [2.1.2 设计初衷：从股性到命分](#212-设计初衷从股性到命分)
> - [2.1.3 设计原理](#213-设计原理)
> - [2.1.4 全量7463只分布](#214-全量7463只分布)
> - [2.1.5 评分原则](#215-评分原则)
> - [2.1.6 条件筛选意义解释](#216-条件筛选意义解释)
> - [2.1.7 与周冲策分卡的关系](#217-与周冲策分卡的关系)
> - [2.1.8 仁慈级股票列表](#218-仁慈级股票列表)

---

"""

# ============================================================
# 8. Build TOC
# ============================================================

new_toc = """**目录：**

- [第一章：祖训——只做金银，等金升再进场](#第一章祖训只做金银等金升再进场)
  - [1.1 核心规则](#11-核心规则)
  - [1.2 数据支撑：银升 vs 金升 全量对比](#12-数据支撑银升-vs-金升-全量对比)
  - [1.3 结论](#13-结论)
- [第二章：三变量框架](#第二章三变量框架)
  - [2.1 V1 月基命分（几何均值）](#21-v1-月基命分几何均值)
    - [2.1.1 变量定义](#211-变量定义)
    - [2.1.2 设计初衷：从股性到命分](#212-设计初衷从股性到命分)
    - [2.1.3 设计原理](#213-设计原理)
    - [2.1.4 全量7463只分布](#214-全量7463只分布)
    - [2.1.5 评分原则](#215-评分原则)
    - [2.1.6 条件筛选意义解释](#216-条件筛选意义解释)
    - [2.1.7 与周冲策分卡的关系](#217-与周冲策分卡的关系)
    - [2.1.8 仁慈级股票列表](#218-仁慈级股票列表)
  - [2.2 V2 月基策分（5周维持）](#22-v2-月基策分5周维持)
    - [2.2.1 变量定义](#221-变量定义)
    - [2.2.2 评分模型](#222-评分模型)
    - [2.2.3 基础分表（波型×柱排->续持率取整）](#223-基础分表波型柱排续持率取整)
    - [2.2.4 调节分](#224-调节分)
    - [2.2.5 全量验证结果（7463只×121万周，只认金升）](#225-全量验证结果7463只121万周只认金升)
    - [2.2.6 使用建议](#226-使用建议)
    - [2.2.7 修正版 vs 旧版（含银升）对比](#227-修正版-vs-旧版含银升对比)
  - [2.3 V3 月基带向（双向带动+）](#23-v3-月基带向双向带动)
    - [2.3.1 WXAB->WXCD四象限](#231-wxabwxcd四象限)
    - [2.3.2 数据验证：WXAB引领WXCD（全量7463只）](#232-数据验证wxab引领wxcd全量7463只)
    - [2.3.3 WXAB > 0 作为全局前置条件分析](#233-wxab--0-作为全局前置条件分析)
  - [2.4 三变量联合决策](#24-三变量联合决策)
- [第三章：月基策略分类（周层四域->七分类）](#第三章月基策略分类周层四域七分类)
  - [3.1 周层四域 ↔ 月基策略映射](#31-周层四域--月基策略映射)
  - [3.2 分类判定流程](#32-分类判定流程)
  - [3.3 各类信号详解](#33-各类信号详解)
  - [3.4 操作规则](#34-操作规则)
- [第四章：月基命分详解（选股）](#第四章月基命分详解选股)
- [第五章：月基持仓预警与退出](#第五章月基持仓预警与退出)
  - [5.1 WXZB退出信号验证](#51-wxzb退出信号验证)
  - [5.2 WXZA>0延续性分析](#52-wxza0延续性分析)
  - [5.3 消极区操作细则](#53-消极区操作细则)
  - [5.4 退出阶段](#54-退出阶段)
- [第六章：VBA实施计划](#第六章vba实施计划)
  - [6.1 已完成](#61-已完成)
  - [6.2 待完成](#62-待完成)"""

# ============================================================
# 9. Build the full new document
# ============================================================

# Find positions
toc_start = content.index('**目录：**')
toc_end = content.index('\n---\n\n## 第一章：祖训') + 1

ch1_start = content.index('## 第一章：祖训')
ch1_end = content.index('## 第二章：三变量框架')
ch1_section = content[ch1_start:ch1_end]

ch2_header = '## 第二章：三变量框架\n\n'

ch3_start = content.index('## 第三章：月基策略分类')
ch4_start = content.index('## 第四章：月基命分详解')
ch3_section = content[ch3_start:ch4_start]

ch5_start_pos = content.index('## 第五章：月基持仓预警与退出')
ch5_section = content[ch5_start_pos:]

# Everything before TOC
before_toc = content[:toc_start]

# Build full document
new_content = before_toc.strip() + '\n\n' + new_toc + '\n\n---\n\n'
new_content += ch1_section + '\n\n---\n\n'
new_content += ch2_header
new_content += '### 2.1 V1 月基命分（几何均值）\n\n'
new_content += new_21
new_content += '### 2.2 V2 月基策分（5周维持）\n\n'
new_content += new_22
new_content += '### 2.3 V3 月基带向（双向带动+）\n\n'
new_content += sec_23_clean + '\n\n'
new_content += '### 2.4 三变量联合决策\n\n'
new_content += sec_24_raw + '\n\n---\n\n'
new_content += ch3_section + '\n\n---\n\n'
new_content += new_ch4
new_content += ch5_section

with open(r'_主文档/MC3.1_研究月基策略.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('OK')
print(f'Total: {len(new_content)} chars')