# 实测结果与证据定义

原始资料分三层：①XMind/方案里提到的知识与设计；②原部署自述及本次可证明的操作；③测试或验收支持的结果。这里仅列③；不能倒推独立贡献。

| 证据ID | 已有结果 | 测量条件 / 限制 |
|---|---|---|
| E01 | Java17项通过 | 注册/登录、本人历史、未判题保存；含预期4xx。没有执行Python |
| E02 | HPA2→3→2 | 09:46:08扩3、09:48:25缩2；CPU request500m、目标20%、min2/max3 |
| E03 | 6485成功/0错误/P95 15.384ms | 8线程，90秒计划，逐线程0.1秒暂停，固定GET题目列表；含末次状态读取约91.552秒 |
| E04 | MySQL5表26行一致 | 修复已有缺失binlog通道；CUD传播和从库误写1290拒绝。当前备库暂关 |
| E05 | NFS4文件约1MiB镜像/独立恢复 | 样本内容/mode/uid/gid匹配及删除传播；无生产历史版本/ES一致性快照保证 |
| E06 | EFK正常R5源40/ES40 | 两Worker各20、seq1–20、40个唯一worker/seq、中文、元数据均匹配；INFO14/WARN14/ERROR12 |
| E07 | 实际过滤4→2 | 保留正常JSON/纯文本，排除原噪声与kube-system；仅检索自有生成器Pod |
| E08 | Kibana代理查询40条及用户Discover截图 | 页面标记与16:00–17:00、40 hits、Worker01样本中文/元数据清楚；截图不代替E06逐条核对 |
| E09 | 告警12条48断言，4路由断言 | 原生promtool离线模拟；实际12规则health=ok，3AM加载路由，30既有规则收件扩展 |
| E10 | 内部模拟pending→firing→清除 | 独立临时规则、空接收器，收到后表达式改假、确认两端无活跃告警并删除；没有追加合成邮件 |
| E11 | QQ测试实际收件 | 旧阶段首轮抑制0次尝试；用户明确追加后1次尝试/0失败/完成样本1，用户确认收件 |
| E12 | 维护后5个读检查通过 | 登录、本人信息、题目列表/详情、本人历史；没有重新执行全部17项或压测 |

源文件对应与SHA映射保存在本人本地求职档案；公共仓库仅提供[去敏摘要](../results/summary.json)，不带Windows路径、私有备份或完整原始业务记录。原始源码/脚本与新增公共工具的关系见[归属](attribution.md)。

## 失败也属于结果

- MySQL“无通道”曾因TSV误解析，后撤回并真实修复旧通道，不掩盖采集错误。
- NFS首轮sleep3600阻塞，初次改动换行错误，补正后第三轮才确认sleep2版本。
- EFK R1=13/40、R2/R3=21/40；Worker01源日志100字节轮转，只留最后一条；修复前不能宣称完整。
- ES维护启动期R4=20/40，默认一次重试耗尽造成真实丢弃/告警。Retry_Limit False后正常R5=40/40；不代表丢失历史补回或跨故障无损。
- 过滤初查命中采集器自己的文件名日志，补加生成器Pod条件后才确认4→2。

event_time在R5等待执行的state生成时写入，早于实际打印；不能把它与@timestamp的差当采集延迟。各统计不能推算99.9%、最大QPS、RPO0或固定RTO/MTTD/MTTI。

## 公共工具如何使用

scripts/diagnostics/cluster-status.sh是只读入口；scripts/validation/efk-sample.py是由已有实验方法整理的通用小样本工具，**新公共版本未在服务器执行**。用已有合法缓存镜像运行；create/check/cleanup分开，状态在被忽略的runs/目录。

~~~bash
python3 scripts/validation/efk-sample.py create --image YOUR_CACHED_SHELL_IMAGE --nodes k8s-worker01 k8s-worker02 --state runs/efk.json
python3 scripts/validation/efk-sample.py check --state runs/efk.json
# 确认namespace仍只含本工具Pod后清理；ES标记测试记录保留。
python3 scripts/validation/efk-sample.py cleanup --state runs/efk.json
~~~

离线告警用例来自实际通过的48断言，不发邮件、不改集群：

~~~bash
cd validation/alerts
promtool check rules rules.json
promtool test rules tests.json
~~~

本次整理没有重新跑这些实验或部署发布模板。
