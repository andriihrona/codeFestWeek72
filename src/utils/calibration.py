import sys

import cv2
import freenect
import numpy as np
from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QMainWindow,
    QWidget,
)

_H = None

class QControl(QGraphicsRectItem):
    def __init__(self, parent, x, y):
        super().__init__(0, 0, 10, 10)
        self.setBrush(QBrush(Qt.GlobalColor.red))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.parent = parent
        self.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.parent.recompute_homography()
        return super().itemChange(change, value)


class QCalibrationApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rgb_item = QGraphicsPixmapItem()
        self.unwrapped_item = QGraphicsPixmapItem()
        self.depth_item = QGraphicsPixmapItem()

        self.lview = QGraphicsView()
        self.cview = QGraphicsView()
        self.rview = QGraphicsView()
        self.lscene = QGraphicsScene()
        self.cscene = QGraphicsScene()
        self.rscene = QGraphicsScene()

        self.controls = [
            QControl(self, 0, 0),
            QControl(self, 630, 0),
            QControl(self, 630, 470),
            QControl(self, 0, 470),
        ]

        self.lscene.addItem(self.rgb_item)
        for control in self.controls:
            self.lscene.addItem(control)
        self.cscene.addItem(self.unwrapped_item)
        self.rscene.addItem(self.depth_item)

        self.lview.setScene(self.lscene)
        self.cview.setScene(self.cscene)
        self.rview.setScene(self.rscene)

        self.lview.setMinimumSize(640, 480)
        self.cview.setMinimumSize(640, 480)
        self.rview.setMinimumSize(640, 480)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(self.lview)
        layout.addWidget(self.cview)
        layout.addWidget(self.rview)
        self.setCentralWidget(central)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.peek_frame)
        self.timer.start(30)  # Kinect frame rate

    def peek_frame(self):
        frame = freenect.sync_get_video()[0]
        depth_frame = freenect.sync_get_depth()[0]

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        depth_frame = depth_frame.astype(np.uint8)

        self.display_frame(frame, self.rgb_item, self.lscene)
        if _H is not None:
            unwrapped = cv2.warpPerspective(frame, _H, (frame.shape[1], frame.shape[0]))
            self.display_frame(unwrapped, self.unwrapped_item, self.cscene)

        depth_rgb = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_frame, alpha=0.03), cv2.COLORMAP_JET
        )
        if _H is not None:
            depth_rgb = cv2.warpPerspective(
                depth_rgb, _H, (depth_rgb.shape[1], depth_rgb.shape[0])
            )
        self.display_frame(depth_rgb, self.depth_item, self.rscene)
        # return frame

    def display_frame(self, frame, item, scene):
        image = QImage(
            frame.data,
            frame.shape[1],
            frame.shape[0],
            frame.strides[0],
            QImage.Format.Format_RGB888,
        )
        item.setPixmap(QPixmap.fromImage(image))
        scene.setSceneRect(QRectF(image.rect()))  # Convert QRect to QRectF

    def recompute_homography(self):
        try:
            coordinates = [
                (control.scenePos().x(), control.scenePos().y())
                for control in self.controls
            ]
        except AttributeError:
            coordinates = [(0, 0), (640, 0), (640, 480), (0, 480)]
        src_pts = np.array(coordinates, dtype=np.float32)
        dst_pts = np.array([(0, 0), (640, 0), (640, 480), (0, 480)], dtype=np.float32)
        global _H
        _H = cv2.getPerspectiveTransform(src_pts, dst_pts)


def run_calibration():
    App = QApplication(sys.argv)
    win = QCalibrationApp()
    win.show()
    App.exec()
    return _H


m = run_calibration()
print(m)