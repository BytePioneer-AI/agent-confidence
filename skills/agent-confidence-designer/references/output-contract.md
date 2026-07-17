# 输出契约

## 设计包目录

```text
confidence-design/
├── confidence-contract.yaml
├── known-risk-patterns.yaml
├── validator-spec.yaml
├── confidence-review-report.md
├── validators/
└── tests/
```

## `confidence-contract.yaml`

必须包含：

- `schema_version`；
- `agent`：ID、名称、版本、负责人和描述；
- `supported_scope`：输入、输出、假设和排除项；
- `result_units`：结果、关键性、验收标准、依赖和验证器；
- `grading_policy`：高可信必要条件和降级规则。

每个结果单元必须定义 `maximum_level_when_unverified`，且不能为 `high`。

## `known-risk-patterns.yaml`

每个风险必须关联：

- 开发测试或用户自测来源；
- 影响结果；
- 检测器或人工门禁；
- 命中与未验证等级；
- 回归测试。

## `validator-spec.yaml`

每个验证器必须定义：

- 类型；
- 实现状态；
- 适用结果；
- 输入和逻辑；
- PASS 条件；
- FAIL 和不可用影响；
- 证据字段；
- 实现路径；
- 回归测试。

## 设计审查报告

必须包含：

1. 结论；
2. 业务与范围；
3. 结果单元覆盖；
4. 历史问题覆盖；
5. 验证器实施状态；
6. 高、中、低规则；
7. 阻断项；
8. 最小下一步；
9. 已接受风险。

## 高可信强制条件

`grading_policy.high_requires` 必须至少包含：

- `all_required_validators_pass`
- `no_critical_risk_detected`
- `within_supported_scope`
- `evidence_traceable`

## 强制降级条件

`grading_policy.downgrade_rules` 必须至少覆盖：

- `any_critical_validator_fail` -> `low`
- `required_validator_unavailable` -> `medium`
- `outside_supported_scope` -> `low`
