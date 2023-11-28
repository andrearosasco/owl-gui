from PyQt5.QtWidgets import QWidget, QSlider, QStackedLayout, QLabel, QStyle, QStyleOption, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

import sys

class ConfidenceSlider(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QHBoxLayout()

        self.setMaximumHeight(15)
        label = QtWidgets.QLabel('0.000') # create a label to display the video
        
        threshold_slider = ThresholdSlider(Qt.Horizontal)
        threshold_slider.setMinimum(0)
        threshold_slider.setMaximum(1000)
        threshold_slider.setSingleStep(1)
        threshold_slider.setTickInterval(100)
        threshold_slider.setTickPosition(QSlider.TicksBelow)
        
        threshold_slider.valueChanged.connect(self.threshold_changed)
        
        confidence_indicator = ConfidenceIndicator(Qt.Horizontal)
        confidence_indicator.setMinimum(0)
        confidence_indicator.setMaximum(1000)
        confidence_indicator.setSingleStep(1)
        confidence_indicator.setValue(0)

        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackAll)

        stacked_layout.addWidget(confidence_indicator)
        stacked_layout.addWidget(threshold_slider)
        
        main_layout.addLayout(stacked_layout)
        main_layout.addWidget(label)
        
        self.setLayout(main_layout)
        
        self.confidence_indicator = confidence_indicator
        self.threshold_slider = threshold_slider
        self.label = label
        
    def update(self, data):
        self.confidence_indicator.setValue(700)
        
    def threshold_changed(self):
        self.label.setText(f'{self.threshold_slider.value() / 1000:.3f}')
        # And send the new value to the detection module

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
    app = QtWidgets.QApplication(sys.argv)
    window = ConfidenceSlider()
    window.show()
    sys.exit(app.exec_())