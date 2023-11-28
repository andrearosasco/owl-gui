import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2

from control_area import ControlArea

class VideoCapture(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.label = QtWidgets.QLabel() # create a label to display the video
        main_layout = QtWidgets.QHBoxLayout() # create a horizontal layout
        main_layout.addWidget(self.label) # add the label to the main layout
        self.setLayout(main_layout) # set the layout
        
        self.data = {}
        
    def update(self, data):
        self.data.update(data)
        
        if 'rgb' not in self.data:
            return
        
        frame = self.data['rgb']
        
        if 'labels' in self.data:
            scores, boxes, labels = self.data['scores'], self.data['boxes'], self.data['labels']
            for score, box, label in zip(scores, boxes, labels):
                if score < self.data["thresholds"][label]:
                    continue
                cx, cy, w, h = (box * 640).astype(int)
                x1, x2, y1, y2 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
                frame = cv2.rectangle(img=frame, pt1=(x1, x2),
                                                    pt2=(y1, y2), color=(255, 0, 0), thickness=5)

                frame = cv2.putText(frame, f'{self.data["class_names"][label]}: {score:1.2f}', (int(cx - w / 2), int(cy + h / 2 + 0.2)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                
                print(score)

        
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888) # create a QImage from the frame
        pixmap = QtGui.QPixmap.fromImage(image) # create a QPixmap from the QImage
        self.label.setPixmap(pixmap) # set the pixmap to the label

    def on_click(self):
        text = self.textbox.text() # get the text from the text box
        print(text) # print it or do something else with it

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = VideoCapture()
    window.show()
    sys.exit(app.exec_())
