import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv
import logging

from info import COMMANDS, COOL_STICKER, NOT_UNDERSTAND_MEDIA, NOT_UNDERSTAND_TEXT, SAY_START
from gpt import GPT

load_dotenv()

token = os.getenv('token')

bot = telebot.TeleBot(token)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

gpt = GPT(system_content="You are a friendly nice helper")


def filter_hello(message):
    return 'hi' in message.text.lower()


def filter_bye(message):
    return 'bye' in message.text.lower()


def make_keyboard(items):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    for item in items:
        markup.add(KeyboardButton(item))

    return markup


MAIN_MARKUP = make_keyboard(['/start', '/help', '/ask_gpt'])
ASK_MARKUP = make_keyboard(['continue', 'end_question'])
help_commands_send = '\n'.join(COMMANDS.values())


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.send_message(
            message.chat.id,
            f'<b>Hi, {message.chat.first_name}!</b>\n'
            f'{SAY_START}',
            parse_mode='HTML',
            reply_markup=MAIN_MARKUP)
        logging.info("The start command is started")
    except Exception as e:
        logging.error(f"The start function received an error: {e}")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, f'<b>List of commands:</b>\n'
                                      f'{help_commands_send}',
                     parse_mode='HTML',
                     reply_markup=MAIN_MARKUP
                     )


@bot.message_handler(commands=['ask_gpt'])
def handle_help(message):
    bot.send_message(message.chat.id, "You can ask me anything you want.\n"
                                      "-If you write continue, I will continue to explain the task\n"
                                      "-To end the dialogue, write the end_question\n"
                                      "if I don't answer you, then the answer is over"
                                      "Enter your question with the next message",
                     parse_mode='HTML',
                     reply_markup=ASK_MARKUP
                     )
    bot.register_next_step_handler(message, ask_gpt)


def ask_gpt(message):
    logging.info(f"Received text from the user: {message.text}")

    try:
        if message.content_type != "text":
            logging.info("A non-text message was received")
            bot.send_message(message.chat.id, "Send prompt by text message",
                             parse_mode='HTML',
                             reply_markup=ASK_MARKUP
                             )
            bot.register_next_step_handler(message, ask_gpt)
            return

        request_tokens = gpt.count_tokens(message.text)
        if request_tokens > gpt.MAX_TOKENS:
            bot.send_message(message.chat.id, "The request does not match the number of tokens.\n"
                                              "Fix the query: ",
                             parse_mode='HTML',
                             reply_markup=ASK_MARKUP
                             )
            logging.info('there are too many tokens in the request')
            bot.register_next_step_handler(message, ask_gpt)
            return

        if message.text.lower() == 'end_question':
            end_q(message)
            return

        if message.text.lower() != 'continue':
            gpt.clear_history()

        json = gpt.make_promt(message.text)
        resp = gpt.send_request(json)
        response = gpt.process_resp(bot, message, resp)

        if not response[0]:
            bot.send_message(message.chat.id, "The request could not be completed...",
                             parse_mode='HTML',
                             reply_markup=ASK_MARKUP
                             )
        bot.send_message(message.chat.id, response[1],
                         parse_mode='HTML',
                         reply_markup=ASK_MARKUP
                         )
        bot.register_next_step_handler(message, ask_gpt)
        return
    except:
        logging.error("Something went wrong with question")
        bot.register_next_step_handler(message, ask_gpt)


def end_q(message):
    bot.send_message(message.chat.id, "The issue has been resolved",
                     parse_mode='HTML',
                     reply_markup=MAIN_MARKUP
                     )


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['text'], func=filter_hello)
def say_hello(message):
    bot.send_message(message.chat.id, "Hi!",

                     reply_markup=MAIN_MARKUP)


@bot.message_handler(content_types=['text'], func=filter_bye)
def say_goodbye(message):
    bot.send_message(message.chat.id, "Bye!",

                     reply_markup=MAIN_MARKUP)


@bot.message_handler(content_types=['sticker'])
def sticker_answer(message):
    bot.send_message(message.chat.id, f"{COOL_STICKER}",

                     reply_markup=MAIN_MARKUP)


@bot.message_handler(content_types=['text'])
def text_answer(message):
    bot.send_message(message.chat.id,

                     f"{NOT_UNDERSTAND_TEXT}",

                     reply_markup=MAIN_MARKUP)


@bot.message_handler(content_types=['audio', 'video', 'voice', 'photo', 'document'])
def media_answer(message):
    bot.send_message(message.chat.id, f"{NOT_UNDERSTAND_MEDIA}",

                     reply_markup=MAIN_MARKUP)


bot.infinity_polling()
