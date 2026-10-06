# 架构与运行模式

下图表示已核对的实验关系；学习笔记中的扩展设计不能代替已部署证据。地址为发布示例，需要映射实际环境。

~~~mermaid
flowchart TD
    B[浏览器或实验客户端] --> E[单台入口 HAProxy 与 Keepalived]
    E --> API[三个控制节点 Kubernetes API]
    E --> ING[Ingress]
    API --> W[两个 Worker]
    ING --> APP[Frontend / Gateway / User Service]
    APP --> EUR[Eureka 单副本]
    APP --> MYSQL[外部 MySQL 主库]
    MYSQL -. 异步复制：展示模式备库暂关 .-> REP[MySQL 备库]
    APP --> NFS[NFS 主服务]
    NFS -. 镜像push：展示模式暂停 .-> NB[NFS 备份机]
    FB[五节点 Fluent Bit] --> ES[单节点 Elasticsearch / NFS PVC]
    ES --> KB[Kibana Discover]
    MON[Prometheus / kube-state-metrics / Node Exporter] --> AM[Alertmanager]
    AM --> QQ[单一 QQ 收件人：私有配置]
~~~

| 主机 | 示例地址 | 角色 | 原配置 |
|---|---|---|---|
| k8s-master | 192.0.2.10 | 入口HAProxy/Keepalived，并非控制节点 | 2CPU/1GiB |
| k8s-master01/02/03 | 192.0.2.11/12/13 | 控制平面 | 3/2/2GiB |
| k8s-worker01/02 | 192.0.2.20/30 | 工作节点 | 各4GiB |
| mysql / mysql-slave | 192.0.2.40/41 | 主库/异步备库 | 各1GiB |
| nfs-server / nfs-rsync | 192.0.2.50/51 | NFS/镜像备端 | 各1GiB |
| VIP | 192.0.2.100 | 当前单入口持有 | 未验双机入口切换 |

上述VM配置合计约20GiB，宿主约16GiB可用RAM；配置总和不等同实时进程内存使用。

## 运行模式

2026-10-06最后记录：五K8s节点Ready；Eureka1，其他三个应用各2；ES1/Kibana1/Fluent Bit5，Prometheus1；User Service HPA当前2、范围2–3。

为保留EFK供查看，正常关闭MySQL备库与NFS备份VM，并暂停NFS源端镜像push。ES PVC依赖NFS主服务器，主数据库也承载应用，不能为了减负随意关闭这两台主服务。

恢复备节点需先核对MySQL binlog位置/保留及NFS两端差异，再恢复复制/镜像。rsync删除传播及在线ES目录的一致性风险保留；没有新增生产历史备份政策。
