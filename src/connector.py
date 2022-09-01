import json
import logging

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
        logging.error(f"Excepition Error: {error}")

        return response(
            message='Ocorreu na comunicação com o conector'
        )
