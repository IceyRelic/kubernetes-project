# 配置示例的用途

- haproxy-api-backend.cfg.example：已验API后端片段，合并原完整HAProxy配置，公共CA须自己提供。
- fluent-bit/：与最终EFK ConfigMap一致，中文注释说明Tag/读头/过滤/重试。
- alertmanager-route-fragment.yaml.example：只含新增路由/空接收器。不是完整Alertmanager配置，邮件账户仅私有保存。
- docker-log-options.json.example：只展示修改字段，不直接覆盖完整daemon.json。先停单副本数据服务，维护窗口单次重启，再逐Pod重建/检查；已有容器不自动更新。
- mysql-replica.cnf.example：只读目标，不包含原复制账户/TLS/位置。恢复前保全旧分支，确认权威快照，不提供自动覆盖数据库脚本。

NFS同步沿用原inotify/rsync，最终仅把逐事件sleep3600改为2秒。原脚本含rsync认证/路径细节，公共包仅在排障文档说明修改；不复制私有脚本/认证，也不另造未经验证的备份实现。
