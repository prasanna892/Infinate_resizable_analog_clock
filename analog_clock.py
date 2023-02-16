from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime
import time
import sys

# creating required variables
RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.HighQualityAntialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.LosslessImageRendering
    | QPainter.RenderHint.Qt4CompatiblePainting
    | QPainter.RenderHint.NonCosmeticDefaultPen
    | QPainter.RenderHint.TextAntialiasing
)

# Creating AnalogClock class
class AnalogClock(QWidget):
    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(parent)

        # Setting window to no icon, frameless and transparent
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Setting getted data to window
        self.screen_resize = self.size_ = 200

        self.pos_x = 100
        self.pos_y = 100

        # getting time
        self.now = datetime.now()
        self.hour = int(self.now.strftime("%I"))
        self.minute = int(self.now.strftime("%M"))
        self.seconds = int(self.now.strftime("%S"))

        # flag variable
        self.oldPos = QCursor.pos()
        self.cursor_above_window = False
        self.cursor_enter_time = 0

        # Setting window position and size
        self.setGeometry(self.pos_x, self.pos_y, self.size_, self.size_)
        self.setMinimumSize(200, 200)

        # adding sizegrip
        self.addSizeGrip()

        # creating timer to update window at each 500ms
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.update_window)
        self.timer1.start(1000)

        # checking window close operation and setting it to closeEvent()
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

    # adding sizegrip
    def addSizeGrip(self):
        self.widget = QWidget(self)
        self.widget.setGeometry(0, 0, self.width(), self.height())

        self.sizegrip_ani = [QLabel(self.widget) for _ in range(6)]
        x = y = -7
        for i in range(6):
            if i == 5:
                x = y = -14
            self.sizegrip_ani[i].setGeometry(self.width() + x, self.width() + y, 7, 7)
            self.sizegrip_ani[i].setStyleSheet(
                "background: rgba(192,192,192, 50); border: 1px solid rgba(0, 100, 100, 50)"
            )
            if i % 2 == 0:
                y -= 7
            x, y = y, x

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.sizegrip = QSizeGrip(self)
        layout.addWidget(self.sizegrip, 0, Qt.AlignBottom | Qt.AlignRight)
        self.sizegrip.setFixedSize(25, 25)
        self.sizegrip.setStyleSheet("background: rgba(0, 0, 0, 0)")

        self.widget.setLayout(layout)

        self.widget.setHidden(True)

    # hide sizegrip after 5 sec
    def hideSizegrip(self):
        if self.underMouse():
            self.cursor_enter_time = int(time.time())
            if not self.cursor_above_window:
                self.cursor_above_window = True
                self.widget.setHidden(False)
        elif int(time.time()) - self.cursor_enter_time == 5:
            self.widget.setHidden(True)
            self.cursor_above_window = False

    # hand rotation calculation
    def hand_rotation(self, val):
        val = (1 / 360) * val
        return abs(val + (-0.25 if val * 100 > 25 else 0.75))

    # for drawing clock face and hands
    def paintEvent(self, event):
        # setting painter to draw clock face
        painter = QPainter(self)
        painter.setRenderHints(RENDER_HINTS, True)

        # drawing spike
        spike_outer_circle_path = QPainterPath()
        spike_outer_circle_path.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.45,
            self.size_ * 0.45,
        )
        spike_inner_circle_path1 = QPainterPath()
        spike_inner_circle_path1.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.39,
            self.size_ * 0.39,
        )
        spike_inner_circle_path2 = QPainterPath()
        spike_inner_circle_path2.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.41,
            self.size_ * 0.41,
        )
        number_circle_path1 = QPainterPath()
        number_circle_path1.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.37,
            self.size_ * 0.37,
        )
        number_circle_path2 = QPainterPath()
        number_circle_path2.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.35,
            self.size_ * 0.35,
        )

        number_font = QFont("Consolas", int(self.size_ * 0.05), 0, True)
        number_fm = QFontMetrics(number_font)
        number_txt_rect = number_fm.boundingRect("00")
        number_gradientP = QGradient(QGradient.SummerGames)
        painter.setPen(QPen(number_gradientP, 3))
        painter.setFont(number_font)

        number_rect = number_txt_rect
        number_rect.setSize(
            QSize(int(number_rect.width() * 1.6), int(number_rect.height() * 1.6))
        )

        painter.setPen(QPen(QGradient(QGradient.Blessing), 4))
        number_list = (1, 2, 4, 5, 7, 8, 10, 11)
        for idx, val in enumerate(number_list):
            spike_outer = spike_outer_circle_path.pointAtPercent((8.33 * val) / 100)
            spike_inner = spike_inner_circle_path2.pointAtPercent((8.33 * val) / 100)
            painter.drawLine(spike_outer, spike_inner)
            number_rect.moveCenter(
                number_circle_path1.pointAtPercent((8.33 * val) / 100).toPoint()
            )
            painter.drawText(
                number_rect,
                Qt.AlignCenter,
                str((number_list[2:] + number_list[:2])[idx]),
            )

        painter.setPen(QPen(QGradient(QGradient.StarWine), 4))
        number_list = (6, 9, 12, 3)
        for i in range(1, 5):
            spike_outer = spike_outer_circle_path.pointAtPercent((25 * i) / 100)
            spike_inner = spike_inner_circle_path1.pointAtPercent((25 * i) / 100)
            painter.drawLine(spike_outer, spike_inner)
            number_rect.moveCenter(
                number_circle_path2.pointAtPercent((25 * i) / 100).toPoint()
            )
            painter.drawText(number_rect, Qt.AlignCenter, str(number_list[i - 1]))

        painter.setPen(QPen(Qt.green, self.size_ * 0.01))
        # drawing clock second hand
        sec_hand_path = QPainterPath()
        sec_hand_path.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.35,
            self.size_ * 0.35,
        )
        sec_hand_point = sec_hand_path.pointAtPercent(
            self.hand_rotation(self.seconds * 6)
        )
        painter.drawLine(QPointF(self.size_ / 2, self.size_ / 2), sec_hand_point)

        painter.setPen(QPen(Qt.blue, self.size_ * 0.01))
        # drawing clock minute hand
        min_hand_path = QPainterPath()
        min_hand_path.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2), self.size_ * 0.3, self.size_ * 0.3
        )
        min_hand_point = min_hand_path.pointAtPercent(
            self.hand_rotation(self.minute * 6)
        )
        painter.drawLine(QPointF(self.size_ / 2, self.size_ / 2), min_hand_point)

        painter.setPen(QPen(Qt.red, self.size_ * 0.01))
        # drawing clock hour hand
        hour_hand_path = QPainterPath()
        hour_hand_path.addEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.25,
            self.size_ * 0.25,
        )
        hour_hand_point = hour_hand_path.pointAtPercent(
            self.hand_rotation((0.5 * self.minute) + (self.hour * 30))
        )
        painter.drawLine(QPointF(self.size_ / 2, self.size_ / 2), hour_hand_point)

        painter.setPen(QPen(Qt.black, self.size_ * 0.015, cap=Qt.RoundCap))
        painter.drawPoint(self.rect().center())

        painter.setPen(QPen(Qt.yellow, self.size_ * 0.01))
        painter.setBrush(QColor(0, 0, 0, 20))
        painter.drawEllipse(
            QPointF(self.size_ / 2, self.size_ / 2),
            self.size_ * 0.45,
            self.size_ * 0.45,
        )

        painter.end()

    # function for update date and time
    def update_datetime(self):
        self.now = datetime.now()
        self.hour = int(self.now.strftime("%I"))
        self.minute = int(self.now.strftime("%M"))
        self.seconds = int(self.now.strftime("%S"))

    # function for updating window on resize
    def update_size(self):
        self.screen_resize = min(self.width(), self.height())

        # setting new size
        self.size_ = self.screen_resize
        self.resize(self.size_, self.size_)

    # function to update sizegrip
    def update_sizegrip(self):
        x = y = -7
        for i in range(6):
            if i == 5:
                x = y = -14
            self.sizegrip_ani[i].move(self.width() + x, self.width() + y)
            if i % 2 == 0:
                y -= 7
            x, y = y, x

    # UI update
    def update_window(self):
        self.hideSizegrip()
        self.update_datetime()
        self.update()

    # catch mouse hold event occure
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    # catch mouse move event occure
    def mouseMoveEvent(self, event):
        if not self.sizegrip.underMouse():
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    # detect key down event
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.finish()

    # detect window resize event
    def resizeEvent(self, event):
        self.widget.resize(self.size())
        self.update_size()
        self.update_sizegrip()

    # to close
    def finish(self):
        QCoreApplication.instance().quit()  # quit window


# creating QApplication
def load():
    app = QApplication(sys.argv)
    analog_clock = AnalogClock()
    app.aboutToQuit.connect(analog_clock.finish)  # detect close event by system
    analog_clock.show()
    app.exec()


# main code
if __name__ == "__main__":
    load()
