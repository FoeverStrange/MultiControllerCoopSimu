#!/usr/bin/env python

import sys
import time
from datetime import datetime # 用于获取当前时间
import re  # 用于正则表达式匹配

sys.path.append("../")
from pysyncobj import SyncObj, SyncObjConf, replicated
from multiprocessing import Process
import KmeansClustering as kc
import random

class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
        self.IP = selfAddress.split(':')[0]
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, cfg)
        self.time_diffs = []  # 用于存储时间差的列表
        self.__data = {}

    @replicated
    def set(self, key, value):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        strForProcess = f"{timestamp} <<<set {key} = {value}"
        timeDiff = extract_and_calculate_timestamp_diff(strForProcess)
        print(f'{self.IP} timeDiff:{timeDiff} set {key} = {value}')
        # print(strForProcess)
        self.__data[key] = value
        self.time_diffs.append(timeDiff)
        print(f'{self.IP} avg_time_diffs:{sum(self.time_diffs) / len(self.time_diffs)}')

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    def get(self, key):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"{timestamp} <<<get {key}")
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

        # 根据时间戳生成序列号
        seq = datetime.now()
        # 生成拓扑并同步
        adjacency_matrix, G = getTOPO()
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        _g_kvstorage.set(f't:{timeStamp},adjacency_matrix:{selfAddr}', adjacency_matrix)
#         生成节点位置并同步
        nodeLocation = getLocation()
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        _g_kvstorage.set(f't:{timeStamp},nodeLocation:{selfAddr}', nodeLocation)
#         生成节点资源并同步
        nodeComputingSituation, nodeStorageSituation, nodeCommunicationSituation = getSituations()
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        _g_kvstorage.set(f't:{timeStamp},nodeComputingSituation:{selfAddr}', nodeComputingSituation)
        _g_kvstorage.set(f't:{timeStamp},nodeStorageSituation:{selfAddr}', nodeStorageSituation)
        _g_kvstorage.set(f't:{timeStamp},nodeCommunicationSituation:{selfAddr}', nodeCommunicationSituation)
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


def extract_and_calculate_timestamp_diff(s):
    # 使用正则表达式匹配时间戳
    timestamps = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}', s)

    if len(timestamps) != 2:
        raise ValueError("字符串中必须恰好包含两个时间戳！")

        # 将字符串时间戳转换为datetime对象
    end_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S.%f')
    start_time = datetime.strptime(timestamps[1], '%Y-%m-%d %H:%M:%S.%f')

    # 计算时间戳之间的差值
    time_diff = (end_time - start_time).total_seconds()

    return time_diff
# https://github.com/bakwc/PySyncObj
if __name__ == '__main__':
    pass