# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction \| insight \| knowledge_gap \| best_practice

---
## [LRN-20260805-001] correction

**Logged**: 2026-08-05
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Three-level classification (DXEF/DXCD/DXAB) must be evaluated by "当前位置 × 明日概率" framework, not by DSHR>2 (short-term volatility) or →ZE>0 alone (circular with DXEF).

### Details
Three iterations of metric correction:
1. First used →ZE>0 → user pointed out "already determined by DXEF, circular reasoning"
2. Then used DSHR>2 → user pointed out "classification is about unlimited vs limited gain, not short-term volatility"
3. Then used →ZE>0+ZC>0 for unlimited gain → user pointed out "嘘 means DXZE<0, current position is limited even if →ZE>0+ZC>0 is high"
4. Final framework: 当前位置(DXEF决定无限/有限) × 明日概率(→ZE>0 = 留在/进入无限区的概率)

### Suggested Action
When analyzing classification systems, always start with first principles: what is the system's actual purpose? For 三级分类, the value is 83.9pp separation between S级(92.2%) and 禁止级(8.3%) in →ZE>0, not DSHR>2 (which only has 2.8pp separation).

### Metadata
- Source: user_feedback
- Related Files: ____temp/三级分类框架结论_完整符号版.md
- Tags: 日冲, 三级分类, 指标选择

---

## [LRN-20260805-002] correction

**Logged**: 2026-08-05
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Never use abbreviated notation for complex concepts. Always write full notation like "DXEF=嘘, DXCD=下, DXAB=上" instead of "嘘/下/上".

### Details
User repeatedly asked for clarification of abbreviated notation. Each time a shorthand like "嘘/下/上" or "→ZE+ZC" was used, the user couldn't understand. The correct approach is to always write the full, explicit notation:
- Full: "DXEF=嘘, DXCD=下, DXAB=上 → →ZE>0=77.6%"
- Bad: "嘘/下/上 →ZE>0=77.6%"
- Full: "→ZE>0+ZC>0" instead of "→ZE+ZC"

### Suggested Action
Write all analysis with explicit full notation from the start. No abbreviations, no shortcuts.

### Metadata
- Source: user_feedback
- Tags: notation, clarity

---

## [LRN-20260805-003] insight

**Logged**: 2026-08-05
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
QC质量比 = →ZE>0+ZC>0 / →ZE>0 量化了"进入DJE后能否守住DJC"的质量，是假突破的量化指标。

### Details
DXEF=嘘, DXCD=中 系列的 QC 比仅 0.49~0.64，说明即使进入 DJE，也大概率站不上 DJC。这是"假突破"的量化识别指标。而 DXEF=嘘, DXCD=上 系列的 QC 比 0.90~0.97，进入后极大概率守住 DJC。

### Suggested Action
Use QC ratio as a secondary filter: QC < 0.70 意味着即使 ZE 转正也站不上 ZC，收益仍受 JC 限制。

### Metadata
- Source: analysis
- Tags: 日冲, QC质量比, 假突破
