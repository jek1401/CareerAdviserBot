import telebot
from telebot import types
from utils import quiz

TOKEN = "YOUR TOKEN"

bot = telebot.TeleBot(TOKEN)

# Хранение состояний пользователя: интересы и этапы
user_data = {}

# Команды

@bot.message_handler(commands=['start'])
def start(message):
    """
    Обработчик команды /start. Инициализирует бота для пользователя.
    """
    quiz.create_demo_data()  # Создаем базу, если не создана

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Пройти мини-тест', 'Показать все интересы')
    markup.row('Совет дня', 'Помощь /help')

    user_data[message.from_user.id] = {
        'interests': set(),
        'stage': 'start'
    }

    bot.send_message(
        message.chat.id,
        "Привет! Я Career Adviser Bot. Помогу подобрать профессию по твоим интересам.\n"
        "Выбери действие в меню или напиши команду.",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    """
    Обработчик команды /help. Отправляет пользователю справочную информацию.
    """
    text = (
        "🚀 Команды и функции бота:\n\n"
        "🔹 Пройти мини-тест - выбрать интересы и получить рекомендации профессий\n"
        "🔹 Показать все интересы - список доступных интересов\n"
        "🔹 Совет дня - получите полезный совет для развития карьеры\n"
        "🔹 /help - показать это сообщение\n"
        "🔹 /cancel - отменить текущую операцию\n\n"
        "💡 Также можно просто писать интересы текстом, а я попробую подобрать подходящие профессии."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['cancel'])
def cancel(message):
    """
    Обработчик команды /cancel. Сбрасывает состояние пользователя.
    """
    user_id = message.from_user.id
    user_data[user_id] = {'interests': set(), 'stage': 'start'}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Пройти мини-тест', 'Показать все интересы')
    markup.row('Совет дня', 'Помощь /help')
    
    bot.send_message(
        message.chat.id, 
        "🔄 Операция отменена. Вы в главном меню.", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == 'Показать все интересы')
def show_interests(message):
    """
    Обработчик кнопки 'Показать все интересы'. Отправляет список всех доступных интересов.
    """
    interests = quiz.get_interests()
    formatted_interests = "\n".join(f"• {interest}" for interest in sorted(interests))
    bot.send_message(
        message.chat.id, 
        f"📚 Доступные интересы:\n\n{formatted_interests}",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == 'Совет дня')
def career_tip(message):
    """
    Обработчик кнопки 'Совет дня'. Отправляет случайный карьерный совет.
    """
    tip = quiz.get_career_tip()
    bot.send_message(
        message.chat.id, 
        f"💡 Совет дня:\n\n{tip}",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == 'Пройти мини-тест')
def start_test(message):
    """
    Обработчик кнопки 'Пройти мини-тест'. Начинает процесс выбора интересов.
    """
    # Обновляем данные перед началом теста
    quiz.create_demo_data()
    
    user_id = message.from_user.id
    user_data[user_id] = {'interests': set(), 'stage': 'testing'}

    interests = quiz.get_interests()
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Группируем интересы по 4 в строку для лучшего отображения
    for i in range(0, len(interests), 4):
        row = interests[i:i+4]
        buttons = [
            types.InlineKeyboardButton(
                text=f"{'✅ ' if interest in user_data[user_id]['interests'] else ''}{interest}",
                callback_data=f"interest_{interest}"
            )
            for interest in row
        ]
        markup.add(*buttons)
    
    markup.add(types.InlineKeyboardButton(
        text="🚀 Закончить выбор", 
        callback_data="done"
    ))
    
    bot.send_message(
        message.chat.id,
        "🔍 Выбери свои интересы (можно выбрать несколько):\n\n"
        "• Нажми на интерес, чтобы выбрать/отменить\n"
        "• Нажми '🚀 Закончить выбор', когда готов",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('interest_') or call.data == 'done')
def callback_test(call):
    """
    Обработчик inline-кнопок выбора интересов и завершения выбора.
    """
    user_id = call.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'interests': set(), 'stage': 'start'}

    if call.data == 'done':
        selected = user_data[user_id].get('interests', set())
        if not selected:
            bot.answer_callback_query(call.id, "❌ Вы не выбрали ни одного интереса!")
            return

        professions = quiz.get_professions_by_interests(list(selected))
        if not professions:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="😕 По выбранным интересам профессий не найдено. Попробуйте другие интересы.",
                reply_markup=None
            )
            return

        markup = types.InlineKeyboardMarkup()
        for prof in professions:
            prof_id, title, _, _ = prof
            markup.add(types.InlineKeyboardButton(
                text=f"👨‍💻 {title}", 
                callback_data=f"prof_{prof_id}"
            ))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎯 Вот профессии, подходящие под ваши интересы ({', '.join(user_data[user_id]['interests'])}):",
            reply_markup=markup
        )
        user_data[user_id]['stage'] = 'start'
    else:
        interest = call.data.replace('interest_', '')
        if interest in user_data[user_id]['interests']:
            user_data[user_id]['interests'].remove(interest)
            bot.answer_callback_query(call.id, f"❌ Удален интерес: {interest}")
        else:
            user_data[user_id]['interests'].add(interest)
            bot.answer_callback_query(call.id, f"✅ Добавлен интерес: {interest}")

        # Обновляем клавиатуру с новыми отметками
        interests = quiz.get_interests()
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for i in range(0, len(interests), 4):
            row = interests[i:i+4]
            buttons = [
                types.InlineKeyboardButton(
                    text=f"{'✅ ' if i in user_data[user_id]['interests'] else ''}{i}",
                    callback_data=f"interest_{i}"
                )
                for i in row
            ]
            markup.add(*buttons)
        
        markup.add(types.InlineKeyboardButton(
            text="🚀 Закончить выбор", 
            callback_data="done"
        ))
        
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error updating markup: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('prof_'))
def callback_profession_detail(call):
    """
    Обработчик inline-кнопок с профессиями. Показывает детали о профессии.
    """
    prof_id = int(call.data.replace('prof_', ''))
    prof = quiz.get_profession_by_id(prof_id)
    if prof:
        title, description, education = prof
        text = (
            f"<b>{title}</b>\n\n"
            f"<i>{description}</i>\n\n"
            f"📚 <b>Образование:</b> {education}\n\n"
            f"🔹 Выбери другое действие в меню или /start для возврата"
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode='HTML'
        )
    else:
        bot.answer_callback_query(call.id, "Информация о профессии не найдена.")

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    """
    Обработчик произвольного текстового сообщения. Пытается найти интересы в тексте.
    """
    user_id = message.from_user.id
    text = message.text.lower()
    interests = quiz.get_interests()

    matched = [i for i in interests if i.lower() in text]

    if matched:
        user_data.setdefault(user_id, {'interests': set(), 'stage': 'start'})
        user_data[user_id]['interests'].update(matched)

        professions = quiz.get_professions_by_interests(list(user_data[user_id]['interests']))
        if professions:
            markup = types.InlineKeyboardMarkup()
            for prof in professions:
                prof_id, title, _, _ = prof
                markup.add(types.InlineKeyboardButton(
                    text=f"🔹 {title}", 
                    callback_data=f"prof_{prof_id}"
                ))

            bot.send_message(
                message.chat.id,
                f"🔎 По вашим интересам найдены следующие профессии:",
                reply_markup=markup
            )
        else:
            bot.send_message(
                message.chat.id, 
                "По вашим интересам ничего не найдено. Попробуйте другие ключевые слова."
            )
    else:
        bot.send_message(
            message.chat.id,
            "Не удалось найти интересы в сообщении. Попробуйте /help или /start для помощи."
        )

if __name__ == '__main__':
    print("Бот запущен...")