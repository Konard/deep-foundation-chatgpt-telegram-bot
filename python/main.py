import asyncio
import logging
import os
import sys
import traceback

import aiofiles
import httpx
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
import tempfile

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
openai.api_type = "azure"
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://deep-azure.openai.azure.com/"
openai.api_version = "2023-06-01-preview"


async def get_openai_completion(prompt):
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            deployment_id="deep-new",
            model="gpt-4",
            messages=[{"role": 'user', "content": prompt}]
        )

        return chat_completion["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenAI completion error: {e}")
        raise


dp = Dispatcher()

TOKEN = os.getenv("TELEGRAM_TOKEN")
# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    logger.info(f"---------\nReceived message: {message}")
    if message.text is not None:
        if message.reply_to_message is not None:
            if message.reply_to_message.document is not None:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    await bot.download(message.reply_to_message.document, temp_file.name)
                    async with aiofiles.open(temp_file.name, 'r', encoding='utf-8') as file:
                        # Read the content of the file
                        text = await file.read()
                promt = "Context: \n" + text + "Promt:\n" + message.text
                answer = await get_openai_completion(promt)
                await message.answer(answer, reply_to_message_id=message.message_id)
                text_file = BufferedInputFile(bytes(answer, 'utf-8'), filename="file.txt")
                await message.answer_document(text_file, reply_to_message_id=message.message_id)
            else:
                promt = "Context\n" + message.reply_to_message.text + "Promt:\n" + message.text
                answer = await get_openai_completion(promt)
                await message.answer(answer, reply_to_message_id=message.message_id)
                text_file = BufferedInputFile(bytes(answer, 'utf-8'), filename="file.txt")
                await message.answer_document(text_file, reply_to_message_id=message.message_id)
        else:
            promt = "Promt:\n" + message.text
            answer = await get_openai_completion(promt)
            await message.answer(answer, reply_to_message_id=message.message_id)
            text_file = BufferedInputFile(bytes(answer, 'utf-8'), filename="file.txt")
            await message.answer_document(text_file, reply_to_message_id=message.message_id)
    try:
        # Send a copy of the received message
        logger.info(f"---------\nReceived message: {message}")
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        logger.info(f"---------\nReceived message: {message.to_python()}")


async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG)
    httpx_logger.propagate = True
    asyncio.run(main())
