import asyncio
import logging
import os
import sys
from typing import Any

import aiofiles
import openai
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from dotenv import load_dotenv
import tempfile
from python import Filters as ContentTypesFilter

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
openai.api_type = "azure"
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://deep-azure.openai.azure.com/"
openai.api_version = "2023-06-01-preview"


async def send_or_split_message(message, text):
    text_file = BufferedInputFile(bytes(text, 'utf-8'), filename="file.txt")
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            text_chunk = text[i:i + 4096]
            await message.answer(text_chunk, reply_to_message_id=message.message_id)
    else:
        await message.answer(text, reply_to_message_id=message.message_id)
    await message.answer_document(text_file, reply_to_message_id=message.message_id)


async def get_openai_completion(prompt):
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            deployment_id="deep-new",
            model="gpt-4-128k",
            messages=[{"role": 'user', "content": prompt}]
        )

        return chat_completion["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenAI completion error: {e}")
        raise


router = Router(name=__name__)


@router.message(ContentTypesFilter.Text())
async def handle_text(message: Message, state: FSMContext) -> Any:
    try:

        logger.info(f"---------\nReceived message: {message}")
        context_text = message.reply_to_message.text if message.reply_to_message else ""
        document_file = message.reply_to_message.document if message.reply_to_message and message.reply_to_message.document else None

        if document_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                await bot.download(document_file, temp_file.name)

            async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
                context_text += await file.read()
        answer = await get_openai_completion(f"Context:\n{context_text}Prompt:\n{message.text}")
        await send_or_split_message(message, answer)
    except Exception as e:
        logger.error(e)


dp = Dispatcher()

TOKEN = os.getenv("TELEGRAM_TOKEN")
# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG)
    httpx_logger.propagate = True
    asyncio.run(main())
