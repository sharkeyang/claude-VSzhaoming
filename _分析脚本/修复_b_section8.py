with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix tab indentation on line 977 (the _多被 line)
c = c.replace('\t    _多被     → 可参与（视情况开基仓）', '	    _多被     → 可参与（视情况开基仓）')
# Better: replace the tab with spaces
c = c.replace('\t_多被', '    _多被')

# Remove the "待B文件同步" section (lines 986-1010 or so)
marker = '**5. 待B文件同步（四区划+_多长体系确定后统一更新）**'
if marker in c:
    start = c.find(marker)
    # Find the next section header (starts with ## or ---)
    end = c.find('---', start)
    if end < 0:
        end = c.find('#', start + 1)
    # Remove from marker to end
    c = c[:start] + c[end:]

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('C done')

# ============================================
# B文件：更新 §八 三层策略框架
# ============================================
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'r', encoding='utf-8') as f:
    b = f.read()

# Find the §八 section and replace it
section_start = b.find('## 八、三层策略分类框架')
section_end = b.find('## 九、操盘时间线')

if section_start >= 0 and section_end >= 0:
    new_section = '''## 八、三层策略框架（四区划体系）

> 基于四区划（_多长/_多被/_空看/_空长）的三种独立策略，每种有明确的触发时机和退出条件。

---

### 🟢 策略一：_多长策略（基仓持有）

**适用对象：** 区划判定为 `_多长`（金+甲乙己）
**触发时机：** 持续有效，无时间限定

```
持有条件：区划 = _多长
             AND 前周WXZC>0 AND 今日DXZE>0
             AND WXCD>0,WXZC>0（金）
             AND WXZB>0（甲乙己）
离场条件：WXZC<0 → 全部清仓，无一例外
```

**对应仓位：** 基仓（单一仓位，不区分基仓/浮仓/减仓/清仓）

---

### 🟡 策略二：浮仓（周频）— 原下周冲高

**适用对象：** 依赖于周级别指标进行浮仓操作
**触发时机：** 前周五至本周四尾盘均可，优选前周五

```
入场条件：区划 = _多长
         AND 在 DJE&DJC 之上
         AND 下柱冲高提示 != ""
         AND 柱排周 以"升"开头
出场条件：
  ├── 🟢 止盈：下周临涨幅达标 → 平仓
  └── 🔴 止损：下破 DJC → 平浮仓（基仓不受影响）
时间限制：周五收盘前无论盈亏平仓
```

**买入时点弹性：**
- 🟢 **优选前周五尾盘** — 完整吃到下周冲高幅度
- 🟡 **如预感下周初冲低** — 可等冲低后再介入（周一~周四）
- 🔴 **必须在周五收盘前卖出**

---

### 🔵 策略三：浮仓（日频）— 原下日冲高

**适用对象：** 日柱排=升开头 AND 收盘价>DJA
**触发时机：** 周一到周四尾盘（当日判断当日操作）

```
入场条件：区划 = _多长
         AND 在 DJE&DJC 之上
         AND 日柱排 以"升"开头
         AND 收盘价 > DJA
         AND 通过诱多甄别（见下方）

⚠️ 前置检查：甄别已冲高
  如果标的已经大幅冲高（DSHA很高），则不适用本策略
  → 已冲高的标的只保持基仓，不加浮仓

⛔ 核心风控：剔除"日诱"
  以下情况即使柱排=升开头也禁止开仓：

  ①  DXAB=<己>，DXAB负交时同时上破DJA与DJB → 形态看似突破，实则诱多
  ②  主升后以连阴回归DJA，随后出现大阳柱 → 反弹诱多，非趋势延续
  ③  在DJA之上以连阴或阴阳阴，回归DJA后，出现从DJA之下上穿DJA的鼎 → 鼎在DJA附近不可靠
  ④  下破DJA → 须等再站上DJA才算信号，不能以下破DJA作为入场信号
  ⑤  反复围绕DJA震荡（DTZA>3 或 日主升后的日震荡） → 日诱

出场条件：
  ├── 🟢 止盈：次日冲高达标 → 平仓
  └── 🔴 止损：下破 DJC → 平浮仓（基仓不受影响）
时间限制：次日收盘前无论盈亏平仓
```

---

### 仓位退出规则总表

| 仓位 | 适用区划 | 介入条件 | 退出条件 |
|:----|:--------|:---------|:--------|
| **基仓** | _多长 | 区划=_多长 | WXZC<0 |
| **浮仓（周频）** | _多长 | _多长 + DJE&DJC之上 + 周指标 | 下破DJC或周五收盘前 |
| **浮仓（日频）** | _多长 | _多长 + DJE&DJC之上 + 日指标 | 下破DJC或次日收盘前 |'''

    b = b[:section_start] + new_section + b[section_end:]
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'w', encoding='utf-8') as f:
        f.write(b)
    print('B done')
else:
    print('Section markers not found')