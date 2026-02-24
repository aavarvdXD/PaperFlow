from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QStatusBar, QFileDialog, QMessageBox
)
from PySide6.QtGui import (
    QAction, QIcon, QKeySequence
)
from PySide6.QtCore import Qt, QStandardPaths
from paperFlow.widgets.editor import EditorCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PaperFlow")
        self.setWindowIcon(QIcon("paperFlow/resources/icons/icon.ico"))

        self.zoom = 1.0
        self._current_path = None

        self._init_ui()

    def _init_ui(self):
        # Central Editor
        self.editor = EditorCanvas()
        self.setCentralWidget(self.editor)

        self.create_menu_bar()
        # self.create_tool_bar()
        # self.create_status_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menus
        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        view_menu = menu_bar.addMenu("&View")
        help_menu = menu_bar.addMenu("&Help")

        #Actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.file_new)

        self.open_action = QAction("Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.file_open)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.file_save)

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcuts([
            QKeySequence("Ctrl++"),
            QKeySequence("Ctrl+=")
        ])
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.zoom_reset_action = QAction("Reset Zoom", self)
        self.zoom_reset_action.setShortcut("Ctrl+0")
        self.zoom_reset_action.triggered.connect(self.zoom_reset)

        self.save_as_action = QAction("Save As..", self)
        self.save_as_action.setShortcut("Ctrl+E")
        self.save_as_action.triggered.connect(self.file_save_as)

        # Add actions to File menu
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Add actions to View menu
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addSeparator()
        view_menu.addAction(self.zoom_reset_action)

    def _create_tool_bar(self):
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(True)
        self.addToolBar(Qt.ToolBarArea, self.main_toolbar)

        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.save_action)

        #Add sub toolbars later

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("PaperFlow")

    def zoom_in(self):
        self.editor.zoom_in()

    def zoom_out(self):
        self.editor.zoom_out()

    def zoom_reset(self):
        self.editor.zoom_reset()

    def file_new(self):
        if self.editor.editor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Unsaved changes - PaperFlow",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.editor.editor.clear()
        self.editor.editor.document().setModified(False)
        self._current_path = None
        self.setWindowTitle("PaperFlow")

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "PaperFlow Files (*.pflow);;Text Files (*.txt);;Word Document Files (*.docx);;All Files (*.*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            if path.lower().endswith((".htm", ".html")):
                self.editor.editor.setHtml(data)
            else:
                self.editor.editor.setPlainText(data)
            self.editor.editor.document().setModified(False)
            self._current_path = path
            self.setWindowTitle(f"PaperFlow - {path}")
        except Exception as e:
            QMessageBox.critical(self, "Open Failed", str(e))

    def file_save(self):
        if not self._current_path:
            documents_dir = QStandardPaths.writableLocation(
                QStandardPaths.DocumentsLocation
            )
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                documents_dir,
                "PaperFlow Files (*.pflow);;Text Files (*.txt);;HTML Files (*.html *.htm);;All Files (*.*)"
            )
            if not path:
                return
            if "." not in path.rsplit("\\", 1)[-1]:
                path += ".pflow"
            self._current_path = path
        try:
            if self._current_path.lower().endswith((".htm", ".html")):
                data = self.editor.editor.toHtml()
            else:
                data = self.editor.editor.toPlainText()
            with open(self._current_path, "w", encoding="utf-8") as f:
                f.write(data)
            self.editor.editor.document().setModified(False)
            self.setWindowTitle(f"PaperFlow - {self._current_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    def file_save_as(self):
        documents_dir = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            documents_dir,
            "PaperFlow Files (*.pflow);;Text Files (*.txt);;HTML Files (*.html *.htm);;All Files (*.*)"
        )
        if not path:
            return
        if "." not in path.rsplit("\\", 1)[-1]:
            path += ".pflow"
        self._current_path = path
        self.file_save()
