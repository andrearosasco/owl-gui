from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic
import sys

from card import Card
from owlgui.utils.concurrency.py_queue import PyQueue


class ControlArea(QWidget):

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
                
        self.updatables = []
        self.name_list = []
        
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        
        main_layout = QtWidgets.QVBoxLayout()   # create a horizontal layout
        
        add_class_name = QLineEdit()
        add_class_name.setPlaceholderText('Insert new class name')
        add_class_button = QPushButton("Submit")
        add_class_button.clicked.connect(self.add_class)
        self.vbox.addWidget(add_class_name)
        self.vbox.addWidget(add_class_button)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        
        card = Card("placeholder", -1, self.remove)
        card.hide()
        self.vbox.addWidget(card) # add the card to the control area

        main_layout.addWidget(self.scroll)
        
        self.setLayout(main_layout)
        self.main_layout = main_layout
        self.add_class_name = add_class_name
        
        self.output_queue = PyQueue(ip="localhost", port=50000, queue_name='viz_to_det', size=1, write_format={'add': None, 'remove': None}, blocking=False)
        
    def update(self, data):
        
        for widget in self.updatables:
            widget.update(data)
            
    def remove(self, label):
        idx = self.name_list.index(label)
        card = self.updatables.pop(idx)
        self.name_list.pop(idx)
        self.vbox.removeWidget(card)
        card.setVisible(False)
        self.output_queue.write({'remove': {'class_name': label}})
        
            
    def add_class(self):
        class_name = self.add_class_name.text().strip()
        if class_name == "":
            self.error = QMessageBox()
            self.error.setWindowTitle("Error")
            self.error.setText("No class name provided")
            self.error.exec()
            return
        if class_name in self.name_list:
            self.error = QMessageBox()
            self.error.setWindowTitle("Error")
            self.error.setText(f"{class_name} already exists")
            self.error.exec()
            return
        
        self.add_class_name.clear()
       
        card = Card(class_name, len(self.updatables), rm_func=self.remove)
        self.vbox.insertWidget(2, card) # add the card to the control area
        self.updatables.append(card)
        self.name_list.append(class_name)
        
        self.output_queue.write({'add': {'class_name': class_name, 'threshold': 0.1}})



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = ControlArea()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()