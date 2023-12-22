from aiogram.filters import Filter
from aiogram.types import Message


class Text(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text is not None


class Document(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.document is not None
