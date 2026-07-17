# 设计文件约定

## 目录

```text
confidence-design/
├── confidence-contract.yaml
├── known-risk-patterns.yaml
├── confidence-logic.yaml
└── confidence-review-report.md
```

## `confidence-contract.yaml`

必须包含：

- `schema_version`；
- `agent`；
- `business_context`；
- `result_units`；
- 每个结果的 `confidence_meaning`、`high_conditions`、`medium_conditions`、`low_conditions` 和 `review_policy`。

## `known-risk-patterns.yaml`

每个风险必须包含来源、触发条件、影响结果、根因分类、可泛化性、业务确认状态和建议动作。

## `confidence-logic.yaml`

每项逻辑必须包含适用结果、判断维度、硬性规则、证据要求、建议实现方式和建议实现位置。

## 审查报告

必须说明设计成熟度、关键结果、主要风险、需业务确认事项、实施落点和下一步。
