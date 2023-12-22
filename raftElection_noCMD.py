#!/usr/bin/env python
from __future__ import print_function

import sys

sys.path.append("../")
from pysyncobj import SyncObj, SyncObjConf, replicated
from multiprocessing import Process


def run_instance(port):
    # 将端口号转换为字符串格式，并构造selfAddr和partners
    selfAddr = f'localhost:{port}'
    partners = [f'localhost:{port + 1}'] if port % 2 == 0 else [f'localhost:{port - 1}']

    global _g_kvstorage
    _g_kvstorage = KVStorage(selfAddr, partners)
    # 在此处添加实例的运行逻辑


class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
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
    _g_kvstorage = KVStorage(selfAddr, partners)
#     维护一个时间键值对，每过1秒，更新一次时间
#     用于判断是否需要进行选举
    import time
    while True:
        time.sleep(1)
        _g_kvstorage.set('time', time.time())



# https://github.com/bakwc/PySyncObj
if __name__ == '__main__':
    KVStorageStart()