import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sys
import re
from content import portfolio_data, achievements, hackathons
from ai import get_ai_answer

debug_mode = False
if '--debug' in sys.argv:
    debug_mode = True

bot = telebot.TeleBot("8776750215:AAFj0U6HNOhTQ7KVwViA7K5Gne95NW4ncpE")

def print_debug(message):
    if debug_mode:
        print(f"[{message.from_user.username}] {message.text}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print_debug(message)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Обо мне"), KeyboardButton("Цель"))
    markup.add(KeyboardButton("Путь в IT"), KeyboardButton("Ментор"))
    markup.add(KeyboardButton("Точка А -> Точка Б"), KeyboardButton("Хобби"))
    markup.add(KeyboardButton("Лучшие работы"), KeyboardButton("GitHub"))
    markup.add(KeyboardButton("Достижения"), KeyboardButton("Вайб хакатонов"))
    markup.add(KeyboardButton("Задать вопрос ИИ"))
    
    bot.send_message(message.chat.id, "Привет! Я бот-портфолио. Выбери раздел:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Обо мне")
def about_me(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["about_me"])

@bot.message_handler(func=lambda message: message.text == "Цель")
def goal(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["goal"])

@bot.message_handler(func=lambda message: message.text == "Путь в IT")
def path_in_it(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["path_in_it"])

@bot.message_handler(func=lambda message: message.text == "Ментор")
def mentor(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["mentor"])

@bot.message_handler(func=lambda message: message.text == "Точка А -> Точка Б")
def point_a_b(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["point_a_b"])

@bot.message_handler(func=lambda message: message.text == "Хобби")
def hobbies(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["hobbies"])

@bot.message_handler(func=lambda message: message.text == "Лучшие работы")
def best_works(message):
    print_debug(message)
    
    photo_paths = [p.strip() for p in portfolio_data.get("best_works_photos", "").split(',') if p.strip()]
    
    if not photo_paths:
        bot.send_message(message.chat.id, portfolio_data["best_works"])
        return

    first_photo = True
    for photo_path in photo_paths:
        try:
            with open(photo_path, 'rb') as photo_file:
                if first_photo:
                    bot.send_photo(message.chat.id, photo_file, caption=portfolio_data["best_works"])
                    first_photo = False
                else:
                    bot.send_photo(message.chat.id, photo_file)
        except Exception:
            if first_photo:
                bot.send_message(message.chat.id, f"{portfolio_data['best_works']}\n\n(Фото {photo_path} временно недоступно)")
                first_photo = False

@bot.message_handler(func=lambda message: message.text == "GitHub")
def github(message):
    print_debug(message)
    bot.send_message(message.chat.id, portfolio_data["github_link"])

@bot.message_handler(func=lambda message: message.text == "Достижения")
def show_achievements(message):
    print_debug(message)
    text = "Мои достижения:\n"
    for item in achievements:
        text += f"- {item}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == "Вайб хакатонов")
def show_hackathons(message):
    print_debug(message)
    markup = InlineKeyboardMarkup()
    for index, hack in enumerate(hackathons):
        btn = InlineKeyboardButton(text=hack["name"], callback_data=f"hack_{index}")
        markup.add(btn)
    bot.send_message(message.chat.id, "Выбери хакатон, чтобы посмотреть фото и описание:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('hack_'))
def hackathon_callback(call):
    index = int(call.data.split('_')[1])
    hack = hackathons[index]
    
    photo_paths = [p.strip() for p in hack.get("photo", "").split(',') if p.strip()]
    
    if not photo_paths:
        bot.send_message(call.message.chat.id, f"{hack['name']}\n\n{hack['description']}")
        return

    first_photo = True
    for photo_path in photo_paths:
        try:
            with open(photo_path, 'rb') as photo_file:
                if first_photo:
                    bot.send_photo(call.message.chat.id, photo_file, caption=f"{hack['name']}\n\n{hack['description']}")
                    first_photo = False
                else:
                    bot.send_photo(call.message.chat.id, photo_file)
        except Exception:
            if first_photo:
                bot.send_message(call.message.chat.id, f"{hack['name']}\n\n{hack['description']}\n\n(Фото {photo_path} недоступно)")
                first_photo = False

@bot.message_handler(func=lambda message: message.text == "Задать вопрос ИИ")
def ask_ai_prompt(message):
    print_debug(message)
    bot.send_message(message.chat.id, "Отправь мне любой вопрос про меня, и я постараюсь ответить на него!")

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    print_debug(message)
    question = message.text.strip()
    
    if question.lower().startswith("вопрос:"):
        question = question[7:].strip()
    
    if not re.match(r"^[a-zA-Zа-яА-Я0-9\s\?\,\.\!\-\:]{5,200}$", question):
        bot.send_message(message.chat.id, "Пожалуйста, выбери раздел из меню или задай понятный вопрос (не слишком короткий и без сложных спецсимволов).")
        return
        
    bot.send_message(message.chat.id, "Думаю над ответом...")
    answer = get_ai_answer(question)
    bot.send_message(message.chat.id, answer)

bot.polling(none_stop=True)
