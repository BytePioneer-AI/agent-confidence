# Agent Confidence

面向业务 Agent + Skill 的可信等级设计最佳实践与通用设计 Skill。

本项目帮助开发人员针对一个具体业务回答：

- Agent 的产出应该拆成哪些可独立审查的结果；
- 开发测试和用户自测中发现的问题，哪些应进入可信等级定义；
- 每类结果在什么业务条件下属于高、中、低可信；
- 相关判断逻辑适合融入现有 SQL、脚本、业务服务、API 还是工作流；
- 用户最终只需要检查哪些高风险位置。

## 核心边界

本项目提供两类通用成果：

1. **最佳实践文档**：统一分析方法、术语、设计步骤和审查要点；
2. **`agent-confidence-designer` Skill**：把方法应用到具体业务，生成或审查业务专属的可信等级设计。

具体业务的可信判断逻辑不要求使用独立脚本，也不要求采用统一运行时协议。它可以直接融入已有的：

- SQL 或数据任务；
- Python、Java、JavaScript 等业务代码；
- 规则引擎；
- 内部或外部 API；
- Agent 工作流节点；
- 人工审核流程。

本项目不规定统一的 `PASS / FAIL / NOT_RUN` 状态，不提供通用置信度聚合器，也不假设所有业务都需要额外建设“验证器框架”。

## 仓库结构

```text
agent-confidence/
├── README.md
├── docs/
│   ├── agent-confidence-best-practices.md
│   ├── implementation-guide.md
│   └── research-conclusion.md
├── skills/
│   └── agent-confidence-designer/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── assets/
│       └── references/
└── examples/
    ├── excel-sales-report/confidence-design.md
    └── word-management-report/confidence-design.md
```

## 推荐使用方式

向 Skill 提供：

- 业务目标和下游用途；
- Agent / Skill 的输入、处理流程和输出；
- 业务验收标准；
- 开发测试中发现的问题；
- 用户自测或验收阶段确认的问题；
- 当前代码、SQL、API 或工作流结构；
- 已有的置信度设计（如有）。

Skill 默认输出一份 `confidence-design.md`，包括：

1. 业务背景与范围；
2. 结果单元及关键性；
3. 已知问题与风险映射；
4. 各结果的高、中、低条件；
5. 整体等级组合原则；
6. 判断逻辑的建议实现位置；
7. 定向人工审查策略；
8. 待业务确认的问题。

## 可信等级的通用语义

| 等级 | 通用解释 | 默认用户动作 |
|---|---|---|
| 高 | 在该业务已经定义的条件下，可直接使用或仅做少量抽查 | 不做全文检查 |
| 中 | 存在边界情况、依据不足或已知风险，需要检查指定结果 | 定向检查系统标记位置 |
| 低 | 命中明确错误条件、严重已知风险或关键业务条件不满足 | 必须人工确认或阻断 |

各业务必须自行定义什么条件对应高、中、低；置信度设计通用skill 不替业务负责人决定“什么是正确”。

## 示例

- [`examples/excel-sales-report/confidence-design.md`](examples/excel-sales-report/confidence-design.md)：销售数据合并、汇总与报告场景；
- [`examples/word-management-report/confidence-design.md`](examples/word-management-report/confidence-design.md)：经营分析 Word 报告场景。

两个示例只展示分析和设计方式，不代表真实业务可以直接照搬。
