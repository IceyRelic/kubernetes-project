# 来源与贡献归属

## 三类材料

1. 学习/设计：原XMind与培训材料描述技术方案，不自动构成熟练度/部署结果。
2. 操作：个人确认原容器化、ACR与YAML部署；后续2026-10-05/06修复、验证和本公共包整理有Codex协助，明确区别。
3. 验收：只使用已有功能/HPA/固定请求/MySQL/NFS/EFK/告警证据支持的有限结论，具体见validation。

## 第三方业务应用

Java/Vue源码与初始业务资料来自培训机构，公开许可未确认。本仓库不上传完整源码、源码diff、JAR、dist、数据库初始化/业务dump或应用镜像；私有仓库也不被自动视为获再分发授权。

平台清单由已部署对象选取、去敏和重建；通用诊断/样本脚本为本次新整理版本，未运行到实验服务器，不假称与历史已验脚本逐字相同。修改点与私有源路径/原件SHA仅留本地筛选台账。

Kubernetes、Prometheus、Fluent Bit、Elastic、HAProxy等组件的镜像/发行版及许可证由各原项目管理；本仓库不替第三方授权。尚未添加整仓LICENSE，后续需确定自己可授权范围。

## 公共参考

- https://kubernetes.io/docs/concepts/configuration/secret/
- https://docs.docker.com/engine/logging/configure/
- https://docs.fluentbit.io/manual/1.9/administration/scheduling-and-retries
- https://docs.fluentbit.io/manual/1.9/pipeline/filters/kubernetes
- https://docs.fluentbit.io/manual/1.9/pipeline/filters/grep
- https://www.elastic.co/guide/en/kibana/7.10/saved-objects-api-create.html
- https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/

链接是技术依据，不代表业务源码许可已经取得。私人联系人/服务器密钥/业务记录不进入仓库；原桌面截图含无关标签，仅本地保存，公共版需要另准备去敏展示。
