# 关键排障案例

## 1. 控制节点心跳/客户端连接异常

现象：Master03/02等连接或状态异常，发布期间宿主余量很小。先核对可信SSH身份、kubelet/运行时/etcd、时间及API；不能仅看到节点NotReady就重建etcd。

操作：Master03单次kubelet恢复、Master02解除cordon/隔离调度验证；先按用户选择停EFK与Prometheus缩1减负，再做API /readyz、Worker02客户端和Master01连接恢复。Master01保留单节点DISABLE_HTTP2=true诊断drop-in，20分钟41次观察Ready且三类连接错误0。

结论：有限观察支持恢复，不证明HTTP2是所有故障根因。不能照搬此变量到所有节点或当永久兼容解决；后续EFK恢复是在关闭两个备VM的模式下完成。

## 2. HAProxy TCP端口通但API并未就绪

原后端只TCP探活，可能把未就绪API交给客户端。改为向各6443后端请求/readyz并要求HTTP200，使用既有公共CA验证TLS链，失败后关闭被标记down的会话。配置片段见configs/haproxy-api-backend.cfg.example。

这不是已验证的双机入口故障转移，也不表示某个节点永久健康。备份/校验/单次重启过程留在本地完整档案，公共片段不包含私钥。

## 3. 日志40条却只查到21条

按源端→Tail→过滤/元数据→ES→Kibana逐层核对：

1. Tag原有重复路径，改为kube.*，Kube_Tag_Prefix保留kube.var.log.containers.；新文件读头开启，DB保留。
2. 默认SA不能读Pod；只增get/list/watch pods/namespaces，禁止Secret读取与资源写入。
3. 噪声grep移到Merge前，命名空间grep使用Record Accessor；保留原kube-system排除。
4. 源端Worker01 max-size是100字节；实际stdout只有seq20。经用户维护确认，正常停止ES、仅改Docker日志10m/3并重启一次，逐Pod重建后确认新容器策略。旧容器不会自动继承新默认。
5. ES启动期间默认一次重试耗尽真实丢记录；最小改为持续重试，未增磁盘spool。最终正常链路40/40和Discover页面通过。

维护重建Eureka时因原无约束落Master01，随后只增原Worker01约束恢复；Ingress/Grafana按原策略移到Master01，最终无节点压力且入口检查通过。发布应用清单保留Eureka落点，不隐去副作用。

## 4. 数据服务的小范围恢复

MySQL先纠正采集解析，再识别旧binlog缺失；按用户指定主库快照重建备库、保全私有旧分支，验证CUD/拒写，不宣称自动故障转移。

NFS inotify逐事件sleep3600导致延迟；保留原权限/SELinux，仅改sleep2。错误换行版也保留，最终通过普通文件样本与独立实验包恢复；--delete依然传播删除。
