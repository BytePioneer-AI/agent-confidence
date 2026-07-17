# 业务 Agent 可信等级实施指南

## 1. 实施目标

对每个业务 Agent 建立一个独立的可信设计包，作为业务实现、测试和运行时等级判断之间的契约。通用仓库提供模板和设计检查，业务团队负责编写真实校验逻辑。

## 2. 可信设计包

建议在业务 Agent 仓库中增加：

```text
confidence/
├── confidence-contract.yaml
├── known-risk-patterns.yaml
├── validator-spec.yaml
├── confidence-review-report.md
├── validators/
└── tests/
```

可使用脚手架生成：

```bash
python path/to/agent-confidence-designer/scripts/scaffold_confidence_package.py \
  --agent-id your-agent \
  --agent-name "Your Agent" \
  --output ./confidence
```

## 3. 文件职责

### `confidence-contract.yaml`

定义：

- Agent 版本和支持范围；
- 结果单元及其依赖；
- 关键性和验收标准；
- 必要与可选验证器；
- 高可信必要条件；
- 中、低等级降级规则。

### `known-risk-patterns.yaml`

记录开发测试和用户自测问题，包括：

- 问题来源；
- 触发条件；
- 影响结果；
- 检测方式；
- 命中和未验证时的等级影响；
- 回归测试。

### `validator-spec.yaml`

定义业务验证器的：

- 类型；
- 输入；
- 实现位置和状态；
- 检查逻辑；
- PASS 条件；
- FAIL 和不可用时的影响；
- 证据字段；
- 回归测试。

### `confidence-review-report.md`

记录设计评审：

- 已充分覆盖的关键结果；
- 缺少验证的结果；
- 未覆盖历史问题；
- 只能依赖语义或人工检查的内容；
- 发布前阻断项。

## 4. 业务验证器接口建议

业务验证器可以使用任意语言实现，但建议统一返回 JSON：

```json
{
  "validator_id": "validate-monthly-total",
  "validator_version": "1.0.0",
  "result_unit": "monthly_sales_total",
  "target": "sales_summary.xlsx#月度汇总!D42",
  "status": "PASS",
  "criticality": "critical",
  "risk_type": null,
  "message": "月度总额与明细独立复算一致",
  "evidence": [
    {"type": "file", "ref": "sales_detail.csv"},
    {"type": "cell", "ref": "sales_summary.xlsx#月度汇总!D42"}
  ],
  "review_action": null
}
```

验证器异常时不要吞掉错误，应返回 `ERROR`；不支持当前输入时返回 `UNSUPPORTED`。

## 5. 参考等级聚合

以下为原则性伪代码，业务团队应依据契约配置关键项：

```python
if any(critical_validator.status == "FAIL"):
    level = "low"
elif outside_supported_scope:
    level = "low"
elif any(required_validator.status in {"NOT_RUN", "UNSUPPORTED", "ERROR"}):
    level = "medium"
elif any(general_risk_detected):
    level = "medium"
elif all_required_validators_pass and evidence_traceable:
    level = "high"
else:
    level = "medium"
```

不要通过子结果分值平均产生整体等级。

## 6. 开发流程建议

1. 在 Agent 开发初期同步建立结果清单和验收标准；
2. 每发现一个测试问题，判断是否需要新增风险模式、验证器和回归测试；
3. 在业务代码中实现固定校验脚本；
4. 运行设计包校验；
5. 运行验证器测试和 Agent 端到端测试；
6. 由业务、开发和测试共同确认高可信条件；
7. 在发布流水线中阻止“关键结果无验证”或“重要问题无覆盖”的版本发布。

## 7. 设计包校验

```bash
python skills/agent-confidence-designer/scripts/validate_confidence_package.py \
  ./confidence --strict

python skills/agent-confidence-designer/scripts/check_issue_coverage.py \
  ./confidence
```

校验器报告错误时应阻断设计评审；警告表示存在成熟度缺口，是否阻断由团队决定。

## 8. 首批试点建议

选择两个差异明显的 Agent：

- 一个 Excel / 结构化数据 Agent，用于验证确定性检查和勾稽；
- 一个 Word / 分析报告 Agent，用于验证事实一致性、完整性和语义风险边界。

试点重点不是追求大量规则，而是验证：

- 高可信是否有充分、可重复的证据；
- 中低等级是否能精准定位人工核查点；
- 已知问题是否真正转成运行时检查和回归测试；
- 业务变更后契约是否可维护。
