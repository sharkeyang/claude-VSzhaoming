"""
MC5.1 stock_selector.py — 四域版每日AI选股引擎

依据：
- MC1.1 策略→指标映射表（选股条件对应Excel列/VBA变量）
- MC1.2 柱排量化规则（柱排字符串解析）
- MC1.3 三层策略伪代码（入场/出场逻辑）
- MC1.5 四域伪代码.md（四域判定逻辑）

选股流程：
  ① 一票否决（WXCD/WXZC/DXZE）
  ② 四域模式匹配（_多长基仓 / <周浮仓> / <日浮仓>）
  ③ 评分排序（综合趋势强度/柱排位置/冲高概率）
  ④ 输出 Top ≤5 推荐标的
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum, auto


# ============================================================
# 操作模式（三种场景）
# ============================================================

class 操作模式(Enum):
    长基仓 = auto()      # 模式①：四域=_多长 → 基仓持有
    周浮仓 = auto()      # 模式②：下柱冲高提示 + 周柱排升开头
    日浮仓 = auto()      # 模式③：日柱排升开头 + 收盘价>DJA


# ============================================================
# 推荐标的数据结构
# ============================================================

@dataclass
class 推荐标的:
    """一只推荐标的的完整信息"""
    名称: str                          # 标的名称
    代码: str                          # szXXXXXX / shXXXXXX
    模式: 操作模式                     # 长基仓/周浮仓/日浮仓
    场景标签: str                      # "_多长基仓" / "<周浮仓>" / "<日浮仓>"

    # 四域体系
    四域周: str = ""                   # 多长/多被/空长/空看
    四域日: str = ""
    日层段: str = ""                   # 买初/持主/持被/卖浮
    日机警: str = ""                   # 警盈/警诱/漏日/漏周

    # 趋势面
    WXCD: str = ""                     # 金/银/唏嘘/屎尿
    WXCD合格: bool = False
    WXZC: float = 0                    # 前周WXZC
    WXZC合格: bool = False
    DXZE: float = 0                    # 今日DXZE
    DXZE合格: bool = False
    DXZD: float = 0                    # 日线条件
    DXZD合格: bool = False

    # 柱排信息
    柱排周: str = ""
    柱排周_升开头: bool = False
    柱排日: str = ""
    柱排日_升开头: bool = False

    # 均线状态
    ZA日: float = 0                    # DJA站稳天数
    ZE日: float = 0                    # DJE状态
    ZB日: float = 0                    # DJB状态
    ZC日: float = 0                    # DJC状态
    ZD日: float = 0                    # DJD状态

    # 冲高信号
    冲高提示: str = ""
    冲高有信号: bool = False

    # 诱多甄别
    通过日诱: bool = True
    命中日诱规则: str = ""             # 如果未通过，记录命中的规则

    # 评分
    综合评分: int = 0                  # 0-100
    评分明细: Dict[str, int] = field(default_factory=dict)

    # 操作建议
    操作建议: str = ""                 # "买入基仓" / "下周冲高" / "下日冲高"
    推荐仓位: str = ""                 # "基仓5000 + 浮仓2000" 等
    止盈条件: str = ""
    止损条件: str = ""
    应对预案: List[str] = field(default_factory=list)

    # 小传
    小传: str = ""                     # 自动生成

    def 小传HTML(self) -> str:
        """生成HTML小传卡片"""
        模式标签 = {
            操作模式.基仓长期: "长期持有(基仓)",
            操作模式.下周冲高: "下周冲高(浮仓)",
            操作模式.下日冲高: "下日冲高(浮仓)",
        }
        场景 = 模式标签.get(self.模式, str(self.模式.value))

        lines = [
            f'<div style="border:1px solid #ccc;padding:12px;margin:8px 0;border-radius:4px;">',
            f'<h3 style="margin:0 0 8px 0;color:#1a5276;">{场景} — {self.名称}({self.代码})</h3>',
            f'<div style="font-size:13px;line-height:1.6;">',
            f'<b>评分：</b>{self.综合评分}/100  ',
            f'<b>WXCD：</b>{self.WXCD}  ',
            f'<b>柱排日：</b>{self.柱排日}<br/>',
            f'<b>操作：</b>{self.操作建议}<br/>',
            f'<b>仓位：</b>{self.推荐仓位}<br/>',
            f'<b>止盈：</b>{self.止盈条件}<br/>',
            f'<b>止损：</b>{self.止损条件}',
        ]
        if self.命中日诱规则:
            lines.append(f'<br/><span style="color:red;">⚠️ 日诱警告：{self.命中日诱规则}</span>')
        lines.extend([
            f'<br/><b>预案：</b>',
        ])
        for p in self.应对预案:
            lines.append(f'{p} | ')
        lines.append('</div></div>')
        return ''.join(lines)


# ============================================================
# 一票否决（硬条件过滤）
# ============================================================

def 一票否决(row: pd.Series) -> tuple:
    """
    M4 第1层：硬性过滤（4条一票否决）

    Returns:
        (通过: bool, 拒绝原因: str)
    """
    # ① WXCD = 金/银（排除屎尿唏嘘）
    if not row.get("WXCD合格", False):
        return False, "WXCD不合格"

    # ② 前周 WXZC > 0
    if not row.get("前周WXZC>0", False):
        return False, "前周WXZC<=0"

    # ③ 今日 DXZE > 0
    if not row.get("今日DXZE>0", False):
        return False, "今日DXZE<=0"

    # ④ DXZD > 0（日线条件）
    if not row.get("DXZD>0", False):
        return False, "DXZD<=0"

    return True, ""


# ============================================================
# 日诱甄别（5条剔除规则）
# ============================================================

def 日诱甄别(row: pd.Series) -> tuple:
    """
    M4 第3层：下日冲高场景的诱多甄别

    Returns:
        (通过: bool, 命中规则编号)
    """
    # 规则①：DXAB<己>负交+上破DJA+DJB
    btab = row.get("护型DXAB", 0)
    if isinstance(btab, str):
        # DXAB可能是"己"/"甲乙"/"丙"等字符串，己=0(正交边缘)
        if btab in ("甲", "乙"):
            btab_val = 1
        elif btab == "己":
            btab_val = 0
        else:
            btab_val = -1
    else:
        btab_val = btab if pd.notna(btab) else 0

    za日 = row.get("ZA日", 0)
    zb日 = row.get("ZB日", 0)
    za日 = za日 if pd.notna(za日) else 0
    zb日 = zb日 if pd.notna(zb日) else 0

    if btab_val <= 0 and za日 > 0 and zb日 > 0:
        return False, "①"

    # 规则②：主升后连阴回归DJA+大阳柱
    柱排日 = str(row.get("柱排日", ""))
    if "跌" in 柱排日 and "连" in 柱排日:
        # 简化：跌连模式后突然转升
        pass

    # 规则③：DJA之上连阴/阴阳阴+鼎
    鼎 = row.get("鼎日", 0)
    if pd.notna(鼎) and 鼎 == 1 and ("连" in 柱排日 or "阴" in 柱排日):
        return False, "③"

    # 规则④：下破DJA须等再站上
    if za日 <= 0:
        return False, "④"

    # 规则⑤：反复震荡（DTZA<3视为未站稳）
    if za日 < 3:
        return False, "⑤"

    return True, ""


# ============================================================
# 评分引擎
# ============================================================

def 计算评分(row: pd.Series, 模式: 操作模式) -> tuple:
    """
    综合评分（满分100）

    维度：
    - 周仓出章（原仓月，出章模式）：25分
    - 大局（市场状态WXCD）：20分
    - 护型（趋势方向）：20分
    - 动量（短期延续/反转）：10分
    - 周仓出节（原仓周，出节模式）：10分
    - 漏提示（模式识别）：10分
    - 日历效应：5分
    """
    score = 0
    明细 = {}

    # 1. 周仓出章（WXCD大局）— 25分
    wxcd = str(row.get("WXCD", ""))
    if "金" in wxcd:
        score += 25
        明细["周仓出章"] = 25
    elif "银" in wxcd:
        score += 15
        明细["周仓出章"] = 15
    else:
        明细["周仓出章"] = 0

    # 2. 大局（WXZC/ZC周）— 20分
    zc周 = row.get("ZC周", 0)
    if pd.notna(zc周) and zc周 > 0:
        score += 20
        明细["大局"] = 20
    else:
        明细["大局"] = 0

    # 3. 护型（DXAB/ZA日）— 20分
    za日 = row.get("ZA日", 0)
    if pd.notna(za日) and za日 >= 3:
        score += 20
        明细["护型"] = 20
    elif pd.notna(za日) and za日 > 0:
        score += 10
        明细["护型"] = 10
    else:
        明细["护型"] = 0

    # 4. 动量（柱排升开头）— 10分
    if 模式 == 操作模式.下日冲高:
        if row.get("柱排日_升开头", False):
            score += 10
            明细["动量"] = 10
        else:
            明细["动量"] = 0
    elif 模式 == 操作模式.下周冲高:
        if row.get("柱排周_升开头", False):
            score += 10
            明细["动量"] = 10
        else:
            明细["动量"] = 0
    else:
        明细["动量"] = 5  # 基仓模式给一半

    # 5. 周仓出节（ZB周）— 10分
    zb周 = row.get("ZB周", 0)
    if pd.notna(zb周) and zb周 > 0:
        score += 10
        明细["周仓出节"] = 10
    else:
        明细["周仓出节"] = 0

    # 6. 漏提示（HA偏）— 10分
    ha偏 = row.get("HA偏", 0)
    if pd.notna(ha偏) and 0 < ha偏 < 6:
        score += 10
        明细["漏提示"] = 10
    elif pd.notna(ha偏) and ha偏 >= 6:
        score += 3  # 太高反而不好
        明细["漏提示"] = 3
    else:
        明细["漏提示"] = 0

    # 7. 日历效应 — 5分
    # 简化：周一到周四给下日冲高加分，周五给下周冲高加分
    if 模式 == 操作模式.下日冲高:
        明细["日历效应"] = 5
        score += 5
    else:
        明细["日历效应"] = 2
        score += 2

    return score, 明细


# ============================================================
# 场景分类（模式匹配）
# ============================================================

def 分类模式(row: pd.Series) -> List[操作模式]:
    """
    MC3 第2层：四域模式分类

    Returns:
        该标的可能匹配的模式列表
    """
    模式 = []

    # 模式①：_多长基仓候选（四域周=多长 或 四域日=多长）
    四域周 = str(row.get("四域周", ""))
    四域日 = str(row.get("四域日", ""))
    if 四域周 == "多长" or 四域日 == "多长":
        模式.append(操作模式.长基仓)

    # 模式②：<周浮仓>候选
    if (row.get("柱排周_升开头", False) and
            row.get("冲高有信号", False)):
        模式.append(操作模式.周浮仓)

    # 模式③：<日浮仓>候选
    if (row.get("柱排日_升开头", False) and
            row.get("ZA日", 0) is not None and
            row.get("ZA日", 0) >= 3):
        模式.append(操作模式.日浮仓)

    return 模式


# ============================================================
# 生成小传
# ============================================================

def 生成小传(rec: 推荐标的) -> str:
    """为推荐标的生成结构化小传"""
    lines = []

    if rec.模式 == 操作模式.基仓长期:
        lines.append(f"【场景：长期持有】")
        lines.append(f"  ┌─ 基仓条件")
        lines.append(f"  │   ├── 乾坤条件满足")
        lines.append(f"  │   └── WXCD={rec.WXCD}")
        lines.append(f"  ├─ 操作建议")
        lines.append(f"  │   ├── 基仓：5000（持有不动）")
        lines.append(f"  │   └── 浮仓：上限20000")
        lines.append(f"  └─ 止损：跌破DJE全部清仓")

    elif rec.模式 == 操作模式.下周冲高:
        lines.append(f"【场景：下周会涨】")
        lines.append(f"  ┌─ 下周判断")
        lines.append(f"  │   ├── 下柱冲高提示={rec.冲高提示}")
        lines.append(f"  │   └── 柱排周={rec.柱排周}")
        lines.append(f"  ├─ 趋势面")
        lines.append(f"  │   ├── WXCD={rec.WXCD} | WXZC={rec.WXZC:.1f}")
        lines.append(f"  │   └── DJE={rec.ZE日:.1f} DJD={rec.ZD日:.1f}")
        lines.append(f"  ├─ 操作建议")
        lines.append(f"  │   ├── 场景：基仓5000 + 下周冲高仓20000")
        lines.append(f"  │   ├── 入场：尾盘14:50-15:00")
        lines.append(f"  │   └── 应对预案：")
        lines.append(f"  │       ├── 涨停 → 持有不动")
        lines.append(f"  │       ├── 跌2% → 观察是否破DJA")
        lines.append(f"  │       ├── 跌破DJE → 全部清仓")
        lines.append(f"  │       └── 冲高达标 → 平浮仓，留基仓")
        lines.append(f"  └─ 推荐仓位")
        lines.append(f"      ├── 基仓：5000")
        lines.append(f"      └── 浮仓：上限20000")

    elif rec.模式 == 操作模式.下日冲高:
        lines.append(f"【场景：下日冲高】")
        lines.append(f"  ┌─ 日柱形态分析")
        lines.append(f"  │   ├── 柱排日={rec.柱排日}")
        lines.append(f"  │   ├── 收盘价>DJA（ZA日={rec.ZA日:.0f}天站稳）")
        lines.append(f"  │   └── 日诱甄别：通过 ✅")
        lines.append(f"  ├─ 操作建议")
        lines.append(f"  │   ├── 场景：下日冲高仓（浮仓上限20000）")
        lines.append(f"  │   ├── 止盈：次日冲高3%平仓")
        lines.append(f"  │   └── 止损：下破DJD平仓")
        lines.append(f"  └─ 推荐仓位：20000")

    return "\n".join(lines)


# ============================================================
# 主选股函数
# ============================================================

def 选股(df: pd.DataFrame, 名称: str = "未知", top_n: int = 5) -> List[推荐标的]:
    """
    M4 选股引擎：全市场选股

    流程：
    ① 一票否决（硬条件过滤）
    ② 模式匹配（基仓/下周冲高/下日冲高）
    ③ 评分排序（综合评分）
    ④ 输出 Top ≤5

    Args:
        df: 全市场数据（来自M2.1加载）
        名称: 标的池名称
        top_n: 返回前N只推荐

    Returns:
        推荐标的列表
    """
    候选 = []

    for idx, row in df.iterrows():
        # 第1层：一票否决
        通过, 原因 = 一票否决(row)
        if not 通过:
            continue

        # 第2层：模式匹配
        模式列表 = 分类模式(row)
        if not 模式列表:
            continue

        for 模式 in 模式列表:
            # 第3层：日诱甄别（仅下日冲高需要）
            if 模式 == 操作模式.下日冲高:
                诱多通过, 诱多规则 = 日诱甄别(row)
                if not 诱多通过:
                    continue
            else:
                诱多通过 = True
                诱多规则 = ""

            # 第4层：评分
            分数, 明细 = 计算评分(row, 模式)

            # 构建推荐标的
            rec = 推荐标的(
                名称=名称,
                代码="",
                模式=模式,
                场景标签=_场景标签(模式),
                WXCD=str(row.get("WXCD", "")),
                WXCD合格=True,
                WXZC=row.get("ZC周", 0) or 0,
                WXZC合格=True,
                DXZE=row.get("ZE日", 0) or 0,
                DXZE合格=True,
                DXZD=row.get("ZD日", 0) or 0,
                DXZD合格=True,
                柱排周=str(row.get("柱排周", "")),
                柱排周_升开头=bool(row.get("柱排周_升开头", False)),
                柱排日=str(row.get("柱排日", "")),
                柱排日_升开头=bool(row.get("柱排日_升开头", False)),
                ZA日=row.get("ZA日", 0) or 0,
                ZE日=row.get("ZE日", 0) or 0,
                ZB日=row.get("ZB日", 0) or 0,
                ZC日=row.get("ZC日", 0) or 0,
                ZD日=row.get("ZD日", 0) or 0,
                冲高提示=str(row.get("冲高提示", "")),
                冲高有信号=bool(row.get("冲高有信号", False)),
                通过日诱=诱多通过,
                命中日诱规则=诱多规则,
                综合评分=分数,
                评分明细=明细,
                操作建议=_操作建议(模式, 分数),
                推荐仓位=_推荐仓位(模式),
                止盈条件=_止盈条件(模式),
                止损条件=_止损条件(模式),
                应对预案=_应对预案(模式),
            )
            rec.小传 = 生成小传(rec)
            候选.append(rec)

    # 按评分排序，取Top N
    候选.sort(key=lambda x: x.综合评分, reverse=True)
    return 候选[:top_n]


def _场景标签(模式: 操作模式) -> str:
    return {
        操作模式.基仓长期: "长期持有",
        操作模式.下周冲高: "下周会涨",
        操作模式.下日冲高: "下日冲高",
    }[模式]


def _操作建议(模式: 操作模式, 分数: int) -> str:
    if 模式 == 操作模式.基仓长期:
        return "买入基仓5000" if 分数 >= 70 else "持有基仓"
    elif 模式 == 操作模式.下周冲高:
        return "尾盘买入下周冲高仓"
    else:
        return "尾盘买入下日冲高仓"


def _推荐仓位(模式: 操作模式) -> str:
    if 模式 == 操作模式.基仓长期:
        return "基仓5000"
    else:
        return "浮仓上限20000"


def _止盈条件(模式: 操作模式) -> str:
    if 模式 == 操作模式.基仓长期:
        return "跌破DJE全部清仓"
    elif 模式 == 操作模式.下周冲高:
        return "下周临涨幅达标 / 周五平仓"
    else:
        return "次日冲高3%平仓"


def _止损条件(模式: 操作模式) -> str:
    if 模式 == 操作模式.基仓长期:
        return "跌破DJE全部清仓"
    elif 模式 == 操作模式.下周冲高:
        return "下破DJB平仓"
    else:
        return "下破DJD平仓"


def _应对预案(模式: 操作模式) -> List[str]:
    if 模式 == 操作模式.基仓长期:
        return ["上涨 → 持有", "下跌 → 不破DJE继续持有", "破DJE → 清仓"]
    elif 模式 == 操作模式.下周冲高:
        return ["涨停 → 持有", "跌2% → 观察DJA", "破DJE → 清仓", "冲高达标 → 平浮仓"]
    else:
        return ["冲高3% → 平仓", "下破DJD → 止损"]


# ============================================================
# 输出格式化
# ============================================================

def 打印选股结果(候选: List[推荐标的]):
    """打印选股结果"""
    if not 候选:
        print("  无推荐标的")
        return

    print(f"\n{'='*60}")
    print(f"  AI选股结果 — {len(候选)} 只推荐")
    print(f"{'='*60}")

    for i, rec in enumerate(候选, 1):
        print(f"\n  #{i} 【{rec.场景标签}】{rec.名称}")
        print(f"      模式: {rec.模式.name}")
        print(f"      评分: {rec.综合评分}/100")
        print(f"      WXCD: {rec.WXCD}")
        print(f"      柱排日: {rec.柱排日}")
        print(f"      柱排周: {rec.柱排周}")
        print(f"      操作: {rec.操作建议}")
        print(f"      仓位: {rec.推荐仓位}")
        print(f"      止盈: {rec.止盈条件}")
        print(f"      止损: {rec.止损条件}")
        print(f"      预案: {' | '.join(rec.应对预案)}")
        print(f"      ── 小传 ──")
        for line in rec.小传.split("\n"):
            print(f"      {line}")


if __name__ == "__main__":
    from M2_1_数据加载 import load_ld_data

    # 用sz300304做测试
    df = load_ld_data("算展D.sz300304.xlsx")
    结果 = 选股(df, "sz300304测试", top_n=5)
    打印选股结果(结果)
