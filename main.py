from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStatusBar, QFileDialog, QMessageBox,
                               QToolBar, QComboBox)
from PySide6.QtGui import (QFont, QAction, QIcon, QActionGroup, QTextDocument, QDragEnterEvent, QDropEvent, QTextCursor,
                           QDesktopServices)
from PySide6.QtCore import Qt, QMimeData, QUrl, QPointF
import sys
import os

FONT_SIZES = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 36, 48, 64, 72, 96, 144, 288]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bluedoc")

        self.current_file = None

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.textarea = TextArea()
        self.setCentralWidget(self.textarea)

        format_toolbar = FormatBar(self.textarea)
        self.addToolBar(format_toolbar)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # FILE MENU
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As", self)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        save_as_action.triggered.connect(self.save_as_file)

        # EDIT MENU
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.textarea.undo)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.textarea.redo)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

    def open_file(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Open File",
                                                   downloads_folder,
                                                   "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.textarea.setHtml(file.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        if hasattr(self, 'current_file') and self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.textarea.toHtml())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_name = os.path.join(downloads_folder, 'untitled.txt')
        file_path, _ = QFileDialog.getSaveFileName(self,
                                                   "Save File As",
                                                   file_name,
                                                   "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.textarea.toHtml())
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")


class FormatBar(QToolBar):
    def __init__(self, textarea):
        super().__init__()

        bold_action = QAction(QIcon.fromTheme("format-text-bold"), "Bold", self)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(lambda x: textarea.setFontWeight(QFont.Weight.Bold if x else QFont.Weight.Normal))
        self.addAction(bold_action)

        italic_action = QAction(QIcon.fromTheme("format-text-italic"), "Italic", self)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(textarea.setFontItalic)
        self.addAction(italic_action)

        font_size = QComboBox()
        font_size.addItems([str(s) for s in FONT_SIZES])
        font_size.currentIndexChanged.connect(
            lambda s: textarea.setFontPointSize(FONT_SIZES[s])
        )
        self.addWidget(font_size)

        align_left_action = QAction(QIcon.fromTheme("format-justify-left"), "Align left", self)
        align_left_action.setCheckable(True)
        align_left_action.triggered.connect(
            lambda: textarea.setAlignment(Qt.AlignmentFlag.AlignLeft)
        )
        self.addAction(align_left_action)

        align_center_action = QAction(QIcon.fromTheme("format-justify-center"), "Align center", self)
        align_center_action.setCheckable(True)
        align_center_action.triggered.connect(
            lambda: textarea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        )
        self.addAction(align_center_action)

        align_right_action = QAction(QIcon.fromTheme("format-justify-right"), "Align right", self)
        align_right_action.setCheckable(True)
        align_right_action.triggered.connect(
            lambda: textarea.setAlignment(Qt.AlignmentFlag.AlignRight)
        )
        self.addAction(align_right_action)

        alignment_group = QActionGroup(self)
        alignment_group.setExclusive(True)
        alignment_group.addAction(align_left_action)
        alignment_group.addAction(align_center_action)
        alignment_group.addAction(align_right_action)


class TextArea(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        font = QFont("Times New Roman", 12)
        self.setFont(font)
        self.document().setDefaultFont(font)

        self.cursor = self.textCursor()
        self.setMouseTracking(True)

        self.resizing_image = False
        self.image_format = None
        self.original_width = None
        self.original_height = None
        self.start_pos = QPointF().toPoint()

    def canInsertFromMimeData(self, source):
        if source.hasImage():
            return True
        else:
            return super(TextArea, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            if QUrl(text).isValid() and text.startswith(("http://", "https://")):
                self.cursor.insertHtml(f'<a href="{text}">{text}</a>')
            else:
                self.cursor.insertText(text, self.currentCharFormat())
        elif source.hasImage():
            image = source.imageData()
            document = self.document()
            document.addResource(QTextDocument.ResourceType.ImageResource, QUrl("inserted_image"), image)
            self.cursor.insertImage("inserted_image")
        else:
            super().insertFromMimeData(source)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()

        if mime_data.hasImage():
            self.cursor.insertImage(mime_data.imageData())
        elif mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    image_path = url.toLocalFile()
                    self.cursor.insertImage(image_path)

    # CLICK-AND-DROP IMAGE RESIZE
    def mousePressEvent(self, event):
        # CHECK IF AN IMAGE IS CLICKED
        cursor = self.cursorForPosition(event.position().toPoint())
        self.image_format = cursor.charFormat().toImageFormat()

        if not self.image_format.isValid():
            super().mousePressEvent(event)
            return

        self.resizing_image = True
        self.original_width = self.image_format.width()
        self.original_height = self.image_format.height()
        self.start_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.resizing_image:
            # CALCULATE THE NEW SIZE BASED ON THE MOUSE MOVEMENT
            delta = event.position() - self.start_pos
            new_width = max(1, self.original_width + delta.x())
            new_height = max(1, self.original_height + delta.y())

            # APPLY THE NEW SIZE
            self.image_format.setWidth(new_width)
            self.image_format.setHeight(new_height)

            # UPDATE THE CURSOR'S CHAR FORMAT WITH THE RESIZED IMAGE
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.setCharFormat(self.image_format)

        else:
            super().mouseMoveEvent(event)

        # Change cursor when hovering over a link
        anchor = self.anchorAt(event.position().toPoint())
        if anchor:
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.IBeamCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing_image:
            self.resizing_image = False
        else:
            super().mouseReleaseEvent(event)

        anchor = self.anchorAt(event.position().toPoint())
        if anchor:
            # IF THERE'S AN ANCHOR, OPEN THE LINK IN THE DEFAULT WEB BROWSER
            QDesktopServices.openUrl(QUrl(anchor))
        else:
            # IF NO LINK WAS CLICKED, CALL THE BASE CLASS IMPLEMENTATION
            super().mouseReleaseEvent(event)


if __name__ == "__main__":
    app = QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
