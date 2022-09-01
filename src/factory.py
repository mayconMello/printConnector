import base64
import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import win32api
import win32print
from pdfCropMargins import crop
from zebra import Zebra

from src.dto import PayloadPrint, PrintDetails
from src.handle import BaseClass, HandlerFactoryEvents as hfv

BASE_PATH = Path(__file__).resolve().parent.parent
SUMATRA_PDF = os.path.join(BASE_PATH, 'bin', 'sumatra-pdf.exe')


@hfv.register_handler('printers')
class GetInstalledPrinters(BaseClass):
    def execute(self):
        printers = []
        for enum in [
            win32print.PRINTER_ENUM_LOCAL,
            win32print.PRINTER_ENUM_CONNECTIONS
        ]:
            for enum_printer in win32print.EnumPrinters(enum, None, 2):
                details = PrintDetails(**enum_printer)
                printers.append(details.dict())

        return printers


class SendPrinterError(Exception):
    pass


@hfv.register_handler('printer')
class SendPrinter(BaseClass):
    def __init__(self, payload):
        super().__init__(payload)

        self.payload = PayloadPrint(
            **payload
        )
        self.filename = self.payload.filename
        self.path = None

        if self.filename:
            self.filename = str(Path(
                self.payload.filename
            ).resolve())

            self.path = Path(
                self.filename
            ).resolve().parent

    @property
    def temp_path(self):
        dirpath = os.path.join(BASE_PATH, 'tmp')

        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)

        return dirpath

    def remove_file(self):
        os.remove(self.filename)

    def printer_zebra(self):
        z = Zebra(self.payload.print_name)
        with open(self.filename, 'r') as doc:
            content = str(doc.read())
            z.output(content)

    def printer_normal(self):
        command = f'''
            -exit-on-print 
            -print-to "{self.payload.print_name}" 
            "{self.filename}" 
            -zoom "fit page"
            -print-settings "fit,bin=1"
        '''
        win32api.ShellExecute(
            1,
            'open',
            SUMATRA_PDF,
            command,
            '.',
            1
        )

    def crop_pdf(self):
        path = Path(self.filename).resolve().parent
        croped_filename = os.path.join(
            path, f'c{os.path.basename(self.filename)}')
        crop(
            ["-p4", "100", "10", "10", "20", '-pdl',
                self.filename, '-o', croped_filename
            ])

        self.remove_file()
        self.filename = croped_filename

    def save_file_by_url(self):
        filename = os.path.basename(
            urlparse(self.payload.url).path
        )

        self.filename = os.path.join(
            self.temp_path,
            filename
        )

        response = urlopen(self.payload.url)

        content = response.read()
        with open(self.filename, 'wb') as document:
            document.write(content)

    def save_file_base64(self):
        self.filename = os.path.join(
            self.temp_path,
            self.filename
        )
        _, content = self.payload.content.split(',')

        with open(self.filename, "wb") as f:
            f.write(
                base64.b64decode(content)
            )

    def save_file(self):
        if self.payload.url:
            return self.save_file_by_url()

        return self.save_file_base64()

    def execute(self):
        handle = win32print.OpenPrinter(
            self.payload.print_name
        )

        details = win32print.GetPrinter(handle, 2)
        print_details = PrintDetails(**details)

        if print_details.offline:
            raise SendPrinterError(
                f'A impressora '
                f'{print_details.verbose_name} '
                f'está offline'
            )

        self.save_file()

        crop_file = (
            self.filename.endswith('.pdf') and
            self.payload.crop
        )
        if crop_file:
            self.crop_pdf()

        logging.info(
            f'Printer {self.payload.filename} '
            f'in {self.payload.print_name}'
        )

        if self.filename.endswith(('.zpl',)):
            self.printer_zebra()

            return

        self.printer_normal()

        win32print.ClosePrinter(handle)

        self.payload.content = None

        return self.payload.dict()
