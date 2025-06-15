import telebot
from telebot import types
from utils import quiz

TOKEN = "YOUR TOKEN"

bot = telebot.TeleBot(TOKEN)

# Хранение состояний пользователя
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    quiz.create_demo_data()
    
    user_data[message.from_user.id] = {
        'interests': set(),
        'stage': 'waiting_age',
        'age': None
    }

    bot.send_message(
        message.chat.id,
        "Привет! Я Career Adviser Bot. Помогу подобрать профессию по твоим интересам.\n"
        "Для начала, сколько тебе лет? (Введи число от 10 до 100)",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: user_data.get(message.from_user.id, {}).get('stage') == 'waiting_age')
def handle_age(message):
    """Обработчик ввода возраста"""
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            bot.send_message(message.chat.id, "Пожалуйста, введите реальный возраст (от 10 до 100 лет).")
            return
        
        user_id = message.from_user.id
        user_data[user_id]['age'] = age
        user_data[user_id]['stage'] = 'start'
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Пройти мини-тест', 'Показать все интересы')
        markup.row('Совет дня', 'Помощь /help')
        
        bot.send_message(
            message.chat.id,
            f"Отлично! Теперь я знаю, что тебе {age} лет. Выбери действие в меню.",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите возраст числом (например, 16 или 25).")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    """Обработчик команды /help"""
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
    """Обработчик команды /cancel"""
    user_id = message.from_user.id
    user_data[user_id] = {'interests': set(), 'stage': 'start', 'age': user_data.get(user_id, {}).get('age')}
    
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
    """Показать все доступные интересы"""
    interests = quiz.get_interests()
    formatted_interests = "\n".join(f"• {interest}" for interest in sorted(interests))
    bot.send_message(
        message.chat.id, 
        f"📚 Доступные интересы:\n\n{formatted_interests}",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == 'Совет дня')
def career_tip(message):
    """Обработчик кнопки 'Совет дня'"""
    tip = quiz.get_career_tip()
    bot.send_message(
        message.chat.id, 
        f"💡 Совет дня:\n\n{tip}",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == 'Пройти мини-тест')
def start_test(message):
    """Начало мини-теста по выбору интересов"""
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'interests': set(), 'stage': 'testing', 'age': None}
    else:
        user_data[user_id]['stage'] = 'testing'

    interests = quiz.get_interests()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('interest_'))
def handle_interest_click(call):
    """Обработчик клика по интересу"""
    user_id = call.from_user.id
    if user_id not in user_data:
        bot.answer_callback_query(call.id, "Начните с команды /start")
        return

    interest = call.data.replace('interest_', '')
    
    if interest in user_data[user_id]['interests']:
        user_data[user_id]['interests'].remove(interest)
        bot.answer_callback_query(call.id, f"❌ Удален интерес: {interest}")
    else:
        user_data[user_id]['interests'].add(interest)
        bot.answer_callback_query(call.id, f"✅ Добавлен интерес: {interest}")

    # Обновляем клавиатуру
    interests = quiz.get_interests()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
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
    
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка при обновлении клавиатуры: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'done')
def handle_done(call):
    """Обработчик завершения выбора интересов."""
    user_id = call.from_user.id
    if user_id not in user_data or not user_data[user_id]['interests']:
        bot.answer_callback_query(call.id, "❌ Вы не выбрали ни одного интереса!")
        return

    selected = list(user_data[user_id]['interests'])
    age = user_data[user_id].get('age')
    professions = quiz.get_professions_by_interests(selected)
    
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
        if len(prof) == 6:
            prof_id, title, _, _, min_age, max_age = prof
        elif len(prof) == 4:
            prof_id, title, _, _ = prof
            min_age, max_age = 0, 100
        else:
            continue  # или обработайте ошибку

        if age is not None:
            if min_age > 0 and age < min_age:
                title += f" (доступно с {min_age} лет)"
            elif max_age < 100 and age > max_age:
                title += f" (рекомендуется до {max_age} лет)"
        
        markup.add(types.InlineKeyboardButton(
            text=f"👨‍💻 {title}", 
            callback_data=f"prof_{prof_id}"
        ))
        

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🎯 Вот профессии, подходящие под ваши интересы ({', '.join(selected)}):",
        reply_markup=markup
    )
    user_data[user_id]['stage'] = 'start'

@bot.callback_query_handler(func=lambda call: call.data.startswith('prof_'))
def show_profession_detail(call):
    """Показать детали профессии"""
    prof_id = int(call.data.replace('prof_', ''))
    prof = quiz.get_profession_by_id(prof_id)
    if not prof:
        bot.answer_callback_query(call.id, "Профессия не найдена")
        return

    # Универсальная распаковка для разных структур
    if len(prof) == 6:
        prof_id, title, description, education, min_age, max_age = prof
    elif len(prof) == 3:
        prof_id, title, description = prof
        education = "Не указано"
        min_age, max_age = 0, 100
    else:
        bot.answer_callback_query(call.id, "Ошибка данных профессии")
        return

    # Гарантируем, что education — строка
    if not education:
        education = "Не указано"

    # Гарантируем, что min_age и max_age — числа
    try:
        min_age = int(min_age)
    except (TypeError, ValueError):
        min_age = 0
    try:
        max_age = int(max_age)
    except (TypeError, ValueError):
        max_age = 100

    user_age = user_data.get(call.from_user.id, {}).get('age')
    try:
        user_age = int(user_age)
    except (TypeError, ValueError):
        user_age = None

    # Формируем информацию о возрасте
    age_info = ""
    if user_age is not None:
        if min_age > 0 and user_age < min_age:
            age_info = f"\n\n⚠️ <b>Внимание:</b> Эта профессия доступна с {min_age} лет. Вам пока {user_age} лет."
        elif max_age < 100 and user_age > max_age:
            age_info = f"\n\n⚠️ <b>Внимание:</b> Эта профессия рекомендуется до {max_age} лет. Вам уже {user_age} лет."
        elif user_age >= min_age and user_age <= max_age:
            age_info = f"\n\n✅ <b>Возраст:</b> Вам {user_age} лет — подходящий возраст для этой профессии."

    text = (
        f"<b>{title}</b>\n\n"
        f"<i>{description}</i>\n\n"
        f"📚 <b>Образование:</b> {education}"
        f"{age_info}\n\n"
        f"🔹 Выбери другое действие в меню или /start для возврата"
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    """Обработчик текстовых сообщений"""
    user_id = message.from_user.id
    text = message.text.lower()
    interests = quiz.get_interests()

    matched = [i for i in interests if i.lower() in text]

    if matched:
        user_data.setdefault(user_id, {'interests': set(), 'stage': 'start', 'age': None})
        user_data[user_id]['interests'].update(matched)

        professions = quiz.get_professions_by_interests(matched)
        if professions:
            markup = types.InlineKeyboardMarkup()
            for prof in professions:
                prof_id, title, _, _, min_age, max_age = prof
                age = user_data[user_id].get('age')
                if age is not None:
                    if min_age is not None and age < min_age:
                        title += f" (доступно с {min_age} лет)"
                    elif max_age is not None and age > max_age:
                        title += f" (рекомендуется до {max_age} лет)"
                
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
    bot.infinity_polling()