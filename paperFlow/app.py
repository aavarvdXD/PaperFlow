import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QTimer, Qt, QElapsedTimer
from PySide6.QtGui import QPixmap, QColor
from paperFlow.main_window import MainWindow

STYLE_SHEET = """
    /* Base (avoid styling QMenuBar here) */
    QWidget {
        color: #1f1f1f;
        background: #f2f2f2;
        font-family: "Segoe UI", "Inter", "Arial";
    }
    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 8px 4px 8px 4px;
    }
    QScrollBar::handle:vertical {
        background: #c6c6c6;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #b0b0b0;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: transparent;
    }

    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 4px 8px 4px 8px;
    }
    QScrollBar::handle:horizontal {
        background: #c6c6c6;
        min-width: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #b0b0b0;
    }
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: transparent;
    }
"""

SPLASH_IMAGE_PATH = r"paperFlow/resources/images/splash(1).png"

def run():
    app = QApplication(sys.argv)

    timer = QElapsedTimer()
    timer.start()

    splash_pix = QPixmap(SPLASH_IMAGE_PATH)
    if splash_pix.isNull():
        splash_pix = QPixmap(520, 320)
        splash_pix.fill(QColor("#ffffff"))
    splash = QSplashScreen(splash_pix)
    splash.showMessage(
        "Loading PaperFlow...",
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        QColor("#5a5a5a")
    )
    splash.show()
    app.processEvents()

    window = MainWindow()

    def show_main():
        window.showMaximized()
        app.setStyleSheet(STYLE_SHEET)
        splash.finish(window)

    remaining = max(2000 - timer.elapsed(), 0)
    QTimer.singleShot(remaining, show_main)

    sys.exit(app.exec())