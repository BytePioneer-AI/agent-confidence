---
name: agent-confidence-designer
description: "Analyze and design business-specific high/medium/low confidence schemes for Agent + Skill workflows. Use when a developer provides a business context, agent or skill implementation, output structure, acceptance criteria, development-test issues, user self-test issues, or an existing confidence design and needs to decompose results, identify key risks, define high/medium/low conditions, map known problems to affected outputs, recommend where confidence logic should be integrated into existing SQL, code, APIs, rules, workflows, or human review, generate a confidence-design document, or review the completeness of an existing design. Do not use it as a runtime confidence calculator, require a universal validator interface, or impose fixed runtime status enums."
---

# Agent Confidence Designer

帮助开发人员针对一个具体业务 Agent + Skill，分析并设计高、中、低可信等级。

不要把本 Skill 当作运行时置信度计算器。不要强制业务建立独立验证器框架、统一状态协议或统一聚合服务。重点是把业务中的结果、风险、等级条件和实现位置定义清楚。

## 工作模式

先判断属于哪种模式：

1. **新设计**：为新的 Agent + Skill 建立可信等级方案；
2. **现有设计审查**：检查已有方案是否完整、合理、可落地；
3. **问题沉淀**：把新增开发测试或用户自测问题加入可信设计；
4. **变更影响分析**：评估 Agent、Skill、输入输出或业务规则变化的影响。

可以组合使用，但始终按下面的核心流程执行。

## 核心原则

始终遵守：

- 使用高、中、低，不输出没有校准依据的百分比；
- 先拆分结果单元，再定义等级；
- 根据业务验收标准和风险定义等级，不根据模型主观自信定义；
- 将开发测试和用户自测中确认的问题结构化后纳入设计；
- 区分关键业务结果和低影响格式结果；
- 不通过平均分掩盖关键结果风险；
- 将风险定位到字段、记录、单元格、指标、段落、决策或文件结构；
- 为中、低结果给出具体人工核查动作；
- 允许判断逻辑融入现有 SQL、脚本、服务、API、规则、工作流或人工流程；
- 不要求固定的运行时状态枚举、验证器接口或独立置信度计算模块。

详细方法见 [references/methodology.md](references/methodology.md)。

## 输入整理

尽量读取以下材料；缺失时记录假设和待确认问题，不要凭空补充业务规则：

- 业务目标、使用者、下游动作和错误影响；
- Agent 提示词、Skill、工作流、脚本或服务代码；
- 输入、输出和关键中间结果；
- 业务验收标准、支持范围和不支持范围；
- 开发单测、集成测试、回归测试问题；
- 用户自测和验收阶段确认的问题；
- 现有 SQL、API、规则引擎、日志和人工审核流程；
- 已有可信设计。

## 核心流程

### 1. 建立业务上下文

说明：

- 业务目标；
- 输入、处理过程、输出；
- 使用者和下游动作；
- 支持范围；
- 错误影响；
- 当前信息缺口。

### 2. 拆分结果单元

为每个可独立验收的结果定义：

- 名称和示例；
- 所在位置；
- 关键性：`critical`、`high`、`medium`、`low`；
- 业务验收标准；
- 上游依赖；
- 错误后果。

不要只为整个文件定义一个等级。优先拆到能够产生定向核查动作的粒度。

### 3. 结构化已知问题

将每个开发测试或用户自测问题整理为：

- 来源和问题编号；
- 问题描述；
- 触发条件；
- 影响结果；
- 严重程度；
- 可识别方式；
- 对高、中、低的影响；
- 人工核查动作；
- 建议回归测试。

使用 [references/risk-taxonomy.md](references/risk-taxonomy.md) 统一风险分类。

### 4. 定义每个结果的高、中、低

直接写业务条件，不使用抽象分数或统一运行状态。

对每个结果分别回答：

- 哪些业务条件满足时可定义为高；
- 哪些边界、风险或不确定情况定义为中；
- 哪些明确错误或严重条件定义为低；
- 中、低分别要求用户检查什么。

高、中、低只提供统一语义，具体条件必须结合业务。

### 5. 定义整体组合原则

根据关键性和依赖关系定义：

- 哪些关键结果可以直接决定整体为低；
- 哪些关键结果为中时会限制整体最高等级；
- 上游风险如何影响下游结果；
- 哪些低影响问题只影响局部；
- 是否存在必须阻断的业务条件。

不要机械平均所有子结果。

### 6. 设计实现位置

针对每条可信条件，建议最合适的实现位置：

- 现有 SQL 或数据任务；
- 现有业务代码；
- 文件或文档处理流程；
- 权威业务 API；
- Agent 工作流节点；
- 规则引擎；
- 人工审核节点。

同时说明：

- 需要什么输入或来源；
- 判断逻辑应放在生成前、生成中还是生成后；
- 命中风险后如何影响流程；
- 需要向用户展示什么位置和核查动作。

不要默认新建独立置信度脚本或服务。

### 7. 检查设计完整性

主动查找：

- 没有拆分的复合结果；
- 没有等级定义的关键结果；
- 没有进入设计的重要历史问题；
- 高、中、低条件过于模糊；
- 关键错误可能被平均掩盖；
- 只有技术实现描述，没有业务验收标准；
- 只有泛化“人工检查”，没有具体位置和动作；
- 建议实现方式与现有系统重复或割裂；
- 新增输出没有同步可信设计；
- 需要业务负责人确认但尚未确认的条件。

### 8. 生成落地文件

默认生成一份：

```text
confidence-design.md
```

严格参考 [assets/confidence-design.template.md](assets/confidence-design.template.md)。

审查现有设计时，可以额外生成：

```text
confidence-design-review.md
```

参考 [assets/confidence-design-review.template.md](assets/confidence-design-review.template.md)。

### 9. 输出结论

最终答复按以下顺序输出：

1. 设计结论；
2. 业务背景与范围；
3. 结果单元和关键性；
4. 已知问题与风险；
5. 各结果的高、中、低条件；
6. 整体组合原则；
7. 实现位置和方式建议；
8. 定向人工审查策略；
9. 待确认问题；
10. 创建或修改的文件路径。

## 模式补充

### 新设计

从业务和结果拆分开始，不要先设计统一公式或技术框架。

### 现有设计审查

重点检查：

- 是否真正结合业务；
- 是否覆盖关键结果；
- 是否覆盖测试问题；
- 是否明确高、中、低；
- 是否能融入现有实现；
- 是否能形成具体人工审查动作。

### 问题沉淀

对每个新问题执行：

```text
问题复现
→ 触发条件
→ 影响结果
→ 严重程度
→ 等级影响
→ 实现建议
→ 审查动作
→ 回归测试建议
```

不能只把问题追加到问题列表。

### 变更影响分析

比较变更前后：

- 业务范围；
- 结果单元；
- 验收标准；
- 依赖关系；
- 已知问题；
- 高、中、低条件；
- 实现位置；
- 人工审查策略。

## 示例

需要参考 Excel 和 Word 场景时，读取 [references/examples.md](references/examples.md)。
