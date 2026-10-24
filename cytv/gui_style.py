"""Desktop presentation only; installation stays in the semantic CLI bridge."""
from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget, QComboBox, QRadioButton

# A fixed light palette keeps Qt controls legible even on a dark system theme.
STYLE = '''
QMainWindow, QMessageBox { background: #f7f9fc; }
QWidget { font-family: "Noto Sans", "Segoe UI", "Helvetica Neue"; font-size: 14px; color: #182c46; }
QWidget#sidebar { background: #142d48; }
QLabel { background: transparent; }
QLabel#brand { color: #ffffff; font-size: 20px; font-weight: 700; }
QLabel#platform { color: #b3c8dd; font-size: 12px; }
QLabel#railTitle { color: #d4e2ef; font-size: 14px; font-weight: 600; }
QLabel#railNote { color: #b3c8dd; font-size: 13px; }
QLabel#version { color: #b3c8dd; font-size: 12px; }
QFrame#step { border: none; border-radius: 10px; background: transparent; }
QFrame#step[state="current"] { background: #254760; }
QLabel#stepNumber { color: #b3c8dd; border: 1px solid #6d879f; border-radius: 15px; font-weight: 600; }
QLabel#stepName { color: #b3c8dd; font-size: 13px; }
QFrame#step[state="current"] QLabel { color: white; }
QFrame#step[state="current"] QLabel#stepNumber { background: #2670d6; border-color: #76adf4; }
QFrame#step[state="complete"] QLabel { color: #a8e5cf; }
QFrame#step[state="complete"] QLabel#stepNumber { border-color: #8ccfb8; }
QFrame#step[state="error"] QLabel { color: #ffd2c7; }
QFrame#step[state="error"] QLabel#stepNumber { border-color: #ffd2c7; }
QLabel#badge { color: #335773; font-size: 12px; background: #e7eef6; border-radius: 11px; padding: 5px 12px; }
QLabel#title { font-size: 30px; font-weight: 700; color: #142d48; }
QLabel#subtitle { color: #52647a; font-size: 14px; }
QTextBrowser { background: transparent; color: #52647a; border: none; padding: 0; selection-background-color: #d9e8fc; }
QWidget#form { background: white; border-radius: 12px; }
QLabel#promptTitle { font-size: 15px; font-weight: 600; }
QPushButton { background: white; border: 1px solid #b2c1d2; border-radius: 8px; padding: 10px 16px; font-weight: 500; min-height: 22px; }
QPushButton:hover { background: #edf3fa; border-color: #648ab6; }
QPushButton:pressed { background: #dce8f7; }
QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 2px solid #2670d6; }
QPushButton[primary="true"] { background: #2466c5; color: white; border: 2px solid #2466c5; font-weight: 600; }
QPushButton[primary="true"]:hover { background: #1b56ad; border-color: #1b56ad; }
QPushButton[primary="true"]:pressed { background: #16468e; }
QPushButton[primary="true"]:focus { border-color: #102f53; }
QPushButton:disabled { background: #edf0f4; color: #7c8899; border-color: #d5dce5; }
QPushButton#maintenanceToggle { background: transparent; border: none; color: #42638a; text-align: left; padding: 6px 0; }
QPushButton#maintenanceToggle:focus { border: 2px solid #2670d6; padding: 4px; }
QPushButton#close { background: transparent; padding: 6px 16px; }
QLineEdit, QComboBox { background: white; color: #182c46; border: 1px solid #a6b7cb; border-radius: 7px; padding: 10px 12px; min-height: 22px; selection-background-color: #d9e8fc; }
QComboBox { padding-right: 30px; }
QComboBox::down-arrow { image: none; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView { color: #182c46; background: white; selection-background-color: #d9e8fc; selection-color: #182c46; padding: 6px; }
QComboBox:disabled { background: #edf0f4; color: #7c8899; }
QComboBox#language { font-size: 12px; min-height: 18px; padding: 6px 30px 6px 10px; }
QProgressBar { background: #e4ecf6; border: none; border-radius: 3px; }
QProgressBar::chunk { background: #2466c5; border-radius: 3px; }
QScrollBar:vertical { background: #edf1f6; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #a6b7cb; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
'''


class TVPreview(QWidget):
    """Resolution-independent illustration, with no network or image dependencies."""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(206)
        self.setAccessibleName('Clean Your TV')

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = min(self.width() / 560, self.height() / 206)
        p.translate((self.width() - 560 * scale) / 2, 0)
        p.scale(scale, scale)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#e8eff8'))
        p.drawRoundedRect(QRectF(0, 8, 560, 190), 16, 16)
        # Quiet signal arcs connect the installer to the TV.
        p.setPen(QPen(QColor('#bbcee4'), 2))
        for size in (46, 72, 98):
            p.drawArc(QRectF(440-size/2, 104-size/2, size, size), -65*16, 130*16)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#315578'))
        p.drawRoundedRect(QRectF(118, 22, 326, 154), 9, 9)
        gradient = QLinearGradient(125, 30, 432, 168)
        gradient.setColorAt(0, QColor('#193b60'))
        gradient.setColorAt(1, QColor('#346d93'))
        p.setBrush(gradient)
        p.drawRoundedRect(QRectF(125, 29, 312, 138), 4, 4)
        p.setPen(QColor('#ffffff'))
        p.setFont(QFont('Noto Sans', 15, QFont.Weight.DemiBold))
        p.drawText(QRectF(146, 48, 270, 32), Qt.AlignmentFlag.AlignLeft, 'Clean Your TV')
        p.setPen(Qt.PenStyle.NoPen)
        for x, color in ((146, '#91c5dc'), (214, '#dbb7a0'), (282, '#c3c9e8'), (350, '#a7d7c5')):
            p.setBrush(QColor(color))
            p.drawRoundedRect(QRectF(x, 98, 56, 43), 6, 6)
            p.setBrush(QColor('#ffffff'))
            p.drawRoundedRect(QRectF(x+13, 110, 30, 3), 1, 1)
            p.drawRoundedRect(QRectF(x+13, 119, 20, 3), 1, 1)
        p.setBrush(QColor('#315578'))
        p.drawRoundedRect(QRectF(273, 176, 16, 9), 2, 2)
        p.drawRoundedRect(QRectF(244, 184, 74, 4), 2, 2)
        p.end()


class Select(QComboBox):
    """A visible disclosure indicator on both native and Fusion styles."""
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor('#52647a'), 1.5))
        x, y = self.width() - 18, self.height() // 2
        p.drawLine(x - 4, y - 2, x, y + 2)
        p.drawLine(x, y + 2, x + 4, y - 2)
        p.end()


class EditionOption(QRadioButton):
    """A keyboard-accessible radio option with a wrapping description."""
    def __init__(self, title, detail, key):
        super().__init__(title + ('\n' + detail if detail else ''))
        self.title, self.detail, self.key = title, detail, key
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(144)

    def sizeHint(self):
        return QSize(260, 144)

    def hitButton(self, position):
        return self.rect().contains(position)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        selected = self.isChecked()
        p.setBrush(QColor('#edf4ff' if selected else '#f4f8fc' if self.underMouse() else '#ffffff'))
        p.setPen(QPen(QColor('#2466c5' if selected or self.hasFocus() else '#a6b7cb'), 2 if selected or self.hasFocus() else 1))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 9, 9)
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor('#142d48'), 1, Qt.PenStyle.DotLine))
            p.drawRoundedRect(QRectF(self.rect()).adjusted(6, 6, -6, -6), 6, 6)
        p.setPen(QPen(QColor('#2466c5' if selected else '#a6b7cb'), 1.5))
        p.setBrush(QColor('#2466c5' if selected else '#ffffff'))
        p.drawEllipse(QRectF(16, 19, 16, 16))
        if selected:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor('#ffffff'))
            p.drawEllipse(QRectF(21, 24, 6, 6))
        p.setPen(QColor('#182c46'))
        font = self.font()
        font.setBold(True)
        p.setFont(font)
        p.drawText(QRectF(44, 16, self.width()-60, 36), Qt.TextFlag.TextWordWrap, self.title)
        font.setBold(False)
        p.setFont(font)
        p.setPen(QColor('#52647a'))
        p.drawText(QRectF(16, 52, self.width()-32, self.height()-60), Qt.TextFlag.TextWordWrap, self.detail)
        p.end()
