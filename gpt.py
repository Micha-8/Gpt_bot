import requests
from transformers import AutoTokenizer
import telebot


class GPT:
    def __init__(self, system_content):
        self.system_content = system_content
        self.URL = 'http://localhost:1234/v1/chat/completions'
        self.HEADERS = {"Content-Type": "application/json"}  # точно не знаю, но может что-то надо в env?
        self.MAX_TOKENS = 2048
        self.TEMPERATURE = 0.3
        self.assistant_content = "Let's solve the task step by step: "

    # Подсчитываем количество токенов в промте
    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        return len(tokenizer.encode(prompt))

    # Проверка ответа на возможные ошибки и его обработка
    def process_resp(self, bot, message, response) -> [bool, str]:
        # Проверка статус кода
        if response.status_code != 200:
            self.clear_history()
            return False, f"Error: {response.status_code}"

        # Проверка json
        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Error with JSON"

        # Проверка сообщения об ошибке
        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            return False, f"Error: {full_response}"

        # Результат
        result = full_response['choices'][0]['message']['content']

        # Пустой результат == объяснение закончено
        if result == "":
            self.clear_history()
            bot.send_message(message.chat.id, response[1])

        # Сохраняем сообщение в историю
        self.save_history(result)
        return True, self.assistant_content

    # Формирование промта
    def make_promt(self, user_request):
        json = {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": self.assistant_content},
            ],
            "temperature": self.TEMPERATURE,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    # Сохраняем историю общения
    def save_history(self, content_response):
        # Твой код ниже
        self.assistant_content += content_response

    # Очистка истории общения
    def clear_history(self):
        self.assistant_content = "Let's solve the task step by step: "  # код из веба(а почему бы и нет?)
