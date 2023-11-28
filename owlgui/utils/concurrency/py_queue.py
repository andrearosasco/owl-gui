import copy
from multiprocessing import Process
import time
from multiprocessing.managers import BaseManager
from queue import Empty, Full

from owlgui.manager import ConnectionManager


def connect(manager):
    print('Connecting to manager...')
    start = time.time()

    while True:
        try:
            manager.connect()
            break
        except ConnectionRefusedError as e:
            if time.time() - start > 120:
                print('Connection refused.')
                raise e
            time.sleep(1)
    print('Connected to manager.')


class PyQueue:

    def __init__(self, ip, port, queue_name, size=1, write_format=None, read_format=None,
                 auto_write=True, auto_read=True, blocking=False):

        self.auto_write = auto_write
        self.auto_read = auto_read

        self.blocking = blocking
        self.write_format = write_format
        self.read_format = read_format

        BaseManager.register('get_queue')
        manager = BaseManager(address=(ip, port), authkey=b'abracadabra')
        connect(manager)
        self.queue = manager.get_queue(queue_name, size)
        self.name = queue_name

    def startup(self):
        pass

    def write(self, data, blocking=None):
        if blocking is None:
            blocking = self.blocking
            
        if self.write_format is None:
            raise RuntimeError("You need to specify a write_format to send the output to the correct nodes")

        data_dest = copy.deepcopy(self.write_format)
        data_dest.update(data)  # add computed values while keeping default ones
        data_dest = {k: v for k, v, in data_dest.items() if k in self.write_format}  # remove unnecessary keys
        
        for k, v in list(data_dest.items()):
            if v is None:
                del data_dest[k]
        
        if len(data_dest) == 0:
            return

        msg = {}
        if not blocking:
            while not self.queue.empty():
                try:
                    msg = self.queue.get(block=False)
                except Empty:
                    break

        msg.update(data_dest)
        try:
            self.queue.put(msg, block=blocking)
        except Full:
            pass

    def read(self, blocking=None):
        if blocking is None:
            blocking = self.blocking

        if blocking:
            msg = self.queue.get()
        else:
            if not self.queue.empty():
                msg = self.queue.get()
            else:
                msg = {}

        if self.read_format is not None:
            template = copy.deepcopy(self.read_format)
            template.update(msg)  # add computed values while keeping default ones
            msg = {k: v for k, v, in template.items() if k in self.read_format}  # remove unnecessary keys

        return msg
