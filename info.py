from telebot.types import ReplyKeyboardMarkup, KeyboardButton

COOL_STICKER = ("Cool sticker, but still use the bot for its intended purpose\n"
                "Enter /help")

NOT_UNDERSTAND_TEXT = "Sorry, I didn't understand you, please enter the command or /help to view the list of commands"

NOT_UNDERSTAND_MEDIA = ("Unfortunately, I'm just a bot and I can't listen and watch all this\n"
                        "Enter the command /help")

SAY_START = "This is a gpt bot. He can just chat with you or help you in some way. To ask gpt, enter /ask_gpt"

SAY_RULES = ("You can ask me anything you want.\n"
             "-If you write continue, I will continue to explain the task\n"
             "-To end the dialogue, write the end_question\n"
             "if I don't answer you, then the answer is over"
             "Enter your question with the next message")
COMMANDS = {

    '/start': 'Write /start to make the bot work',

    '/help': 'Write /help to display a list of commands',

    '/ask_gpt': 'Write /ask_gpt to ask a neural network question',

    'continue': 'Write <b>continue</b> in order to continue the explanation of the question',

    'end_question': 'Write <b>end_question</b> in order to complete the explanation of the question'

}

users = {}


def make_keyboard(items):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    for item in items:
        markup.add(KeyboardButton(item))

    return markup


MAIN_MARKUP = make_keyboard(['/start', '/help', '/ask_gpt', '/configure_gpt'])
ASK_MARKUP = make_keyboard(['continue', 'end_question'])
HELP_COMMANDS_SEND = '\n'.join(COMMANDS.values())
SUBJECT_MARKUP = make_keyboard(['Math', "Geometry"])
LEVEL_MARKUP = make_keyboard(["Beginner", "Professional"])