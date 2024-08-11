from PySide6.QtWidgets import QMainWindow, QTextEdit, QStatusBar, QFileDialog, QMessageBox
from PySide6.QtGui import QFont, QAction
from PySide6 import QtWidgets
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bluedoc")

        self.current_file = None

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.textarea = TextArea()
        self.setCentralWidget(self.textarea)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

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

    def open_file(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Open File",
                                                   downloads_folder,
                                                   "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.textarea.setPlainText(file.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        if hasattr(self, 'current_file') and self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.textarea.toPlainText())
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
                    file.write(self.textarea.toPlainText())
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")


class TextArea(QTextEdit):
    def __init__(self):
        super().__init__()

        font = QFont("Times New Roman", 12)
        self.setFont(font)
        self.document().setDefaultFont(font)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
