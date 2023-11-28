import sys
from PyQt5.QtWidgets import QWidget, QSlider, QStackedLayout, QLabel, QStyle, QStyleOption, QVBoxLayout, QHBoxLayout, QSizePolicy, QMainWindow, QApplication
from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from owlgui.utils.concurrency.py_queue import PyQueue


class ConfidenceSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.output_queue = PyQueue(ip="localhost", port=50000, queue_name='viz_to_det', size=1, write_format={'threshold': None}, blocking=False)
        self.initUI()

    def initUI(self):
        self.setFixedHeight(10)
        
        self.slider1 = ConfidenceIndicator(Qt.Horizontal)
        self.slider1.setMinimum(0)
        self.slider1.setMaximum(1000)
        self.slider1.setSingleStep(1)
        self.slider1.setValue(1)
        self.slider1.setFixedWidth(200)
        self.slider1.setValue(0)

        layout_box = QHBoxLayout(self)
        layout_box.setContentsMargins(0, 0, 0, 0)
        layout_box.addWidget(self.slider1)
        self.label = QLabel("0.00")
        layout_box.addWidget(self.label)

        self.slider2 = ThresholdSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(1000)
        self.slider2.setSingleStep(1)
        self.slider2.setTickInterval(100)
        self.slider2.setTickPosition(QSlider.TicksBelow)
        self.slider2.setFixedWidth(200)
        self.slider2.setValue(100)
        self.label.setText(f'{self.slider2.value() / 1000:.3f}')
        self.slider2.valueChanged.connect(self.threshold_changed)
        
        self.setFixedWidth(230)
        
        self.slider2.setParent(self)
        
    def threshold_changed(self):
        new_thr = self.slider2.value() / 1000
        self.label.setText(f'{new_thr:.3f}')
        self.output_queue.write({'threshold': {'class': self.parent().parent().idx, 'value': new_thr}})
        
    def update_confidence(self, confidence):
        self.slider1.setValue(confidence)
        
        
class ThresholdSlider(QSlider):
    def __init__(self, direction):
        super().__init__(direction)
        self.setMaximumHeight(10)
        self.setStyleSheet(self.get_style_sheet())

    @staticmethod
    def get_style_sheet():
        return """
            QSlider::groove:horizontal { 
                background: rgba(100, 100, 100, 0);
                height: 4px; 
                border-radius: 4px;
            }
            
            QSlider::groove:horizontal:hover { 
                background-color: rgba(48,100,47, 0);
                border: 0px solid #424242; 
                height: 6px; 
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal { 
                background-color: rgb(239,82,82);
                border: 2px solid rgb(239,82,82); 
                width: 5px; 
                height: 5px; 
                line-height: 5px; 
                margin-top: -2px; 
                margin-bottom: -2px; 
                border-radius: 4px; 
            }
            
            QSlider::handle:horizontal:hover { 
                background-color: rgb(239,82,82); 
                border: 2px solid rgb(239,82,82);  
                width: 5px; 
                height: 5px; 
                line-height: 5px; 
                margin-top: -2px; 
                margin-bottom: -2px; 
                border-radius: 4px; 
            }
            
            QSlider:sub-page:horizontal {
                background: rgba(239,82,82, 0);  
            }
            """

class ConfidenceIndicator(QSlider):
    def __init__(self, direction):
        super().__init__(direction)
        self.setMaximumHeight(10)
        self.setStyleSheet(self.get_style_sheet())

    def mousePressEvent(self, event):
        pass

    @staticmethod
    def get_style_sheet():
        return """
            QSlider::groove:horizontal { 
                background-color: rgba(48,100,47, 0);
                border: 0px solid #424242; 
                height: 6px; 
                border-radius: 4px;
            }
            
            QSlider::groove:horizontal:hover { 
                background-color: rgba(48,100,47, 0);
                border: 0px solid #424242; 
                height: 6px; 
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal { 
                background-color: rgba(239,82,82, 0);
                border: 2px solid rgba(239,82,82, 0); 
                width: 5px; 
                height: 5px; 
                line-height: 5px; 
                margin-top: -2px; 
                margin-bottom: -2px; 
                border-radius: 4px; 
            }
            
            QSlider::handle:horizontal:hover { 
                background-color: rgba(239,82,82, 0); 
                border: 2px solid rgba(239,82,82, 0);  
                width: 5px; 
                height: 5px; 
                line-height: 5px; 
                margin-top: -2px; 
                margin-bottom: -2px; 
                border-radius: 4px; 
            }
            
            QSlider:sub-page:horizontal {
                background: rgba(40, 40, 40, 100);  
            }
            """
    

if __name__ == '__main__':
    import PyQt5
    app = QApplication(sys.argv)

    ex = ConfidenceSlider()
    ex.show()

    sys.exit(app.exec_())