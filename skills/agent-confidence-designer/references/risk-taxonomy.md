# 已知风险分类

使用下列分类统一整理开发测试与用户自测问题。一个问题可以属于多个分类，但应选择一个主分类。

| 分类 | 典型问题 | 优先验证方式 |
|---|---|---|
| `input_completeness` | 文件、页、工作表、字段或记录缺失 | 文件清单、Schema、数量守恒 |
| `input_format` | 日期、金额、编码、区域格式异常 | 类型和解析检查、标准化前后对比 |
| `mapping` | 字段、工作表、列或实体映射错误 | 映射表校验、样本对照、唯一性约束 |
| `omission` | 隐藏行、过滤行、附件或段落被漏处理 | 物理数量与处理数量对比 |
| `duplication` | 重复导入、重复记录、重复段落 | 主键、哈希、业务唯一性 |
| `calculation` | 公式、聚合、单位、币种或口径错误 | 独立复算、业务不变量 |
| `reconciliation` | 明细、汇总、跨表或跨系统不一致 | 双向勾稽、来源对比 |
| `source_traceability` | 数字、事实或结论没有明确来源 | 血缘、引用和证据链检查 |
| `requirement_coverage` | 漏掉用户要求、固定章节或输出项 | 需求清单和结构检查 |
| `execution_process` | 工具失败、步骤跳过、截断、重试后状态不明 | 运行轨迹和步骤完成检查 |
| `supported_scope` | 输入超出测试范围或使用未支持格式 | 支持范围判定与人工门禁 |
| `semantic_consistency` | 文档内部矛盾、摘要曲解原文 | 规则 + 受约束语义检查 |
| `unsupported_claim` | 没有证据的原因、趋势或因果结论 | 数据支持检查、人工复核 |
| `output_integrity` | 文件损坏、公式丢失、格式破坏 | 文件可打开性和结构检查 |

## 问题规则化要求

每个风险至少包含：

- `source`：`development_test` 或 `user_self_test`；
- `issue_reference`：缺陷或测试编号；
- `trigger_conditions`；
- `affected_result_units`；
- `severity`；
- `detectability`；
- `validator_id` 或 `manual_gate`；
- `on_detected`；
- `on_unverified`；
- `regression_tests`。

## 严重度建议

- `critical`：可能导致重大财务、法律、合规或外部承诺错误；
- `high`：影响核心结果、主要决策或大范围数据；
- `medium`：影响局部分析或可通过定向检查修复；
- `low`：低影响格式或非关键内容。

## 可检测性

- `deterministic`：可以由固定代码明确检测；
- `semantic_assist`：需要受约束的大模型或语义模型辅助；
- `manual`：暂时只能通过人工门禁确认。

不要把主观描述直接写成风险。先明确触发条件和可观察表现。
