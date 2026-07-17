---
name: agent-confidence-designer
description: "Guide developers to analyze and design business-specific high/medium/low confidence schemes for Agent + Skill workflows. Use when the user provides a business context, agent or skill implementation, output structure, acceptance criteria, development-test findings, user self-test findings, historical QA data, human final versions, or an existing confidence design and needs help decomposing results, defining what confidence means, identifying evidence and risks, designing hard rules and high/medium/low conditions, planning traceability and review actions, or deciding where the logic should fit into existing SQL, code, APIs, services, or workflows. Do not impose a universal validator interface, status protocol, aggregation engine, or standalone confidence service."
---

# Agent Confidence Designer

帮助开发人员针对具体业务 Agent + Skill，把可信等级想清楚、定义清楚，并给出适合融入现有系统的落地建议。

本 Skill 不建设统一运行时框架，不要求独立校验脚本、统一接口、固定状态、通用聚合器或独立服务。

## 工作模式

1. **新设计**：为新业务建立可信等级方案。
2. **现有设计审查**：检查结果拆分、可信含义、高中低条件和实施位置是否合理。
3. **问题沉淀**：将测试问题或人工终版差异转成可泛化的风险和规则候选。
4. **变更影响分析**：评估 Agent、Skill、输入输出、规则、数据源或业务阶段变化。

## 核心原则

- 使用高 / 中 / 低；没有历史校准时，不把内部规则分解释为概率。
- 先定义可信对象和可信含义，再讨论分数或实现。
- 不把文本相似、语言流畅或模型自信当作业务正确。
- 可信等级和业务影响分开；高可信高影响结果仍可要求责任部门确认。
- 集合型结果同时检查数量、必要维度、分支、边界、重复和缺失。
- 历史问题先归因、判断可泛化性并完成业务确认，再进入通用规则。
- 硬性规则优先于加权分。
- 结果必须尽量可追溯到具体来源、规则、主体、时间和审查位置。
- 优先建议复用现有 SQL、代码、API、规则引擎和工作流。

详细方法见 [references/methodology.md](references/methodology.md)。

## 输入整理

尽量读取：

- 业务目标、用户、下游动作和错误影响；
- Agent / Skill / 工作流 / 代码；
- 输入、输出、中间产物和业务阶段；
- 验收标准、支持范围和权威数据源；
- 开发测试、用户自测、人工修正版和部门终版；
- 已有标签、风险、规则和审查流程。

信息不足时记录假设和需确认项，不自行发明业务口径。

## 核心流程

### 1. 建立业务上下文

输出业务目标、范围、输入输出、处理阶段、下游动作、错误影响、责任部门和权威来源。

### 2. 拆分结果单元

为每个结果定义：

- ID、名称和位置；
- 结果形态：`scalar`、`field`、`record`、`text`、`collection`、`document` 或 `decision`；
- 所处业务阶段；
- 业务影响；
- 上游依赖；
- 人工审查对象。

不要只给整个文件一个等级。

### 3. 定义可信含义

每个结果必须说明：

- 评价的是什么；
- 高可信证明什么；
- 高可信不证明什么。

例如：字段映射高可信不等于源数据本身业务正确；规则解析高可信不等于测试数据已通过目标系统执行。

### 4. 结构化历史问题

将问题归类为：

- 脚本实现错误；
- 规则缺失或不清晰；
- 新业务规则候选；
- 个案人工信息；
- 外部系统字段；
- 待业务确认。

记录触发条件、影响结果、根因、证据、可泛化性、业务确认状态和建议动作。

### 5. 选择判断维度

根据业务选择，不强制统一权重：

- 规则匹配与条件解析；
- 主体、时间、客户和用途适用性；
- 来源权威性与多来源一致性；
- 单条结果正确性；
- 集合数量、分支和边界覆盖；
- 答案完整性；
- 来源追溯；
- 下游系统结果；
- 历史终版是否实质修改。

### 6. 定义硬性规则

识别不能被综合分掩盖的条件，例如主体不一致、高影响问题无责任部门证据、关键规则条件未解析、集合缺少核心场景。

### 7. 定义高 / 中 / 低

由业务结合上述维度和硬性规则确定：

- **高**：达到业务认可的充分条件，可按约定动作使用；
- **中**：有可参考依据，但需要定向复核；
- **低**：缺少直接依据、关键冲突或高风险推断，应留空、批注、阻断或交责任部门。

### 8. 设计证据链和审查动作

明确来源文件、行列、历史问题、原始值、采用值、适用主体、时间、规则、转换说明和检查位置。中、低结果必须给出最小审查动作。

### 9. 给出实施建议

为每项判断逻辑说明：

- 建议实现方式：SQL、现有代码、API、规则引擎、工作流或人工；
- 建议实现位置；
- 所需输入和证据；
- 是否需要业务确认；
- 是否适合加入回归测试或离线校准。

### 10. 生成设计文件

需要落地文件时运行：

```bash
python scripts/scaffold_confidence_package.py \
  --agent-id <agent-id> \
  --agent-name "<agent name>" \
  --output <target-directory>
```

填写：

- `confidence-contract.yaml`
- `known-risk-patterns.yaml`
- `confidence-logic.yaml`
- `confidence-review-report.md`

参考 [references/output-contract.md](references/output-contract.md)。

### 11. 静态校验

```bash
python scripts/validate_confidence_package.py <target-directory> --strict
```

该脚本只检查设计文件结构、引用和核心字段，不计算业务运行结果。

## 最终输出顺序

1. 结论和设计成熟度；
2. 业务上下文与阶段；
3. 结果单元和可信含义；
4. 历史问题与可泛化性；
5. 判断维度与硬性规则；
6. 高 / 中 / 低条件；
7. 证据链和人工审查；
8. 建议实现位置；
9. 需业务确认的问题；
10. 创建或修改的文件。

## 实际案例

需要案例时读取 [references/examples.md](references/examples.md)，对应：

- PBA SO 合同转换；
- ECS UAT 自动化；
- 供应商调查问卷整合。
