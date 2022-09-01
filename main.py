import os

from PyQt5 import QtWebSockets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, 
    QMenu,
    QSystemTrayIcon
)

from src.gui import QDialogLogs
from src.sever import WebsocketServer

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = QDialogLogs()

    icon = QSystemTrayIcon(
        QIcon(os.path.join('assets', 'logo.ico')),
        parent=app
    )
    icon.setToolTip('Print Connector')
    icon.show()

    menu = QMenu()
    exit_action = menu.addAction('Exit')
    exit_action.triggered.connect(app.quit)

    show_loggers = menu.addAction('Ver Logs')
    show_loggers.triggered.connect(dialog.show)

    serverObject = QtWebSockets.QWebSocketServer(
        'Socket Print Connector',
        QtWebSockets.QWebSocketServer.NonSecureMode
    )
    server = WebsocketServer(serverObject)
    serverObject.closed.connect(app.quit)

    icon.setContextMenu(menu)
    sys.exit(app.exec_())
