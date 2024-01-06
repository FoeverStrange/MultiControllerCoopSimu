#!/usr/bin/env python
from __future__ import print_function

import sys
import time

sys.path.append("../")
from pysyncobj import SyncObj, SyncObjConf, replicated
from multiprocessing import Process
import KmeansClustering as kc
import random


def run_instance(port):
    # 将端口号转换为字符串格式，并构造selfAddr和partners
    selfAddr = f'localhost:{port}'
    partners = [f'localhost:{port + 1}'] if port % 2 == 0 else [f'localhost:{port - 1}']

    global _g_kvstorage
    _g_kvstorage = KVStorage(selfAddr, partners)
    # 在此处添加实例的运行逻辑


class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
        self.IP = selfAddress.split(':')[0]
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, cfg)
        self.__data = {}

    @replicated
    def set(self, key, value):
        print("<<<set %s = %s" % (key, value))
        self.__data[key] = value

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    def get(self, key):
        print("<<<get %s" % key)
        return self.__data.get(key, None)


_g_kvstorage = None


def KVStorageStart(selfAddr, partners):
    global _g_kvstorage
    _g_kvstorage = KVStorage(selfAddr, partners)

    def get_input(v):
        if sys.version_info >= (3, 0):
            return input(v)
        else:
            print("need python2")
            return

    while True:
        cmd = get_input(">> ").split()
        if not cmd:
            continue
        elif cmd[0] == 'set':
            # print("set %s = %s" % (cmd[1], cmd[2]))
            _g_kvstorage.set(cmd[1], cmd[2])
        elif cmd[0] == 'get':
            # print("get %s" % cmd[1])
            print(_g_kvstorage.get(cmd[1]))
        elif cmd[0] == 'pop':
            # print("pop %s" % cmd[1])
            print(_g_kvstorage.pop(cmd[1]))
        else:
            print('Wrong command')

        # 需先 pip install pysyncobj
def KVStorageServer(selfAddr, partners):
    global _g_kvstorage
    print(f'{selfAddr} start')
    _g_kvstorage = KVStorage(selfAddr, partners)
    print(f'{selfAddr} start success')
#     维护一个时间键值对，每过1秒，更新一次时间
#     用于判断是否需要进行选举
    while True:
        time.sleep(5)
        # _g_kvstorage.set('time', time.time())
        print(f'{selfAddr} time: {time.time()}')
        # 生成拓扑并同步
        adjacency_matrix, G = getTOPO()
        _g_kvstorage.set(f'adjacency_matrix:{selfAddr}', adjacency_matrix)
#         生成节点位置并同步
        nodeLocation = getLocation()
        _g_kvstorage.set(f'nodeLocation:{selfAddr}', nodeLocation)
#         生成节点资源并同步
        nodeComputingSituation, nodeStorageSituation, nodeCommunicationSituation = getSituations()
        _g_kvstorage.set(f'nodeComputingSituation:{selfAddr}', nodeComputingSituation)
        _g_kvstorage.set(f'nodeStorageSituation:{selfAddr}', nodeStorageSituation)
        _g_kvstorage.set(f'nodeCommunicationSituation:{selfAddr}', nodeCommunicationSituation)
        print(f'{selfAddr} sync success')


def getTOPO():
    adjacency_matrix, G = kc.matrixCreate(100, 5)
    return adjacency_matrix, G

def getSituations():
    # 随机生成100个节点的状态，包括计算资源、存储资源、通信资源
    nodeComputingSituation = {}
    nodeStorageSituation = {}
    nodeCommunicationSituation = {}
    # 假设资源值是在0到100之间的整数，你可以根据需要调整这个范围
    for node_id in range(1, 101):  # 生成100个节点的状态
        # 计算资源
        computing_resource = random.randint(0, 100)
        nodeComputingSituation[node_id] = computing_resource

        # 存储资源
        storage_resource = random.randint(0, 100)
        nodeStorageSituation[node_id] = storage_resource

        # 通信资源
        communication_resource = random.randint(0, 100)
        nodeCommunicationSituation[node_id] = communication_resource

    return nodeComputingSituation, nodeStorageSituation, nodeCommunicationSituation
def getLocation():
    # 随机生成100个节点的位置
    nodeLocation = {}
    for i in range(1, 101):  # 生成100个节点，编号从1到100
        x = random.uniform(-100, 100)  # 假设x坐标在-100到100之间
        y = random.uniform(-100, 100)  # 假设y坐标在-100到100之间
        nodeLocation[i] = (x, y)  # 将节点的位置和编号存储在字典中
    return nodeLocation

# https://github.com/bakwc/PySyncObj
if __name__ == '__main__':
    pass