#!/usr/bin/env python
from __future__ import print_function

import sys

sys.path.append("../")
from raftElection_noCMD import *



# https://github.com/bakwc/PySyncObj
if __name__ == '__main__':
    # 聆听者
    KVStorageStart('localhost:4321', ['localhost:4322','localhost:4323'])