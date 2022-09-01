import json
import logging

from PyQt5 import QtCore, QtNetwork, QtWebSockets

from src.dto import PayloadResponse
from src.factory import SendPrinterError
from src.handle import HandlerFactoryEvents


def response(message=None, payload=None):
    payload = PayloadResponse(
        message=message,
        payload=payload
    )

    return payload.dict()


def handler_websocket_events(message):
    try:
        data = json.loads(message)
        event = data.get('event')

        payload = data.get('payload', {})

        handler = HandlerFactoryEvents.get_handler(
            event
        )
        payload = handler(payload).execute()
        return response(
            payload=payload,
            message=None
        )

    except SendPrinterError as error:
        logging.error(f'Send Printer Error: {error}')
        return response(message=error)

    except Exception as error:
        logging.error(
            f"Excepition Error: {error}"
        )

        return response(
            message='Ocorreu na comunicação com o conector'
        )


class WebsocketServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.clients = []

        logging.info(
            f"server name: {parent.serverName()}"
        )

        self.server = QtWebSockets.QWebSocketServer(
            parent.serverName(), parent.secureMode(), parent)
        if self.server.listen(
            QtNetwork.QHostAddress.LocalHost,
            50001
        ):
            logging.info(
                f'Listening: {self.server.serverName()}:'
                f'{self.server.serverAddress().toString()}:'
                f'{str(self.server.serverPort())}'
            )
        else:
            logging.error(
                'Could not start server on port 50001'
            )
        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
        self.clientConnection = None

    def onAcceptError(accept_error):
        logging.warning(f"Accept Error: {accept_error}")

    def onNewConnection(self):
        logging.info("On New Connection")
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(
            self.processTextMessage)

        self.clientConnection.disconnected.connect(
            self.socketDisconnected
        )

        logging.info("New Client Connected")
        self.clients.append(self.clientConnection)

    def processTextMessage(self, message):
        message = handler_websocket_events(message)
        self.clientConnection.sendTextMessage(
            json.dumps(message)
        )

    def socketDisconnected(self):
        logging.info("Client Socket Disconected")
        if not self.clientConnection:
            return

        if self.clientConnection not in self.clients:
            return

        self.clients.remove(self.clientConnection)
        self.clientConnection.deleteLater()
