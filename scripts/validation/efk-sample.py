#!/usr/bin/env python3
"""小范围EFK样本：create/check/cleanup分开；只处理带本轮标签的对象，不发通知、不删ES索引。

依赖Python3标准库和已配置的kubectl。由历史已验方法整理，公共版本未执行到原服务器。
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import uuid


def require(condition):
    """前置条件在python -O下也生效；失败即停止，避免错删资源或误报通过。"""
    if not condition:
        raise ValueError("样本状态、资源归属或完整性条件不满足，已停止。")


def kubectl(args, data=None):
    """参数列表避免shell插值；只提交自有清单或带本轮标记的查询。"""
    result = subprocess.run(["kubectl", "--request-timeout=15s"] + args,
                            input=json.dumps(data, ensure_ascii=False).encode() if data is not None else None,
                            capture_output=True, timeout=40)
    if result.returncode:
        raise RuntimeError("kubectl失败；请核对context/服务状态，不要盲目重跑create。")
    return result.stdout.decode("utf-8")


def load_state(path):
    """只接受本工具产生的命名空间和UUID；不把外部state当作任意删除授权。"""
    state = json.loads(path.read_text(encoding="utf-8"))
    require(re.fullmatch(r"[0-9a-f]{32}", state["run_id"]))
    require(state["namespace"] == "efk-public-" + state["run_id"][:12])
    require(isinstance(state["pods"], list) and len(state["pods"]) == 2)
    require(all(p["name"] == "sample-" + str(i) for i, p in enumerate(state["pods"])))
    return state


def create(args):
    """保存独占state再创建对象；如中断，按state检查/清理，不能覆盖原state。"""
    require(len(set(args.nodes)) == 2)
    require(all(re.fullmatch(r"[a-z0-9][a-z0-9.-]*", node) for node in args.nodes))
    require(re.fullmatch(r"[A-Za-z0-9./:_@-]+", args.image))
    run_id = uuid.uuid4().hex
    ns = "efk-public-" + run_id[:12]
    labels = {"project": "public-efk-validation", "validation-run": run_id}
    state = {"run_id": run_id, "namespace": ns,
             "pods": [{"name": "sample-" + str(i), "node": node} for i, node in enumerate(args.nodes)]}
    args.state.parent.mkdir(parents=True, exist_ok=True)
    with args.state.open("x", encoding="utf-8") as stream:
        json.dump(state, stream, ensure_ascii=False, indent=2)
    namespace = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns, "labels": labels}}
    made = json.loads(kubectl(["create", "-f", "-", "-o", "json"], namespace))
    state["namespace_uid"] = made["metadata"]["uid"]
    args.state.write_text(json.dumps(state, indent=2), encoding="utf-8")
    for pod in state["pods"]:
        # 打印20条已知JSON，镜像只运行shell，不启动原Java程序。
        lines = [json.dumps({"validation_id": run_id, "worker_source": pod["node"], "seq": seq,
                            "level": ("INFO", "WARN", "ERROR")[(seq - 1) % 3],
                            "message": "EFK public controlled test 中文日志"}, ensure_ascii=True)
                 for seq in range(1, 21)]
        command = "\n".join("printf '%s\\n' '" + line + "'" for line in lines) + "\nsleep 120"
        manifest = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": pod["name"], "namespace": ns, "labels": labels},
                    "spec": {"restartPolicy": "Never", "automountServiceAccountToken": False,
                             "nodeSelector": {"kubernetes.io/hostname": pod["node"]},
                             "containers": [{"name": "producer", "image": args.image, "imagePullPolicy": "Never",
                                             "command": ["/bin/sh", "-c", command],
                                             "resources": {"requests": {"cpu": "10m", "memory": "16Mi"},
                                                           "limits": {"cpu": "100m", "memory": "64Mi"}}}]}}
        kubectl(["create", "-f", "-"], manifest)
    print(json.dumps({"created_namespace": ns, "state": str(args.state), "expected_logs": 40,
                      "note": "先等待采集；check不完整时仅重试只读check，不重跑create。"}, ensure_ascii=False))


def check(args):
    """同时检查源stdout和ES中每节点序号；仅计总数会漏掉重复或源端丢失。"""
    state = load_state(args.state)
    for pod in state["pods"]:
        raw = kubectl(["-n", state["namespace"], "logs", pod["name"]])
        rows = [json.loads(line) for line in raw.splitlines() if line]
        require(len(rows) == 20 and [r["seq"] for r in rows] == list(range(1, 21)))
        require(all(r["validation_id"] == state["run_id"] for r in rows))
    query = {"size": 100, "query": {"term": {"validation_id.keyword": state["run_id"]}},
             "_source": ["validation_id", "seq", "level", "message", "worker_source",
                         "kubernetes.namespace_name", "kubernetes.pod_name", "kubernetes.container_name"]}
    raw = kubectl(["-n", "logging", "exec", "-i", "elasticsearch-0", "-c", "elasticsearch", "--",
                   "curl", "-fsS", "--max-time", "10", "-H", "Content-Type: application/json", "-X", "POST",
                   "http://127.0.0.1:9200/logstash-*/_search", "--data-binary", "@-"], query)
    hits = [item["_source"] for item in json.loads(raw)["hits"]["hits"]]
    require(len(hits) == 40 and len({(h["worker_source"], h["seq"]) for h in hits}) == 40)
    for pod in state["pods"]:
        require({h["seq"] for h in hits if h["worker_source"] == pod["node"]} == set(range(1, 21)))
    require(all(h["message"] == "EFK public controlled test 中文日志" and
                h["kubernetes"]["namespace_name"] == state["namespace"] and
                h["kubernetes"]["container_name"] == "producer" for h in hits))
    print(json.dumps({"marker": state["run_id"], "source": 40, "es": 40, "unique_pairs": 40,
                      "metadata_and_chinese_ok": True, "scope": "正常小样本，不代表高吞吐/故障无损"}, ensure_ascii=False))


def cleanup(args):
    """检查namespace标签、UID和全部Pod归属，再用UID前置条件删除；ES记录不删除。"""
    state = load_state(args.state)
    ns = json.loads(kubectl(["get", "namespace", state["namespace"], "-o", "json"]))
    require(ns["metadata"]["labels"]["validation-run"] == state["run_id"])
    require(ns["metadata"]["uid"] == state["namespace_uid"])
    pods = json.loads(kubectl(["-n", state["namespace"], "get", "pods", "-o", "json"]))["items"]
    require(all(p["metadata"].get("labels", {}).get("validation-run") == state["run_id"] for p in pods))
    options = {"apiVersion": "v1", "kind": "DeleteOptions", "preconditions": {"uid": state["namespace_uid"]}}
    kubectl(["delete", "--raw", "/api/v1/namespaces/" + state["namespace"], "-f", "-"], options)
    print(json.dumps({"owned_namespace_deleted": state["namespace"], "es_records_kept": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("create", "check", "cleanup"))
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--image", help="含/bin/sh/printf/sleep的合法缓存镜像，仅create需要")
    parser.add_argument("--nodes", nargs=2, help="两个目标节点名，仅create需要")
    args = parser.parse_args()
    if args.mode == "create" and (not args.image or not args.nodes):
        parser.error("create必须提供--image和两个--nodes")
    {"create": create, "check": check, "cleanup": cleanup}[args.mode](args)
