import copy
from math import ceil, floor
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, QtGui
import sys
import numpy as np
import skimage

from test import ConfidenceSlider
from owlgui.utils.concurrency.py_queue import PyQueue


class Card(QWidget):

    def __init__(self, text, idx, rm_func):
        super().__init__()
        self.rm_func = rm_func
        self.output_queue = PyQueue(ip="localhost", port=50000, queue_name='viz_to_det', size=1, write_format={'remove': None}, blocking=False)
        
        
        self.idx = idx
        main_layout = QtWidgets.QHBoxLayout()
        
        # Setting card frame appearence
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.Box)
        card.setFrameShadow(QtWidgets.QFrame.Plain)
        card.setLineWidth(3)
        card.setMaximumHeight(200)
        # card.setMinimumWidth(200)
        
        top_widget = QWidget()
        left_widget = QWidget()
        right_widget = QWidget()
        # Setting card layout
        card_layout = QtWidgets.QVBoxLayout()
        top_layout = QtWidgets.QHBoxLayout(top_widget)
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        card.setLayout(card_layout) # the card widget becomes the layout parent
        
        # Adding components to the card
        label = QtWidgets.QLabel(text)
        detection = QtWidgets.QLabel() # create a label the detection
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove)
        confidence_slider = ConfidenceSlider()
        
        left_layout.addWidget(label)
        left_layout.addWidget(detection)
        
        right_layout.addWidget(remove_button)
        
        top_layout.addWidget(left_widget)
        top_layout.addWidget(right_widget)             

        card_layout.addWidget(top_widget)
        card_layout.addWidget(confidence_slider)
        
        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)
        
        # Adding the card to the widget layout
        main_layout.addWidget(card)
        self.setLayout(main_layout)
        
        # Image placeholder
        image = QtGui.QImage(np.zeros([80, 80]), 80, 80, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        detection.setPixmap(pixmap)
        
        self.label = label
        self.detection = detection
        self.confidence_slider = confidence_slider
        
    def remove(self):
        self.rm_func(self.label.text())
        
        
    def update(self, data):
        if 'labels' not in data:
            return
        
        if self.idx not in data['labels']:
            return
        
        class_idxs = data['labels'] == self.idx
        max_idx = np.argmax(data['scores'][class_idxs])
        score = data['scores'][class_idxs][max_idx]
        box = data['boxes'][class_idxs][max_idx]
        
        cx, cy, w, h = (box * 640).astype(int)
        x1, x2, y1, y2 = int(cx - w / 2), int(cx + w / 2), int(cy - h / 2), int(cy + h / 2)
        x1, x2, y1, y2 = *np.clip(np.array([x1, x2]), 0, 640), *np.clip(np.array([y1, y2]), 0, 480)
        
        self.confidence_slider.update_confidence(int(score * 1e3))

        if 'rgb' in data:
            frame = data['rgb']
            np.clip
            test = frame[y1:y2, x1:x2]
            h, w, _ = test.shape
            size = max(h, w)
            image_padded = np.pad(test, ((floor((size - h) / 2), ceil((size - h) / 2)), ( floor((size - w) / 2), ceil((size - w) / 2)), (0, 0)), constant_values=1)
            frame = skimage.transform.resize(image_padded, (80, 80), anti_aliasing=True)
            frame = (frame * 255).astype(np.uint8)
            
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888) # create a QImage from the frame
            pixmap = QtGui.QPixmap.fromImage(image) # create a QPixmap from the QImage
            self.detection.setPixmap(pixmap) # set the pixmap to the label

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Card(text='Card')
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()