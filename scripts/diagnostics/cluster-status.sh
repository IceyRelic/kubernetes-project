#!/bin/sh
# 只读状态，不输出Secret、kubeconfig或业务日志；先核对context。
set -eu
kubectl config current-context
kubectl get nodes
kubectl -n spring-cloud get deployments,services,ingresses,hpa
kubectl -n logging get deployments,statefulsets,daemonsets,pvc
kubectl -n monitoring get prometheus,prometheusrule,servicemonitor,probe
