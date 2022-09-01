import logging
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QPushButton, QVBoxLayout


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class QDialogLogs(QDialog, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(640, 480)
        self.setWindowTitle('Print Connector - Show Logs')
        self.setWindowIcon(QIcon(os.path.join('assets', 'logo.ico')))

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        lot_text_box = QTextEditLogger(self)

        lot_text_box.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(lot_text_box)
        logging.getLogger().setLevel(logging.DEBUG)

        self._button = QPushButton(self)
        self._button.setText('Fechar')

        layout = QVBoxLayout()
        layout.addWidget(lot_text_box.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)

        self._button.clicked.connect(self.hide)

    def closeEvent(self, a0) -> None:
        self.hide()
