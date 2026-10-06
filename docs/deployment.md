# 环境准备与部署顺序

## 本包的定位

配置来自2026-10-06实验最终对象，发布时做了去敏与参数化。已有集群里的实测结果在validation中；本包未重新部署，不宣称从零一键安装通过。不要直接对已有项目整目录apply。

## 前置条件

1. 自备与旧版本API兼容的Kubernetes环境，以及相应CNI/DNS/Ingress Controller。
2. 已有Prometheus Operator CRD及monitoring namespace、Prometheus、Alertmanager、KSM/Node Exporter。此仓库不复制整个第三方监控发行版。
3. 自备合法Spring Cloud/Vue工件和可运行镜像，或已有缓存镜像；必须自行核对接口契约。机构应用不随仓库再分发。
4. 外部MySQL user_db及符合应用的合法初始化资料、NFS服务；已有nfs-subdir-external-provisioner和名为nfs-storage的StorageClass，或替换ES PVC的StorageClass。
5. 替换全部192.0.2.*地址、practice.example.test域名、应用镜像占位、匹配nodeSelector的节点名；EFK缓存镜像/tag也需合法来源。Blackbox模板保留Never策略，先准备缓存。
6. 阅读资源requests/limits与架构运行模式；完整组件不能假定在16GiB宿主无压力。

ES/Kibana使用node-role=log选择器，目标Worker需保留该标签。Prometheus Operator必须提供本清单使用的PrometheusRule/ServiceMonitor/Probe CRD，且规则/Monitor选择器包含这些对象；有CRD不等于一定会被抓取。

## 配置顺序（手工审阅后执行）

~~~bash
# 当前context必须是你自己的隔离实验集群。
kubectl config current-context
kubectl apply -f manifests/namespaces.yaml
# 在自己的目标Worker执行，下面是原实验节点名示例。
kubectl label node k8s-worker01 k8s-worker02 node-role=log --overwrite
~~~

先准备本地私有Secret与应用镜像；examples/application-credentials.yaml.example只有占位值，不直接apply。两个MySQL字段通过application-credentials Secret引用，机构工件内部JWT等配置仍需自行检查。本次把原环境中的MYSQL明文env改为Secret引用是发布模板转换，未重新部署验证。

NFS动态供给器就绪后创建es-data-pvc，再依次审阅应用、日志和指标对象：

~~~bash
kubectl apply -f manifests/storage/es-data-pvc.yaml
kubectl apply -f manifests/apps/applications.yaml
kubectl apply -f manifests/logging/efk.yaml
kubectl apply -f manifests/monitoring/efk-observability.yaml
kubectl apply -f manifests/monitoring/application-alert.yaml
~~~

efk-observability同时包含内部Fluent Bit指标、黑盒探针及12条规则。ES/Kibana原配置主要是单副本示例，ES Pod Ready可能早于HTTP启动；实际核对/_cluster/health和Kibana/api/status后才做日志验证。

使用Prometheus Operator管理副本；若选择本实验单副本模式，改Prometheus CR的spec.replicas，不能直接缩受控StatefulSet后声称持久生效。

Alertmanager路由片段不是完整配置：先保留/准备私有qq-lab-core邮件接收器，再合并路由并amtool校验。examples/alertmanager-email.yaml.example不可直接投入通知。内部合成验证使用空接收器，不自动发邮件。

确认Metrics API和CPU request=500m，再应用实验HPA：

~~~bash
kubectl apply -f manifests/autoscaling/user-service-lab.yaml
kubectl get hpa -n spring-cloud
~~~

HPA 20%只是小资源实验参数；不默认重新执行压测。本实验阶段09/10的负载与工作集不能归因为固定性能改善。

## 合法工件与镜像

不提供机构业务Dockerfile/源码diff/JAR/dist。可使用自己的镜像构建流程，命名为清单中的合法缓存镜像标签，或改为自己的registry并配置PullPolicy/私有拉取Secret。本轮历史新镜像仅缓存两个Worker，没有本轮推送ACR/CI/CD证据。

## 文件转换

移除uid/resourceVersion/managedFields/status/last-applied与生成注解；Service集群IP由目标集群分配；私人ACR/联系人/Windows路径未进入发布文件；保留实际API版本/探针/资源/HPA阈值/只读RBAC。原始地址和源文件逐项映射只保留在本地发布来源台账。
