# 风险与问题分类

## 根因分类

- `implementation_error`：规则明确但代码实现错误；
- `rule_gap`：规则文档缺失、冲突或不清晰；
- `new_rule_candidate`：可能可泛化的新业务口径；
- `case_specific_info`：仅适用于当前案例；
- `external_system_field`：必须由外部系统或人工提供；
- `business_confirmation_needed`：证据不足，需要业务确认。

## 业务风险分类

- `mapping`：字段或实体映射；
- `source_traceability`：来源和证据链；
- `scope_applicability`：主体、时间、客户、用途或规则范围；
- `rule_match`：规则模板匹配和条件解析；
- `coverage`：数量、分支、边界和完整性；
- `calculation`：计算、公式和单位；
- `reconciliation`：跨文件或跨系统一致性；
- `unsupported_claim`：无依据事实或结论；
- `high_impact`：财务、法律、监管、处罚等高影响内容。

## 可泛化要求

进入长期可信规则前，应说明：

- 是否能从输入稳定识别；
- 是否在多个案例成立；
- 是否依赖当前项目人工信息；
- 是否已获得业务确认；
- 是否需要回归案例。
