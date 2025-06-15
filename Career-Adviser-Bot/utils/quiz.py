import sqlite3
import random

DB_PATH = 'data/careers.db'

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

def get_interests():
    """Получить список всех интересов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM interests ORDER BY name")
    interests = [row[0] for row in cursor.fetchall()]
    conn.close()
    return interests

def get_professions_by_interests(user_interests):
    """Находит профессии, соответствующие интересам пользователя."""
    if not user_interests:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in user_interests)
    query = f"""
    SELECT DISTINCT p.id, p.title, p.description, p.education, 
       COALESCE(p.min_age, 0), COALESCE(p.max_age, 100)
    FROM professions p
    JOIN profession_interests pi ON p.id = pi.profession_id
    JOIN interests i ON pi.interest_id = i.id
    WHERE i.name IN ({placeholders})
    ORDER BY p.title
    """
    cursor.execute(query, user_interests)
    results = cursor.fetchall()
    conn.close()
    return results

def get_profession_by_id(profession_id):
    """Получает полную информацию о профессии по её идентификатору."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, education, 
               COALESCE(min_age, 0), COALESCE(max_age, 100)
        FROM professions 
        WHERE id=?
    """, (profession_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_career_tip():
    """Получить случайный совет по карьере"""
    return random.choice(CAREER_TIPS)

def create_demo_data():
    """Создать демо-данные"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создание таблиц
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS professions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        education TEXT,
        min_age INTEGER,
        max_age INTEGER
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
    
    # Профессии с возрастными ограничениями
    professions = [
        ('UX-дизайнер', 'Проектирует удобные интерфейсы для пользователей.', 'Курсы, колледжи, университеты', 16, None),
        ('Биоинформатик', 'Работает с биологическими данными и алгоритмами.', 'Биофак, IT-курсы', 18, None),
        ('Веб-разработчик', 'Создает веб-сайты и веб-приложения.', 'Курсы программирования, компьютерные науки', 14, None),
        ('Аналитик данных', 'Анализирует большие объемы данных для принятия решений.', 'Математика, статистика, экономика', 18, None),
        ('Маркетолог', 'Разрабатывает стратегии продвижения товаров и услуг.', 'Маркетинг, бизнес-образование', 18, None),
        ('Графический дизайнер', 'Создает визуальные коммуникации и элементы бренда.', 'Дизайн, искусство', 16, None),
        ('Инженер-робототехник', 'Разрабатывает и программирует роботов.', 'Инженерия, программирование', 18, None),
        ('Психолог', 'Изучает поведение и психические процессы людей.', 'Психология, педагогика', 18, None),
        ('Эколог', 'Исследует проблемы окружающей среды и пути их решения.', 'Биология, экология', 18, None),
        ('Финансовый аналитик', 'Анализирует финансовые данные и рынки.', 'Финансы, экономика', 21, 50),
        ('Копирайтер', 'Создает тексты для рекламы и маркетинга.', 'Журналистика, филология', 16, None),
        ('Менеджер проектов', 'Организует и контролирует выполнение проектов.', 'Бизнес-администрирование', 21, None),
        ('Архитектор', 'Проектирует здания и сооружения.', 'Архитектура, строительство', 18, None),
        ('Врач', 'Диагностирует и лечит заболевания.', 'Медицинское образование', 18, 60),
        ('Юрист', 'Консультирует по правовым вопросам и представляет интересы в суде.', 'Юриспруденция', 18, None)
    ]
    
    # Добавление профессий
    cursor.execute("SELECT COUNT(*) FROM professions")
    if cursor.fetchone()[0] == 0:
        for prof in professions:
            cursor.execute(
                "INSERT INTO professions (title, description, education, min_age, max_age) VALUES (?, ?, ?, ?, ?)",
                prof
            )
    
    # Добавление интересов
    interests = [
        'дизайн', 'психология', 'технологии', 'биология', 'программирование', 
        'анализ данных', 'маркетинг', 'искусство', 'робототехника', 'экология',
        'финансы', 'письмо', 'управление', 'архитектура', 'медицина', 'право',
        'математика', 'статистика', 'экономика', 'коммуникации'
    ]
    
    for interest in interests:
        try:
            cursor.execute("INSERT OR IGNORE INTO interests (name) VALUES (?)", (interest,))
        except sqlite3.IntegrityError:
            pass
    
    # Связи профессий и интересов
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
                cursor.execute(
                    "INSERT OR IGNORE INTO profession_interests (profession_id, interest_id) VALUES (?, ?)",
                    (prof_id, interest_id[0])
                )
    
    conn.commit()
    conn.close()