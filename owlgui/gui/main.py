import sys
from PyQt5 import QtCore, QtWidgets

from control_area import ControlArea
from video_capture import VideoCapture
from owlgui.utils.concurrency.py_queue import PyQueue

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        self.timer = QtCore.QTimer() # create a timer to update the video
        self.timer.timeout.connect(self.read) # connect the timer to the nextFrame slot

        main_layout = QtWidgets.QHBoxLayout() # create a horizontal layout
        control_area = ControlArea()
        video_capture = VideoCapture()
            
        main_layout.addWidget(control_area) # add the control layout to the main layout
        main_layout.addWidget(video_capture) # add the label to the main layout
        self.setLayout(main_layout) # set the layout
        
        self.control_area = control_area
        self.video_capture = video_capture
        
        self.source_input = PyQueue(ip="localhost", port=50000, queue_name='det_to_viz', size=1, blocking=False)
        self.detection_input = PyQueue(ip="localhost", port=50000, queue_name='source_to_viz', size=1, blocking=False)
        
    def read(self):
        data = {}
        data.update(self.source_input.read())
        data.update(self.detection_input.read())
        
        self.control_area.update(data)
        self.video_capture.update(data)


    def start(self):
        self.timer.start(1000//60) # start the timer with 24 fps

    def stop(self):
        self.timer.stop() # stop the timer

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.start()
    window.show()
    sys.exit(app.exec_())
