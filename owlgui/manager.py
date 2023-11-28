import sys
import threading
from collections import defaultdict
from multiprocessing import Process, process
from multiprocessing.managers import BaseManager
from queue import Queue


# {node: Queue(1) for node in Config.nodes}
queues = dict()


def get_queue(name, size):
    if name not in queues:
        queues[name] = Queue(size)
        
    return queues[name]

class ConnectionManager(Process):
    def run(self):

        print('Starting communication server')

        BaseManager.register('get_queue', callable=get_queue)
        m = BaseManager(address=('0.0.0.0', 50000), authkey=b'abracadabra')
        server = m.get_server()

        server.stop_event = threading.Event()
        process.current_process()._manager_server = server
        try:
            accepter = threading.Thread(target=server.accepter)
            accepter.daemon = True
            accepter.start()
            print('Communication server online')
            try:
                while not server.stop_event.is_set():
                    server.stop_event.wait(1)
            except (KeyboardInterrupt, SystemExit):
                pass
        finally:
            if sys.stdout != sys.__stdout__:
                print('resetting stdout, stderr')
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            sys.exit(0)


if __name__ == '__main__':
    ConnectionManager().run()