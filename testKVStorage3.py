#!/usr/bin/env python

import sys

sys.path.append("../")
from raftElection_noCMD import *



# https://github.com/bakwc/PySyncObj
if __name__ == '__main__':
    KVStorageServer('localhost:4323', ['localhost:4322','localhost:4321'])