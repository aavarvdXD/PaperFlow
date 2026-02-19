from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Qt

class mainToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(True)
        self.setFloatable(True)