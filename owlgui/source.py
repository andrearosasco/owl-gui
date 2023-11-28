import copy
import sys
from pathlib import Path

from utils.base_config import BaseConfig
from utils.concurrency.generic_node import GenericNode
from utils.concurrency.py_queue import PyQueue
from utils.input import WinCamera


from logging import INFO

class Logging(BaseConfig):
    level = INFO


class Network(BaseConfig):
    node = GenericNode

    class Args:
        out_queues = {
            'to_det': PyQueue(ip="localhost", port=50000, queue_name='source_to_det', write_format={'rgb': None}, blocking=False),
            'to_viz': PyQueue(ip="localhost", port=50000, queue_name='source_to_viz', write_format={'rgb': None}, blocking=False)
        }


class Input(BaseConfig):
    camera = WinCamera


class Source(Network.node):
    def __init__(self):
        super().__init__(**Network.Args.to_dict())
        self.camera = None

    def startup(self):
        self.camera = Input.camera()

    def loop(self, _):

        while True:
            try:
                data = self.camera.read()
                data = copy.deepcopy(data)

                return data

            except RuntimeError as e:
                print("Realsense: frame didn't arrive")
                self.camera = Input.camera(**Input.Params.to_dict())


if __name__ == '__main__':
    source = Source()
    source.run()
