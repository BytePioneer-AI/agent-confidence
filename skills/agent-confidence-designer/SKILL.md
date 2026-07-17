---
name: agent-confidence-designer
description: "Design, review, and update business-specific high/medium/low confidence grading schemes for Agent + Skill workflows. Use when a developer provides an agent business context, implementation, output structure, acceptance criteria, development-test issues, user self-test issues, or an existing confidence design and needs to decompose results, convert known issues into risk patterns, specify deterministic validators, define grading and aggregation rules, identify validation gaps, generate confidence-contract/known-risk-patterns/validator-spec files, scaffold business validator code and regression tests, or assess confidence-design impact after an agent or skill change. Do not use it to let an LLM self-score a runtime result or to replace business-specific validation code."
---

# Agent Confidence Designer

将通用方法应用到具体业务，生成并审查业务专属的可信等级设计。把“开发测试和用户自测中发现的问题”转化为风险模式、验证器、回归测试和高/中/低等级规则。

不要把本 Skill 当作运行时万能置信度计算器。要求业务团队实现具体固定校验脚本；本 Skill 只负责设计、脚手架和设计审查。

## 工作模式

先判断任务属于哪种模式：

1. **新设计**：为新 Agent + Skill 建立可信等级方案。
2. **现有设计审查**：检查已有契约、规则和验证器是否完整、自洽、可执行。
3. **问题沉淀**：把新增开发测试或用户自测问题转成风险模式、验证器和回归测试。
4. **变更影响分析**：评估 Agent、Skill、输入输出、数据源或业务规则变更对可信设计的影响。

可以组合多种模式，但始终按下面的核心流程执行。

## 核心原则

始终遵守：

- 使用高 / 中 / 低，不输出没有校准依据的百分比。
- 把“可信等级”定义为验证证据是否充分，而不是模型主观自信。
- 让历史问题决定检查项，让当前验证结果决定本次等级。
- 优先设计确定性脚本；仅把难以脚本化的语义问题交给受约束的大模型检查。
- 不允许大模型“未发现问题”单独支持高可信。
- 不把 `NOT_RUN`、`UNSUPPORTED` 或 `ERROR` 当作通过。
- 不通过平均分掩盖关键子结果失败。
- 要求高可信具备正向证据、来源追溯和支持范围证明。
- 将风险定位到字段、记录、单元格、段落、指标、决策步或文件结构。
- 为每个中、低结果给出最小人工核查动作。

详细方法见 [references/methodology.md](references/methodology.md)。

## 输入整理

尽量读取以下材料；缺失时明确记录假设和设计缺口，不要凭空补全业务规则：

- 业务目标、用户、下游动作和错误影响；
- Agent 提示词、Skill、工作流、脚本和工具调用；
- 输入、输出、中间产物和 Schema；
- 业务验收标准与支持范围；
- 开发单测、集成测试、回归测试问题；
- 用户自测和验收阶段确认的问题；
- 已有可信等级配置、校验器和测试。

不要把实时、零散、无法复现的主观反馈直接当作置信信号。先把问题归纳成可描述的触发条件、错误表现和影响对象。

## 核心流程

### 1. 建立业务上下文

输出：

- 业务目标；
- 输入、输出和中间产物；
- 支持范围与不支持范围；
- 下游动作；
- 错误影响；
- 当前假设和信息缺口。

### 2. 拆分结果单元

为每个可独立验收的结果定义：

- 唯一 ID；
- 描述与位置；
- 关键性：`critical`、`high`、`medium`、`low`；
- 验收标准；
- 上游依赖；
- 必要验证器；
- 未验证时允许的最高等级。

不要只为整个文件定义一个等级。优先拆到能够产生定向核查动作的粒度。

### 3. 结构化已知问题

将每个开发测试或用户自测问题转成：

- 来源与问题编号；
- 触发条件；
- 影响结果单元；
- 严重度；
- 可检测性；
- 检测器或人工门禁；
- 命中时等级；
- 无法验证时等级；
- 回归测试。

使用 [references/risk-taxonomy.md](references/risk-taxonomy.md) 分类风险。

### 4. 设计验证器

按优先级设计：

1. 业务不变量和独立复算；
2. 数据完整性、Schema 和来源追溯；
3. 跨文件或跨系统一致性；
4. 已知缺陷模式检测；
5. 语义辅助检查；
6. 人工门禁。

为每个验证器明确：输入、逻辑、PASS 条件、FAIL 影响、不可用影响、证据、实现状态和回归测试。使用 [references/validator-design-guide.md](references/validator-design-guide.md)。

### 5. 定义等级规则

至少满足：

- 任一关键验证器 `FAIL` -> 对应关键结果为低；
- 必要验证器 `NOT_RUN` / `UNSUPPORTED` / `ERROR` -> 结果不能为高；
- 超出明确支持范围 -> 默认低，除非业务契约规定人工门禁路径；
- 所有必要验证通过、没有关键风险、来源可追溯、输入在支持范围内 -> 才允许高；
- 证据不足但未发现明确关键错误 -> 中；
- 关键上游结果降级 -> 下游结果同步限制最高等级。

### 6. 检查设计覆盖

主动查找：

- 没有验证器的关键结果；
- 只有语义验证器的关键结果；
- 未绑定检测器或人工门禁的严重风险；
- 没有回归测试的历史问题；
- 把运行成功当作业务正确的规则；
- 把未验证默认成通过的路径；
- 通过平均分掩盖关键失败的聚合；
- 新增输出没有同步可信设计；
- 只能输出泛化“请人工检查”而无法定位的风险。

### 7. 生成落地文件

需要创建文件时，先运行：

```bash
python scripts/scaffold_confidence_package.py \
  --agent-id <agent-id> \
  --agent-name "<agent name>" \
  --output <target-directory>
```

随后填写：

- `confidence-contract.yaml`
- `known-risk-patterns.yaml`
- `validator-spec.yaml`
- `confidence-review-report.md`
- `validators/` 中的业务脚本骨架
- `tests/` 中的回归测试要求

严格遵循 [references/output-contract.md](references/output-contract.md)。

### 8. 运行设计校验

完成配置后运行：

```bash
python scripts/validate_confidence_package.py <target-directory> --strict
python scripts/check_issue_coverage.py <target-directory>
```

修复所有错误。把警告分为发布阻断项、后续改进项和明确接受的风险。

### 9. 输出审查结论

最终答复按以下顺序输出：

1. **结论**：设计成熟度与是否具备上线条件；
2. **业务与结果清单**：结果单元、关键性、依赖；
3. **可信等级规则**：高、中、低和聚合规则；
4. **历史问题覆盖**：已覆盖、未覆盖、需人工门禁；
5. **验证器实施清单**：已实现、待实现、无法自动化；
6. **阻断问题**：会错误标高或漏掉关键风险的问题；
7. **最小下一步**：具体脚本、测试或业务确认动作；
8. **生成文件**：列出创建或修改的路径。

## 模式补充

### 新设计

从结果拆分开始，不要先写综合等级公式。先定义正确性和必要证据，再设计等级。

### 现有设计审查

保留原设计意图，同时明确：

- 哪些规则有确定性证据；
- 哪些规则只是模型判断；
- 哪些关键结果存在验证空白；
- 哪些高可信路径不成立；
- 需要修改的具体配置和代码。

### 问题沉淀

对每个新问题执行：

```text
问题复现
-> 根因和触发条件
-> 影响结果
-> 检测方式
-> 等级影响
-> 回归测试
-> 更新契约和验证器
```

不能只把问题追加到文档列表。

### 变更影响分析

比较变更前后：

- 结果单元；
- 依赖关系；
- 支持范围；
- 验收标准；
- 风险模式；
- 验证器输入与实现；
- 高可信充分条件。

把新增但未验证的关键结果标记为发布阻断项。

## 业务脚本边界

可以生成业务校验脚本骨架和测试骨架，但不要声称已经实现业务正确性检查，除非已经获得真实数据结构、业务规则并实际运行测试。

不把通用脚本写成万能业务判断器。通用脚本只负责：

- 生成设计包；
- 校验配置结构和交叉引用；
- 检查历史问题覆盖；
- 暴露关键设计缺口。

具体的数据勾稽、公式复算、字段映射和文档内容核对必须在业务仓库中实现。

## 示例

需要参考 Excel 和 Word 场景时，读取 [references/examples.md](references/examples.md)。
