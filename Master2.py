import json 
#import socket
import sys
import _thread
from socket import *
import threading
import random

class Worker:
    def __init__(self,id,slots,port,running_tasks):
        self.id = id
        self.slots = slots
        self.port = port
        self.running_tasks = running_tasks
    