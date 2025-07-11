
# Career Adviser Bot (telebot version)

Телеграм-бот для помощи в выборе профессии на основе интересов.

## Функционал

- Пройти мини-тест с выбором интересов кнопками
- Показать все интересы
- Рекомендации профессий по интересам с подробным описанием
- Совет дня для развития карьеры
- Помощь по командам
- Обработка текстовых сообщений с автоматическим поиском интересов
- Отмена действий (/cancel)

## План работы над проектом

1. **Подготовка репозитория**
    - Создание структуры проекта
    - Добавление README и requirements.txt

2. **Создание базы данных**
    - Проектирование SQL-схемы (профессии, интересы, связи)
    - Наполнение базы демонстрационными данными

3. **Разработка логики бота**
    - Обработка команд /start, /help, /cancel
    - Реализация мини-теста с кнопками для выбора интересов
    - Рекомендации профессий на основе выбранных интересов

4. **Расширение функционала**
    - Советы дня для пользователя
    - Обработка произвольных текстовых сообщений с распознаванием интересов
    - Детальные описания профессий по кнопкам

5. **Тестирование и отладка**
    - Проверка корректности работы всех функций
    - Улучшение взаимодействия с пользователем

6. **Документация**
    - Описание проекта, инструкции по запуску
    - Пояснения по структуре и базе данных

---

## Установка

1. Склонируй проект
2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Вставь свой токен в `main.py`
4. Запусти бота:

```bash
python main.py
```

---

## Структура проекта

```
career-adviser-bot/
├── main.py
├── requirements.txt
├── README.md
├── data/
│   └── careers.db
└── utils/
    └── quiz.py
```
---

## Как работать с ботом

- Отправь команду `/start`
- Выбери «Пройти мини-тест» или напиши свои интересы
- Нажми на профессию, чтобы узнать детали
- Используй /help и /cancel по необходимости

---
