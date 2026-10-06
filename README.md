# kubernetes-project

微服务部署与 Kubernetes 集群资源监控实训：以 Spring Cloud 应用为载体，展示容器化交付、集群排障、HPA、外部 MySQL/NFS，以及 Prometheus/Alertmanager 和 EFK 日志链路。

## 先看什么

- [架构与运行模式](docs/architecture.md)
- [环境准备与部署顺序](docs/deployment.md)
- [实测结果与证据定义](docs/validation.md)
- [关键排障案例](docs/troubleshooting.md)
- [功能与可靠性边界](docs/limitations.md)
- [资料来源和贡献归属](docs/attribution.md)

## 已验证结果

| 范围 | 2026-10-05/06 实验结果 | 使用边界 |
|---|---|---|
| 集群与应用 | 3 控制平面＋2 Worker；17 项核心功能/权限用例通过 | 包含预期401/403/400；不是17个接口都返回200 |
| HPA | User Service 实际2→3→2，曾3/3就绪 | min2/max3，CPU20%是实验阈值 |
| 固定只读请求 | 8线程、90秒计划、6485成功/0错误、P95 15.384ms | 每线程0.1秒暂停；不是容量上限或生产SLA |
| MySQL | 修复既有异步复制；5表26行一致，CUD传播及从库拒写通过 | 无自动故障转移；当前备库为EFK展示暂关 |
| NFS | 4文件约1MiB的变更镜像与独立实验包恢复通过 | 删除会传播；不是生产历史备份或ES一致性恢复 |
| EFK | 正常链路40/40日志，两Worker各20，中文/序号/元数据正确；过滤4→2；Discover截图支持40 hits | 维护期曾丢日志；无持久spool，ES为单节点 |
| 告警 | 后续新增12条，48项离线断言；扩展30条既有规则的收件路由；实际总数147 | 大多数真实故障未注入；内部合成验证走空接收器 |

结果是实训环境的特定时间样本，保留失败轮次与修复过程。详细定义及去敏摘要见 [validation](docs/validation.md) 和 [results](results/summary.json)。

## 目录

- manifests/：四应用Deployment/Service/Ingress、HPA、EFK、应用与EFK告警、ES PVC。
- configs/：HAProxy API后端、Fluent Bit最终配置、Alertmanager路由片段、Docker/MySQL示例。
- examples/：仅含待填写占位值的凭据示例。
- scripts/：只读诊断与小范围EFK样本生成/核对/清理。
- validation/alerts/：promtool的12条规则及48项模拟检查输入。
- results/：少量去敏统计，排除原始业务日志/数据库。

## 准备环境

本次原实验为Kubernetes v1.18.0、Docker18.6.3、CentOS7、ES/Kibana7.10.2、Fluent Bit1.9.10。发布模板保留旧API（如HPA v2beta2），没有假称完成现代版本迁移。

这是已有集群上的配置与复盘包；原业务Java/Vue应用来自培训机构，公开许可未确认，所以本仓库不提供源码、JAR、dist、镜像或业务初始化数据。使用者需自行合法准备工件及兼容环境。

应用镜像使用 example.invalid/your-project/... 占位名称、imagePullPolicy=Never；替换为自备并已加载的镜像。地址192.0.2.*与practice.example.test均为发布示例，替换后再应用。

## 当前展示模式（2026-10-06记录）

EFK运行、Prometheus一副本；MySQL备库和NFS备份机暂关，NFS镜像push暂停，主库/NFS服务保留。此模式不代表实时主从/镜像持续正常。[模式与恢复步骤](docs/architecture.md#运行模式)。

## 归属

个人原工作自述为容器化、ACR发布和YAML部署；2026年10月的排障、应用修复与验收有Codex辅助。二者分别记录，不以新实验倒写历史个人成果。本发布模板由最终对象重建并去敏，未重新部署、未在全新集群验证。

机构业务工件不在本仓库；暂无整仓许可证授予，不能从本仓库推定第三方应用的再分发许可。
