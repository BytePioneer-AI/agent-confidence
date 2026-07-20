---
name: agent-confidence-designer
description: "Design, review, and maintain business-specific result-level high/medium/low confidence definitions for Agent, automation, document, and data workflows. Use when a developer provides business outputs, acceptance criteria, existing confidence rules, implementation code, or real test and user feedback and needs to identify true business result units, require non-rated result provenance chains, define review-oriented high/medium/low conditions, draft or review a confidence design, maintain approved `.agent-confidence/definition.md` and append-only `feedback.md`, or analyze implementation gaps. Do not use it to calculate confidence for a runtime result, grade inputs or intermediate process nodes, create file/task aggregate confidence, invent feedback, or modify runtime code without an explicit request."
---

# Agent Confidence Designer

帮助开发人员在开发和维护阶段设计业务结果的高、中、低可信等级。只对业务结果评级，并为每个结果提供不评级的结果溯源要求，使最终用户能够减少审查或只检查指定结果。

不要把本 Skill 当作运行时置信度计算器。运行时判断通常由 SQL、脚本、业务代码、API、规则或人工审核节点完成。

## 必读方法

先读取 [references/methodology.md](references/methodology.md)。

仅在以下情况下读取 [references/risk-taxonomy.md](references/risk-taxonomy.md)：

- 用户提供了真实测试问题或用户反馈；
- 需要检查高、中、低条件是否遗漏常见结果风险。

需要示例时先读取 [references/examples.md](references/examples.md)，再按当前场景选择完整示例：

- [Excel 销售汇总](references/examples/excel-sales-report.md)；
- [Word 经营报告](references/examples/word-management-report.md)。

## 工作模式

根据用户请求选择一种或多种模式：

1. **新设计**：分析业务并生成待确认的 `confidence-design.md`；
2. **现有定义审查**：审查已有设计或 `.agent-confidence/definition.md`，生成 `confidence-design-review.md` 或修改建议；
3. **反馈归档与建议**：仅在用户实际提供测试问题或反馈时，追加到 `.agent-confidence/feedback.md` 并提出规则变更建议；
4. **确认内容落地**：仅在用户明确认可设计或变更后，创建或更新 `.agent-confidence/definition.md`；
5. **实现差距分析**：比较已确认定义与现有 SQL、脚本、代码、API 或工作流，指出差距和建议实现位置。

不要因记录反馈或生成建议而自动修改当前生效定义。不要因完成设计而默认修改运行时代码。

## 强制边界

始终遵守：

- 只把业务明确要求输出、且用户可以独立接受、退回或修正的对象定义为结果单元；
- 不把输入、来源、候选记录、中间数据、日志或处理步骤仅因“可以检查”而定义为结果单元；
- 将完整 Excel、Word、报告或数据包视为结果承载容器，不定义文件或任务总体置信度；
- 不做结果等级平均、整体聚合或交付完整性校验；
- 为每个结果单元定义结果位置、至少一个来源位置，以及来源—结果形成关系；
- 不为结果溯源链、来源或处理节点定义高、中、低；
- 不记录或要求模型内部思维过程；
- 只对业务结果定义高、中、低，并使用业务验收条件，不使用模型主观自信或无校准百分比；
- 不把“模型生成”当作置信等级；
- 将业务影响作为可选维度，不强制另一套通用分级；
- 为中、低结果给出具体结果位置、来源位置和核查动作；
- 高可信关键结果仍可因既有业务控制或可选业务影响要求额外复核；
- 不猜测开发测试问题、用户自测问题或用户反馈；
- 不要求统一运行时状态枚举、验证器接口或独立置信度服务。



## 输入整理

优先读取：

- 业务目标、使用者和下游动作；
- 明确输入和明确输出；
- 业务验收标准、支持范围和不支持范围；
- 输出文件或数据结构，以及用户实际审查和修正的粒度；
- 来源数据和现有溯源方式；
- 现有 SQL、脚本、业务代码、API、规则和人工审核流程；
- 现有 `confidence-design.md` 或 `.agent-confidence/definition.md`；
- 用户实际提供的开发测试、用户自测或验收反馈。

可以读取处理过程来理解结果如何形成，但不要据此自动增加结果单元。材料不足时记录假设和待确认问题，不要补造业务规则或历史问题。

## 核心流程



### 1. 建立业务上下文

说明：

- 业务目标；
- 使用者和下游动作；
- 输入与输出；
- 业务验收标准；
- 支持范围和不支持范围；
- 用户如何接受、退回或修正结果。



### 2. 识别结果单元类型

从业务输出开始，为每类结果记录：

- 业务含义和示例；
- 在输出中的识别和定位方式；
- 用户独立接受、退回或修正的拆分边界；
- 业务验收标准；
- 可选的具体业务影响。

结果拆分遵循：

```text
来源更多 ≠ 结果单元更多
处理步骤更多 ≠ 结果单元更多
可独立处理的业务输出更多 = 结果单元更多
```

中间产物只有在其本身也是业务明确要求独立使用和验收的输出时，才转为结果单元。

### 3. 定义结果溯源要求

为每类结果单元定义：

- 结果位置如何定位；
- 必须记录哪些实际来源；
- 来源位置需要精确到什么粒度；
- 来源与结果之间是什么形成关系；
- 多来源结果如何关联全部实际来源；
- 用户如何从结果查看对应溯源信息。

形成关系可以是原样提取、字段映射、格式转换、公式计算、规则判断、相似问题匹配、多来源汇总或内容合并。不要强制固定的线性步骤。

### 4. 定义每类结果的高、中、低

直接写业务条件，不写抽象分数。

对每类结果分别回答：

- 哪些条件满足时可以直接使用；
- 哪些明确不确定点需要定向审查；
- 哪些明确错误或不可接受风险必须确认、修正或阻断；
- 结果溯源中的哪些事实会影响结果等级；
- 中、低分别要求用户检查哪个结果、哪些来源和什么条件。

统一语义：

- **高**：满足该业务定义的直接使用条件；
- **中**：未确认存在错误，但有明确的不确定点或边界条件，需要定向审查；
- **低**：已发现错误，或命中不可接受的重大风险，需要确认、修正或阻断。

具体条件始终由业务定义。

### 5. 处理可选业务影响

仅在不同结果出错后的影响明显不同，或业务需要区分重点审查对象时，记录具体错误后果。

不要默认创建业务影响等级。如果业务已有正式风险或影响分类，直接复用；否则可以只写具体后果，或完全不使用该维度。

业务影响不改变高、中、低，但可以独立影响审查优先级和强度。

### 6. 建议实现位置

把每条判断逻辑放在最容易取得准确事实、最适合判断它的位置，例如：

- SQL 或数据任务；
- 文件解析和生成脚本；
- 现有业务代码；
- 权威业务 API；
- 规则引擎；
- 工作流节点；
- 人工审核节点。

大模型可以辅助语义匹配、矛盾识别和依据充分性分析，但不能通过自我评价认证结果。

只提供设计和实现建议。只有用户明确要求修改实际代码时，才实施代码变更。

### 7. 检查设计完整性

检查：

- 每个结果单元是否都属于业务明确输出；
- 是否误把输入、中间数据或处理步骤作为结果；
- 结果粒度是否对应用户可独立处理的对象；
- 每个结果是否有位置、验收标准和结果溯源要求；
- 每条溯源是否包含来源位置和来源—结果形成关系；
- 是否误为来源或处理节点评级；
- 每类结果是否有具体高、中、低条件；
- 中、低是否有定向审查位置和动作；
- 是否错误定义文件或任务总体置信度；
- 是否使用模型主观自信或“模型生成”代替业务条件；
- 未确认建议是否与当前生效定义分离；
- 判断逻辑是否靠近业务事实。



## 文件管理



### 设计建议

新设计默认生成：

```text
confidence-design.md
```

使用 [assets/confidence-design.template.md](assets/confidence-design.template.md)。在文件顶部明确说明它是待确认建议，不是当前生效定义。

审查已有定义时可以生成：

```text
confidence-design-review.md
```

使用 [assets/confidence-design-review.template.md](assets/confidence-design-review.template.md)。

### 已确认定义

只在用户明确确认后，在业务项目根目录创建或更新：

```text
.agent-confidence/definition.md
```

使用 [assets/confidence-definition.template.md](assets/confidence-definition.template.md)。只写已确认内容；不写待确认建议、某次运行结果或代码实现状态。

### 真实反馈

只在用户提供真实测试问题或反馈时创建或追加：

```text
.agent-confidence/feedback.md
```

使用 [assets/confidence-feedback.template.md](assets/confidence-feedback.template.md)。保留原始描述，只追加分析、建议、用户决定和最终处理，不覆盖或删除历史记录。

没有真实反馈时，不创建反馈文件，也不生成占位问题。

收到反馈后：

```text
保留原始描述并归档
→ 分析可能影响的结果单元和置信度条件
→ 提出修改建议
→ 等待用户确认
→ 确认后更新 definition.md
```

反馈记录本身不能自动改变当前定义。

## 最终答复

最终说明：

1. 设计或审查结论；
2. 识别出的业务结果单元类型；
3. 结果溯源要求；
4. 各结果的高、中、低条件；
5. 可选业务影响；
6. 定向审查动作；
7. 实现位置建议或差距；
8. 待确认问题；
9. 创建或修改的文件路径；
10. 哪些建议尚未进入当前生效定义。

不要输出整体置信度、独立来源置信度或虚构的历史问题。
