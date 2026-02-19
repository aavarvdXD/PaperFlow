from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QScrollArea
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QTextCursor
import math


class _PageSurface(QWidget):
    """
    A widget that draws white page rectangles on a gray background.
    A QTextEdit sits on top with transparent background.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the text editor
        self.editor = QTextEdit(self)
        self.editor.setAcceptRichText(True)
        self.editor.setFont(QFont("Times New Roman", 12))
        self.editor.setFrameStyle(QTextEdit.Shape.NoFrame)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Page metrics
        dpi_x = self.logicalDpiX()
        dpi_y = self.logicalDpiY()
        self._page_width = int(dpi_x * 8.5)   # 8.5 inches
        self._page_height = int(dpi_y * 11)    # 11 inches
        self._page_gap = int(dpi_y * 0.4)      # 0.4 inch gap between pages

        # Margins (1 inch)
        self._margin_side = int(dpi_x * 1.0)
        self._margin_top = int(dpi_y * 1.0)
        self._margin_bottom = int(dpi_y * 1.0)

        self._page_count = 1

        # Style the editor
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: #1f1f1f;
                selection-background-color: #cfe3ff;
                selection-color: #1f1f1f;
                padding: {self._margin_top}px {self._margin_side}px;
            }}
        """)

        # Set fixed width
        self.setFixedWidth(self._page_width)
        self.editor.setFixedWidth(self._page_width)

        # Connect signals
        self.editor.document().contentsChanged.connect(self._on_content_changed)

        # Initial size
        self._update_size()

    def _on_content_changed(self):
        QTimer.singleShot(0, self._update_size)

    def _update_size(self):
        # Get document height
        doc = self.editor.document()
        doc_height = doc.size().height()

        # Calculate pages needed (at minimum 1 page)
        usable_height = self._page_height - self._margin_top - self._margin_bottom
        if usable_height <= 0:
            usable_height = self._page_height

        # Simple calculation: how many pages fit the content
        self._page_count = max(1, math.ceil(doc_height / self._page_height))

        # Total height = pages * page_height + (pages-1) * gap
        total_height = (self._page_count * self._page_height) + ((self._page_count - 1) * self._page_gap)

        # Set minimum height
        self.setMinimumHeight(total_height)
        self.editor.setFixedHeight(total_height)

        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.editor.setGeometry(0, 0, self.width(), self.height())

    def paintEvent(self, event):
        painter = QPainter(self)

        # Gray background
        painter.fillRect(self.rect(), QColor("#d4d4d4"))

        # Draw each page
        for i in range(self._page_count):
            y = i * (self._page_height + self._page_gap)

            # Shadow
            shadow_rect = self.rect()
            shadow_rect.setTop(int(y) + 4)
            shadow_rect.setHeight(self._page_height)
            shadow_rect.setLeft(4)
            shadow_rect.setWidth(self._page_width)
            painter.fillRect(shadow_rect, QColor(0, 0, 0, 40))

            # White page
            page_rect = self.rect()
            page_rect.setTop(int(y))
            page_rect.setHeight(self._page_height)
            painter.fillRect(page_rect, QColor("#ffffff"))

            # Border
            painter.setPen(QPen(QColor("#c0c0c0"), 1))
            painter.drawRect(page_rect.adjusted(0, 0, -1, -1))

        painter.end()

    def zoom_in(self):
        self.editor.zoomIn(1)
        self._update_size()

    def zoom_out(self):
        self.editor.zoomOut(1)
        self._update_size()


class EditorCanvas(QWidget):
    """
    The main editor widget containing a scrollable page surface.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._zoom_steps = 0

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("QScrollArea { background: #d4d4d4; }")

        # Container to center the page
        self._container = QWidget()
        self._container.setStyleSheet("background: #d4d4d4;")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Page surface with editor
        self._page_surface = _PageSurface()
        self.editor = self._page_surface.editor  # Expose for main_window

        container_layout.addWidget(self._page_surface)

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        self.setMinimumSize(900, 650)

        # Auto-scroll to cursor
        self.editor.cursorPositionChanged.connect(self._ensure_cursor_visible)

    def zoom_in(self):
        self._zoom_steps += 1
        self._page_surface.zoom_in()

    def zoom_out(self):
        self._zoom_steps -= 1
        self._page_surface.zoom_out()

    def zoom_reset(self):
        if self._zoom_steps > 0:
            for _ in range(self._zoom_steps):
                self._page_surface.zoom_out()
        elif self._zoom_steps < 0:
            for _ in range(-self._zoom_steps):
                self._page_surface.zoom_in()
        self._zoom_steps = 0

    def _ensure_cursor_visible(self):
        rect = self.editor.cursorRect()
        # Map cursor position to container coordinates
        pt = self._page_surface.mapTo(self._container, rect.center())
        self._scroll.ensureVisible(int(pt.x()), int(pt.y()), 50, 100)
