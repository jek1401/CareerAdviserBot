import sqlite3

DB_PATH = 'data/careers.db'

def get_interests():
    """
    Получает список всех доступных интересов из базы данных.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM interests ORDER BY name")
    interests = [row[0] for row in cursor.fetchall()]
    conn.close()
    return interests

def get_professions_by_interests(user_interests):
    """
    Находит профессии, соответствующие интересам пользователя.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in user_interests)
    query = f"""
    SELECT DISTINCT p.id, p.title, p.description, p.education
    FROM professions p
    JOIN profession_interests pi ON p.id = pi.profession_id
    JOIN interests i ON pi.interest_id = i.id
    WHERE i.name IN ({placeholders})
    """
    cursor.execute(query, user_interests)
    results = cursor.fetchall()
    conn.close()
    return results

def get_profession_by_id(profession_id):
    """
    Получает полную информацию о профессии по её идентификатору.

    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, education FROM professions WHERE id=?", (profession_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def create_demo_data():
    """
    Создает базу данных и заполняет её демонстрационными данными, если она пустая.
    Создает таблицы professions, interests и profession_interests.
    Добавляет тестовые профессии и связанные с ними интересы.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS professions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        education TEXT
    );
    CREATE TABLE IF NOT EXISTS interests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS profession_interests (
        profession_id INTEGER,
        interest_id INTEGER,
        PRIMARY KEY (profession_id, interest_id),
        FOREIGN KEY (profession_id) REFERENCES professions (id),
        FOREIGN KEY (interest_id) REFERENCES interests (id)
    );
    """)
    # Insert professions if table empty
    cursor.execute("SELECT COUNT(*) FROM professions")
    if cursor.fetchone()[0] == 0:
        professions = [
            ('UX-дизайнер', 'Проектирует удобные интерфейсы для пользователей.', 'Курсы, колледжи, университеты'),
            ('Биоинформатик', 'Работает с биологическими данными и алгоритмами.', 'Биофак, IT-курсы'),
            ('Веб-разработчик', 'Создает веб-сайты и веб-приложения.', 'Курсы программирования, компьютерные науки'),
            ('Аналитик данных', 'Анализирует большие объемы данных для принятия решений.', 'Математика, статистика, экономика'),
            ('Маркетолог', 'Разрабатывает стратегии продвижения товаров и услуг.', 'Маркетинг, бизнес-образование'),
            ('Графический дизайнер', 'Создает визуальные коммуникации и элементы бренда.', 'Дизайн, искусство'),
            ('Инженер-робототехник', 'Разрабатывает и программирует роботов.', 'Инженерия, программирование'),
            ('Психолог', 'Изучает поведение и психические процессы людей.', 'Психология, педагогика'),
            ('Эколог', 'Исследует проблемы окружающей среды и пути их решения.', 'Биология, экология'),
            ('Финансовый аналитик', 'Анализирует финансовые данные и рынки.', 'Финансы, экономика'),
            ('Копирайтер', 'Создает тексты для рекламы и маркетинга.', 'Журналистика, филология'),
            ('Менеджер проектов', 'Организует и контролирует выполнение проектов.', 'Бизнес-администрирование'),
            ('Архитектор', 'Проектирует здания и сооружения.', 'Архитектура, строительство'),
            ('Врач', 'Диагностирует и лечит заболевания.', 'Медицинское образование'),
            ('Юрист', 'Консультирует по правовым вопросам и представляет интересы в суде.', 'Юриспруденция')
        ]
        for prof in professions:
            cursor.execute("INSERT INTO professions (title, description, education) VALUES (?, ?, ?)", prof)
    
    # Insert interests if empty
    cursor.execute("SELECT COUNT(*) FROM interests")
    if cursor.fetchone()[0] == 0:
        interests = [
            'дизайн', 'психология', 'технологии', 'биология', 'программирование', 
            'анализ данных', 'маркетинг', 'искусство', 'робототехника', 'экология',
            'финансы', 'письмо', 'управление', 'архитектура', 'медицина', 'право',
            'математика', 'статистика', 'экономика', 'коммуникации'
        ]
        for interest in interests:
            try:
                cursor.execute("INSERT INTO interests (name) VALUES (?)", (interest,))
            except sqlite3.IntegrityError:
                pass
    
    # Link professions and interests
    profession_interests = {
        'UX-дизайнер': ['дизайн', 'психология', 'технологии', 'коммуникации'],
        'Биоинформатик': ['биология', 'программирование', 'анализ данных', 'математика'],
        'Веб-разработчик': ['программирование', 'технологии', 'дизайн'],
        'Аналитик данных': ['анализ данных', 'математика', 'статистика', 'экономика'],
        'Маркетолог': ['маркетинг', 'коммуникации', 'психология', 'письмо'],
        'Графический дизайнер': ['дизайн', 'искусство', 'коммуникации'],
        'Инженер-робототехник': ['робототехника', 'программирование', 'технологии'],
        'Психолог': ['психология', 'коммуникации'],
        'Эколог': ['экология', 'биология'],
        'Финансовый аналитик': ['финансы', 'экономика', 'математика', 'анализ данных'],
        'Копирайтер': ['письмо', 'коммуникации', 'маркетинг'],
        'Менеджер проектов': ['управление', 'коммуникации', 'экономика'],
        'Архитектор': ['архитектура', 'дизайн', 'искусство'],
        'Врач': ['медицина', 'биология'],
        'Юрист': ['право', 'коммуникации']
    }
    
    for profession, interests in profession_interests.items():
        cursor.execute("SELECT id FROM professions WHERE title=?", (profession,))
        prof_id = cursor.fetchone()[0]
        for interest in interests:
            cursor.execute("SELECT id FROM interests WHERE name=?", (interest,))
            interest_id = cursor.fetchone()
            if interest_id:
                cursor.execute("INSERT OR IGNORE INTO profession_interests (profession_id, interest_id) VALUES (?, ?)",
                             (prof_id, interest_id[0]))
    
    conn.commit()
    conn.close()

# Совет дня (простой пример)
CAREER_TIPS = [
    "Регулярно учись новому — курсы и самообразование открывают двери.",
    "Развивай коммуникативные навыки — они важны в любой профессии.",
    "Пробуй разные сферы, чтобы найти, что действительно вдохновляет.",
    "Ставь цели и планируй карьеру на несколько лет вперед.",
    "Не бойся менять профессию, если чувствуешь, что это необходимо.",
    "Создавай портфолио своих работ — это ценится работодателями.",
    "Изучай английский язык — он расширяет профессиональные возможности.",
    "Посещай профессиональные мероприятия для нетворкинга.",
    "Развивай эмоциональный интеллект — это ключ к успеху в команде.",
    "Будь проактивным — предлагай идеи и решения, а не жди указаний."
]

def get_career_tip():
    """
    Возвращает случайный совет по карьерному развитию.
    """
    import random
    return random.choice(CAREER_TIPS)