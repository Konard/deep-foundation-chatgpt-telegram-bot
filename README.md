# telegram-gpt-bot

Перед началом работы убедитесь, что у вас установлены Docker и Python, а также что вы создали бота в Telegram.

1. **Клонирование репозитория**
    ```bash
    git clone https://github.com/deep-foundation/chatpgt-telegram-bot 
    ```

2. **Вход в папку с кодом**
    ```bash
    cd .\chatpgt-telegram-bot\python\
    ```

3. **Настройка переменных окружения**
    После входа в папку с кодом, вам нужно будет настроить переменные окружения. Для этого создайте файл `.env`. В этом файле вы можете изменить значения следующим образом:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    TELEGRAM_TOKEN=your_telegram_bot_token
    ```

4. **Сборка Docker образа**
    ```bash
    docker build -t <yourimagename> .
    ```

5. **Запуск Docker контейнера**
    ```bash
    docker run -p <port> --name <yourcontainername> <yourimagename>
    ```
