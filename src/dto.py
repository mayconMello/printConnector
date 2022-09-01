from typing import Dict, List, Union
from pydantic import BaseModel, Field, validator


class PrintDetails(BaseModel):
    server_name: str = Field(alias='pServerName', default=None)
    name: str = Field(alias='pPrinterName', default=None)
    share_name: str = Field(alias='pShareName', default=None)
    port_name: str = Field(alias='pPortName')
    driver_name: str = Field(alias='pDriverName')
    attributes: int = Field(alias='Attributes')
    status: str = Field(alias='Status')
    verbose_name: str = None
    offline: bool = False

    @validator('offline', always=True)
    def set_offline(cls, v, values) -> bool:
        attributes = values.get('attributes')

        return (attributes & 0x00000400) > 10

    @validator('verbose_name', always=True)
    def set_verbose_name(cls, v, values) -> str:
        server_name = values.get('server_name', None)
        driver_name = values.get('driver_name', None)
        if server_name:
            server_name = server_name.replace('\\', '')
            return f'{driver_name} em {server_name}'

        return values.get('name', None)


class PayloadPrint(BaseModel):
    uuid: int = None
    filename: str = None
    content: str = None
    print_name: str = None
    url: str = None
    crop: bool = False


class PayloadResponse(BaseModel):
    error: bool = False
    message: str = None
    payload: Union[List, Dict] = None

    @validator('error', always=True)
    def set_error(cls, v, values):
        message = values.get('message', None)

        return bool(message)
