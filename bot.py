import telebot
import os
from dotenv import load_dotenv
import logging

from info import (
    COOL_STICKER, NOT_UNDERSTAND_MEDIA, NOT_UNDERSTAND_TEXT, SAY_START, SAY_RULES, users, MAIN_MARKUP, ASK_MARKUP,
    HELP_COMMANDS_SEND, SUBJECT_MARKUP, LEVEL_MARKUP
)
from gpt import GPT
from database import add_user, update_subject, update_level, update_answer, update_task

load_dotenv()

token = os.getenv('token')

bot = telebot.TeleBot(token)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


def check_user(uid, message):
    if uid not in users:
        users[uid] = {}
        users[uid]['subject'] = ''
        users[uid]['level'] = ''
        users[uid]['question'] = ''
        users[uid]['answer'] = ''
        add_user('info.db', message.from_user.id, '', '', '', '')


def filter_hello(message):
    return 'hi' in message.text.lower()


def filter_bye(message):
    return 'bye' in message.text.lower()


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:

        uid = message.from_user.id
        bot.send_message(
            message.chat.id,
            f'<b>Hi, {message.chat.first_name}!</b>\n'
            f'{SAY_START}',
            parse_mode='HTML',
            reply_markup=MAIN_MARKUP)
        logging.info("The start command is started")
        check_user(message.from_user.id, message)
    except Exception as e:
        logging.error(f"The start function received an error: {e}")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, f'<b>List of commands:</b>\n'
                                      f'{HELP_COMMANDS_SEND}',
                     parse_mode='HTML',
                     reply_markup=MAIN_MARKUP
                     )
    check_user(message.from_user.id, message)


@bot.message_handler(commands=['configure_gpt'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Choose a subject for which the bot will help you',
                     parse_mode='HTML',
                     reply_markup=SUBJECT_MARKUP
                     )

    bot.register_next_step_handler(message, choice_subject)


def choice_subject(message):
    check_user(message.from_user.id, message)
    uid = message.from_user.id
    global subject
    if message.text == 'Math':
        bot.send_message(message.chat.id, 'Choose the level of explanation',
                         parse_mode='HTML',
                         reply_markup=LEVEL_MARKUP
                         )
        subject = 'math'
        users[uid]['subject'] = message.text
        update_subject('info.db', message.from_user.id, message.text)
        bot.register_next_step_handler(message, choice_level)
    elif message.text == 'Geometry':
        bot.send_message(message.chat.id, 'Choose the level of explanation',
                         parse_mode='HTML',
                         reply_markup=LEVEL_MARKUP
                         )
        subject = 'geometry'
        users[uid]['subject'] = message.text
        update_subject('info.db', message.from_user.id, message.text)
        bot.register_next_step_handler(message, choice_level)
    else:
        bot.send_message(message.chat.id, 'Choose an subject from the list',
                         parse_mode='HTML',
                         reply_markup=ASK_MARKUP
                         )


def choice_level(message):
    global gpt  
    uid = message.from_user.id
    if message.text == 'Beginner':
        level = 'beginner'
        gpt = GPT(subject, level)
        update_level('info.db', message.from_user.id, message.text)
        users[uid]['level'] = message.text
    elif message.text == 'Professional':
        level = 'professional'
        gpt = GPT(subject, level)
        users[uid]['level'] = message.text
        update_level('info.db', message.from_user.id, message.text)
    else:
        bot.send_message(message.chat.id, 'Choose an level from the list',
                         parse_mode='HTML',
                         reply_markup=MAIN_MARKUP
                         )


@bot.message_handler(commands=['ask_gpt'])
def handle_ask_gpt(message):
    uid = message.from_user.id
    check_user(uid, message)
    if users[uid]['subject'] == '' or users[uid]['level'] == '':
        bot.send_message(message.chat.id, 'First, select the subject and level',
                         parse_mode='HTML',
                         reply_markup=MAIN_MARKUP
                         )
    else:
        bot.send_message(message.chat.id, f'{SAY_RULES}',
                         parse_mode='HTML',
                         reply_markup=ASK_MARKUP
                         )
        bot.register_next_step_handler(message, ask_gpt)


def ask_gpt(message):
    logging.info(f"Received text from the user: {message.text}")
    update_task('info.db', message.from_user.id, message.text)
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
            logging.info("there are too many characters in the request")
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
        update_answer('info.db', message.from_user.id, response[1])
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
    try:
       with open("log_file.txt", "rb") as f:
           bot.send_document(message.chat.id, f)
    except:
        bot.send_message(message.chat.id, 'something went wrong')


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
